# coding=utf-8
from django.db import models
import json
import random
from pmtour.models import BaseModel, Tournament, Player


class Turn(BaseModel):
    tournament = models.ForeignKey(Tournament)
    turn_number = models.SmallIntegerField("turn number")
    standings = models.TextField("standings")  # the results
    #bracket = models.TextField("bracket")
    type = models.CharField("type", max_length=100)
    status = models.SmallIntegerField("status", default=0)  # count for log checked

    def __unicode__(self):
        return "%s Turn %s: %s (%s)" % (self.tournament.name, self.turn_number, self.type, self.status)

    @staticmethod
    def _compare2(a, b):
        p = Turn._compare(a, b)
        if p == 0:
            alist = a.foes.all()
            blist = b.foes.all()
            i = len(alist) - 1
            q = Turn._compare(alist[i], blist[i])
            while q == 0 and i > 0:
                i -= 1
                q = Turn._compare(alist[i], blist[i])
            return q
        return p

    @staticmethod
    def _compare(a, b):
        from pmtour.models import Log
        if a.late and not b.late:
            return -1
        if not a.late and b.late:
            return 1
        if a.score > b.score:
            return 1
        if a.score < b.score:
            return -1
        ta = a.opponents_wp
        tb = b.opponents_wp
        if ta > tb:
            return 1
        if ta < tb:
            return -1
        ta = a.opps_opps_wp
        tb = b.opps_opps_wp
        if ta > tb:
            return 1
        if ta < tb:
            return -1
        ta = Log.search(a, b)
        if ta is not None:
            if ta.status == 1:
                return 1
            elif ta.status == 2:
                return -1
        else:
            ta = Log.search(b, a)
            if ta is not None:
                if ta.status == 1:
                    return -1
                elif ta.status == 2:
                    return 1
        return 0

    @classmethod
    def create_from_data(cls, tour, data):
        if "standings" not in data or not data["standings"]:
            data["standings"] = ""
        try:
            turn = cls.objects.create(
                tournament=tour,
                turn_number=data["turn_number"],
                standings=data["standings"],
                type=data["type"],
                status=-1
            )
        except Exception:  # 不知道怎样写才优雅
            raise cls.LoaddataError
        return turn

    @classmethod
    def dumpdata(cls, tour):
        from pmtour.models import Log
        turns = []
        for turn in tour.turn_set.all():
            aturn = {
                "turn_number": turn.turn_number,
                "standings": turn.standings,
                "type": turn.type,
                "logs": Log.dumpdata(turn)
            }
            turns.append(aturn)
        return turns

    @classmethod
    def loaddata(cls, tour, turns_data):
        def cancel_load(data):
            for p in data:
                p[0].delete()
        from pmtour.models import Log
        turns = []
        for turn_data in turns_data:
            try:
                turn = cls.create_from_data(tour, turn_data)
            except cls.LoaddataError:
                cancel_load(turns)
                return "Error creating turn."
            turns.append((turn, turn_data["logs"]))
        for turn, logs_data in turns:
            mg = Log.loaddata(turn, logs_data)
            if mg:
                cancel_load(turns)
                return mg
            turn.save()
        return ""

    def _get_standings(self, on_swiss_over=False):
        #TODO:test
        tmp = [x for x in self.tournament.player_set.all()]
        if on_swiss_over:
            tmp.sort(Turn._compare2, reverse=True)
        else:
            tmp.sort(Turn._compare, reverse=True)
        standings = []
        for i in xrange(len(tmp)):
            tmp[i].standing = i + 1
            tmp[i].save()
            standings.append(tmp[i].gen_standing_dict())
        return standings

    def get_standing(self):
        if self.standings == "":
            return None
        else:
            return json.loads(self.standings)

    def check_all(self):
        rq = []
        for log in self.log_set.all():
            if log.status == 0:
                rq.append(str(log))
        return rq

    def start(self):
        self.gen_bracket()
        self.status = 1

    def end(self):
        if self.type != Tournament.SINGLE:
            self.gen_standings()
        else:
            self.standings = ""
        if self.tournament.tournament_type == Tournament.SWISS_PLUS_SINGLE and\
                self.turn_number == self.tournament.get_option("turns"):
            lp = self.tournament.get_option("elims")
            sts = self.get_standing()
            for i in xrange(lp, len(sts)):
                player = self.tournament.player_set.get(playerid=sts[i]["pid"])
                player.eliminate()
                player.save()
        self.status = -1

    def gen_standings(self):
        standings = self._get_standings(self.tournament.on_swiss_over(self.turn_number))
        self.standings = json.dumps(standings)

    def gen_last_standings(self):
        # 暂时写得太不优雅了……
        if self.tournament.tournament_type == Tournament.SWISS_PLUS_SINGLE:
            s_turn = self.tournament.get_option("turns")
            s_elim = self.tournament.get_option("elims")
            standings = self.tournament.turn_set.get(turn_number=s_turn).get_standing()[s_elim:]
            for i in xrange(s_turn+1, self.turn_number):
                the_turn = self.tournament.turn_set.get(turn_number=i)
                tmp_standings = [x.get_loser() for x in the_turn.log_set.all()]
                tmp_standings.sort(Turn._compare2)
                for tp in tmp_standings:
                    tp.standing = s_elim
                    s_elim -= 1
                    tp.save()
                    standings.insert(0, tp.gen_standing_dict())
            assert s_elim == 2
            alog = self.log_set.all()[0]
            a = alog.get_loser()
            a.standing = 2
            a.save()
            standings.insert(0, a.gen_standing_dict())
            a = alog.get_winner()
            a.standing = 1
            a.save()
            standings.insert(0, a.gen_standing_dict())
            self.standings = json.dumps(standings)

    def gen_bracket(self):
        from pmtour.models import Log
        if self.type == Tournament.SINGLE:
            if self.tournament.tournament_type == Tournament.SINGLE:
                players = Player.get_sorted_by_playerid(self.tournament)
                Log.create_from_players(self, players)
            elif self.tournament.tournament_type == Tournament.SWISS_PLUS_SINGLE:
                players = Player.get_sorted_for_elims(self.tournament)
                Log.create_from_players(self, players)
        elif self.type == Tournament.SWISS:
            if self.turn_number == 1:
                players = Player.get_sorted_by_playerid(self.tournament)
                random.shuffle(players)
                Log.create_from_players(self, players)
            else:
                players = Player.get_sorted_by_standing(self.tournament)
                player_pairs = Turn.swissshuffle(players)
                Log.create_from_player_pairs(self, 1, player_pairs)
        else:
            raise Tournament.NoTypeError("Unknown type.")

    @staticmethod
    def swissshuffle(players):
        tmp = []
        p1 = -1
        p2 = None
        for i in xrange(len(players)):
            if players[i].score == p1:
                p2.append(players[i])
            else:
                p1 = players[i].score
                p2 = [players[i]]
                tmp.append(p2)
        for i in xrange(len(tmp)):
            random.shuffle(tmp[i])
            k = -1
            for j in xrange(len(tmp[i])):
                if tmp[i][j].byes > 0:
                    k += 1
                    t = tmp[i][k]
                    tmp[i][k] = tmp[i][j]
                    tmp[i][j] = t
        tmp2 = []
        for p in tmp:
            tmp2 += p
        player_pairs = []
        while len(tmp2) > 0:
            j = 1
            ok = False
            while j < len(tmp2):
                if not tmp2[0].has_meeted(tmp2[j]):
                    player_pairs.append((tmp2[0], tmp2[j]))
                    tmp2.remove(tmp2[j])
                    tmp2.remove(tmp2[0])
                    ok = True
                    break
                j += 1
            if not ok:
                player_pairs.append((tmp2[0], None))
                tmp2.remove(tmp2[0])
        s = sum([1 for x in player_pairs if x[1] is None])
        if s > 1:
            player_pairs = Turn.swissshuffle(players)

        #random.shuffle(player_pairs)
        return player_pairs
