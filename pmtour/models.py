# coding=utf-8
from django.db import models
import accounts.models
import datetime
import json
import random
from django.utils import timezone


class Tournament(models.Model):
    SWISS = "swiss"
    SINGLE = "single"
    SWISS_PLUS_SINGLE = "swiss_single"
    TYPE_CHOICES = (
        (SWISS, "Swiss"),
        (SINGLE, "Single Elimination"),
        (SWISS_PLUS_SINGLE, "Swiss plus Single Elimination")
    )
    name = models.CharField("name", max_length=100, default='a tournament')
    tour_id = models.CharField("tour_id", max_length=20, unique=True)
    alias = models.CharField("alias", max_length=20, unique=True)
    tournament_type = models.CharField("type", max_length=100, choices=TYPE_CHOICES)
    start_time = models.DateTimeField("start time", default=datetime.datetime(2014, 10, 6, 13, 0))
    description = models.TextField("description", default="")
    status = models.SmallIntegerField("status", default=-2)
    admins = models.ManyToManyField(accounts.models.PlayerUser)
    remarks = models.TextField(default="{}")  # use for the age separated swiss, swiss plus turns, etc
    # the format for each turn

    class NoTypeError(Exception):
        pass

    class InvalidAliasError(Exception):
        pass

    class TourOverError(Exception):
        pass

    @classmethod
    def alias_unique(cls, alias):
        return cls.objects.filter(alias=alias).count() == 0

    @classmethod
    def create(cls, admin, **kwargs):
        uid = accounts.models.Option.objects.get(option_name="uid")
        uid.option_value = str(int(uid.option_value) + 1)
        kwargs["tour_id"] = str(100000 + int(uid.option_value))
        uid.save()
        if "alias" not in kwargs:
            kwargs["alias"] = kwargs["tour_id"]
        else:
            if Tournament.is_unique(kwargs["alias"]):
                raise Tournament.InvalidAliasError
        tour = cls.objects.create(**kwargs)
        tour.admins.add(admin)
        return tour

    def set_option(self, option_name, option_value=None):
        pst = json.loads(self.remarks)
        pst[option_name] = option_value
        self.remarks = json.dumps(pst)

    def get_option(self, option_name):
        pst = json.loads(self.remarks)
        return pst.get(option_name, None)

    def get_current_turn(self):
        if self.is_over():
            return self.turn_set.last()
        else:
            print self.turn_set.all()
            return self.turn_set.get(turn_number=self.status)

    def get_last_turn(self):
        try:
            if self.is_over():
                return self.turn_set.last()
            return self.turn_set.get(turn_number=self.status - 1)
        except Turn.DoesNotExist:
            return None

    def players_count(self):
        return self.player_set.count()

    def refresh(self):
        if self.status == -1 and (
            datetime.datetime.now() - timezone.localtime(self.start_time).replace(tzinfo=None)
        ).total_seconds() >= 0:
            self.status = 0
            self.save()

    def _get_type(self, turn_number):
        if self.tournament_type == Tournament.SWISS or self.tournament_type == Tournament.SINGLE:
            return self.tournament_type
        elif self.tournament_type == Tournament.SWISS_PLUS_SINGLE:
            return Tournament.SWISS if turn_number <= int(self.get_option("turns")) else Tournament.SINGLE
        else:
            raise Tournament.NoTypeError

    def ready(self):
        self.status = -1

    def begin(self):
        t = timezone.now()
        self.start_time = t.strftime("%Y-%m-%dT%H:%M:%S%z")
        self.status = 0

    def _should_end(self):
        print self.player_set.filter(eliminated=False).all()
        if self.tournament_type == Tournament.SWISS:
            return self.status >= int(self.get_option("turns"))
        return self.player_set.filter(eliminated=False).count() == 1

    def start(self, turn_number):
        print turn_number
        if self._should_end():
            self.stop()
            return
        self.status = turn_number
        turn = Turn.objects.create(
            tournament=self,
            turn_number=turn_number,
            standings="",
            type=self._get_type(turn_number),
            status=0
        )
        turn.start()
        turn.save()

    def end(self):
        turn = self.get_current_turn()
        turn.end()
        turn.save()

    def get_current_champion(self):
        if self.tournament_type == Tournament.SWISS:
            turn = self.get_last_turn()
            return self.player_set.get(playerid=turn.get_standing()[0]["pid"])
        try:
            return self.player_set.get(eliminated=False)
        except Player.MultipleObjectsReturned:
            return None

    def on_swiss_over(self, turn_number=None):
        if turn_number is None:
            turn_number = self.status
        return self.tournament_type == Tournament.SWISS_PLUS_SINGLE and int(self.get_option("turns")) == turn_number

    def stop(self):
        self.status = -3
        self.set_option("champion", self.get_current_champion().playerid)

    def is_over(self):
        return self.status == -3

    def __unicode__(self):
        return "%s (%s) %s" % (self.name, self.status, self.start_time)


class Player(models.Model):
    user = models.ForeignKey(accounts.models.PlayerUser)
    tournament = models.ForeignKey(Tournament)
    playerid = models.SmallIntegerField()
    wins = models.SmallIntegerField(default=0)
    loses = models.SmallIntegerField(default=0)
    ties = models.SmallIntegerField(default=0)
    byes = models.SmallIntegerField(default=0)
    foes = models.ManyToManyField("self")
    standing = models.SmallIntegerField(default=0)
    late = models.BooleanField(default=False)
    eliminated = models.BooleanField(default=False)
    exited = models.BooleanField(default=False)
    score = models.IntegerField(default=0)

    @classmethod
    def create(cls, **kwargs):
        player = cls.objects.create(**kwargs)
        if player.late:
            player.loses += player.tournament.status
            player.save()
        return player

    def __unicode__(self):
        return "%s (%s) %s" % (self.user.name, self.get_printable(), self.score)

    def get_printable(self):
        return "%s/%s/%s" % (self.wins + self.byes, self.loses, self.ties)

    def get_winning_persentage(self):
        re = self.wins + self.loses + self.ties + self.byes
        if re == 0:
            return 0.0
        re = float(self.wins) / re
        if re < 0.25:
            re = 0.25
        if self.exited and re > 0.75:
            re = 0.75
        return re

    def get_opponents_wp(self):
        if len(self.foes.all()) == 0:
            return 0.0
        else:
            return sum([x.get_winning_persentage() for x in self.foes.all()]) / self.foes.count()

    def get_opps_opps_wp(self):
        if len(self.foes.all()) == 0:
            return 0.0
        else:
            return sum([x.get_opponents_wp() for x in self.foes.all()]) / self.foes.count()

    def set_log(self, status, foe=None, scored=True):
        if status == 4:
            if scored:
                self.score += 3
            self.byes += 1
        elif status == 3:
            if scored:
                self.score += 1
            self.ties += 1
        elif status == 2:
            self.loses += 1
        elif status == 1:
            if scored:
                self.score += 3
            self.wins += 1
        if foe is not None:
            self.foes.add(foe)

    def delete_log(self, status, foe=None):
        if status == 4:
            self.score -= 3
            self.byes -= 1
        elif status == 3:
            self.score -= 1
            self.ties -= 1
        elif status == 2:
            self.loses -= 1
        elif status == 1:
            self.score -= 3
            self.wins -= 1
        if foe is not None:
            self.foes.remove(foe)

    def exit(self):
        self.exited = True

    def eliminate(self):
        self.eliminated = True

    def has_meeted(self, another):
        return another in self.foes.all()

    @staticmethod
    def _by_playerid(a, b):
        if a.playerid > b.playerid:
            return 1
        return -1

    @staticmethod
    def _by_standing(a, b):
        if a.standing > b.standing:
            return 1
        else:
            return -1

    @classmethod
    def _get_sorted(cls, tour, compare, **kwargs):
        players = tour.player_set.filter(**kwargs)
        players = [x for x in players]
        players.sort(cmp=compare)
        return players

    @classmethod
    def get_sorted_by_playerid(cls, tour):
        return cls._get_sorted(tour, cls._by_playerid, exited=False, eliminated=False)

    @classmethod
    def get_sorted_by_standing(cls, tour):
        return cls._get_sorted(tour, cls._by_standing, exited=False, eliminated=False)

    @classmethod
    def get_sorted_for_elims(cls, tour):
        players = cls._get_sorted(tour, cls._by_standing)
        elims = int(tour.get_option("elims"))
        if elims == 8:
            q = [1, 8, 4, 5, 3, 6, 2, 7]
        elif elims == 4:
            q = [1, 4, 2, 3]
        elif elims == 2:
            q = [1, 2]
        else:
            raise Tournament.NoTypeError("the number of players is wrong")
        players = [players[i - 1] for i in q if not players[i - 1].eliminated]
        return players


class Turn(models.Model):
    tournament = models.ForeignKey(Tournament)
    turn_number = models.SmallIntegerField("turn number")
    standings = models.TextField("standings")  # the results
    #bracket = models.TextField("bracket")
    type = models.CharField("type", max_length=100)
    status = models.SmallIntegerField("status", default=0)  # count for log checked

    def __unicode__(self):
        return "Turn %s: %s (%s)" % (self.turn_number, self.type, self.status)

    @staticmethod
    def _compare2(a, b):
        p = Turn._compare(a, b)
        if p == 0:
            return Turn.compare2(a.foes.last(), b.foes.last())
        return p

    @staticmethod
    def _compare(a, b):
        if a.late and not b.late:
            return -1
        if not a.late and b.late:
            return 1
        if a.score > b.score:
            return 1
        if a.score < b.score:
            return -1
        ta = a.get_opponents_wp()
        tb = b.get_opponents_wp()
        if ta > tb:
            return 1
        if ta < tb:
            return -1
        ta = a.get_opps_opps_wp()
        tb = b.get_opps_opps_wp()
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

#TODO:test
    def _get_standings(self, on_swiss_over=False):
        tmp = [x for x in self.tournament.player_set.all()]
        print tmp
        if on_swiss_over:
            tmp.sort(Turn._compare2, reverse=True)
        else:
            tmp.sort(Turn._compare, reverse=True)
        standings = []
        for i in xrange(len(tmp)):
            tmp[i].standing = i + 1
            tmp[i].save()
            p = {
                "standing": i + 1,
                "pid": tmp[i].playerid,
                "match": tmp[i].get_printable(),
                "score": tmp[i].score,
                "opswin": "{0:.2%}".format(tmp[i].get_opponents_wp()),
                "opsopswin": "{0:.2%}".format(tmp[i].get_opps_opps_wp()),
            }
            standings.append(p)
        print standings
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
        self.gen_standings()
        if self.tournament.tournament_type == Tournament.SWISS_PLUS_SINGLE and\
                self.turn_number == int(self.tournament.get_option("turns")):
            lp = int(self.tournament.get_option("elims"))
            sts = self.get_standing()
            for i in xrange(lp, len(sts)):
                player = self.tournament.player_set.get(playerid=sts[i]["pid"])
                player.eliminate()
                player.save()
        self.status = -1

    def gen_standings(self):
        if self.type == Tournament.SINGLE:
            self.standings = json.dumps(None)
            return None
        standings = self._get_standings(self.tournament.on_swiss_over(self.turn_number))
        self.standings = json.dumps(standings)

    def gen_bracket(self):
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
                print players
                Log.create_from_players(self, players)
            else:
                players = Player.get_sorted_by_standing(self.tournament)
                player_pairs = Turn.swissshuffle(players)
                Log.create_from_player_pairs(self, player_pairs)
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
                print tmp2[j]
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
        random.shuffle(player_pairs)
        return player_pairs


class Log(models.Model):
    player_a = models.ForeignKey(Player, related_name="player_a_log")
    player_b = models.ForeignKey(Player, related_name="player_b_log", null=True)
    status = models.SmallIntegerField("status", default=0)  # 1 for a win, 2 for b win, 3 for tie, 4 for bye
    time = models.DateTimeField("time", null=True)
    turn = models.ForeignKey(Turn)

    _STATUS_DICT = {
        1: 2,
        2: 1,
        3: 3
    }
    def check(self, status):
        if self.status != 0:
            self.delete_status()
        self.status = status
        t = timezone.now()
        self.time = t.strftime("%Y-%m-%dT%H:%M:%S%z")
        if self.turn.type == Tournament.SWISS:
            self.player_a.set_log(status, self.player_b)
            self.player_a.save()
            if self.player_b is not None:
                self.player_b.set_log(Log._STATUS_DICT[status])
                self.player_b.save()
        elif self.turn.type == Tournament.SINGLE:
            self.player_a.set_log(status, self.player_b, False)
            if status == 1:
                self.player_b.eliminated = True
                self.player_b.set_log(2, scored=False)
            elif status == 2:
                self.player_a.eliminated = True
                self.player_b.set_log(1, scored=False)
            elif status == 3:
                # impossible
                self.player_b.set_log(3, scored=False)
            self.player_a.save()
            self.player_b.save()

    def delete_status(self):
        if self.status == 0 or self.status == 4:
            return
        self.player_a.delete_log(self.status, self.player_b)
        self.player_a.save()
        if self.player_b is not None:
            self.player_b.delete_log(Log._STATUS_DICT[self.status])
            self.player_b.save()
        self.status = 0

    def __unicode__(self):
        if self.status == 0:
            return "%s vs. %s" % (self.player_a, self.player_b)
        if self.status == 1:
            return "%s won against %s" % (self.player_a, self.player_b)
        if self.status == 2:
            return "%s won against %s" % (self.player_b, self.player_a)
        if self.status == 3:
            return "%s and %s tied" % (self.player_a, self.player_b)
        if self.status == 4:
            return "%s byed" % self.player_a

    @staticmethod
    def search(a, b):
        try:
            log = a.player_a_log.get(player_b=b)
        except Log.DoesNotExist:
            return None
        return log

    @classmethod
    def create_from_player(cls, turn, p1, p2):
        cls.objects.create(
            player_a=p1,
            player_b=p2,
            turn=turn
        )

    @classmethod
    def create_bye(cls, turn, p1):
        log = cls.objects.create(
            player_a=p1,
            player_b=None,
            turn=turn
        )
        log.check(4)
        log.save()

    @classmethod
    def create_from_player_pairs(cls, turn, player_pairs):
        for pair in player_pairs:
            p1 = pair[0]
            p2 = pair[1]
            if p2 is None:
                cls.create_bye(turn, p1)
            else:
                cls.create_from_player(turn, p1, p2)

    @classmethod
    def create_from_players(cls, turn, players):
        for i in xrange(0, len(players) / 2):
            p1 = players[i * 2]
            p2 = players[i * 2 + 1]
            cls.create_from_player(turn, p1, p2)

        if len(players) & 1 == 1:
            p1 = players[-1]
            cls.create_bye(turn, p1)
