# coding=utf-8
from django.db import models
import accounts.models
import datetime
import json
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
    start_time = models.DateTimeField("start time", default=datetime.datetime(2014, 10, 6,13, 0))
    description = models.TextField("description", default="")
    status = models.SmallIntegerField("status", default=-2)
    admins = models.ManyToManyField(accounts.models.PlayerUser)
    remarks = models.TextField(default="{}")  # use for the age separated swiss, swiss plus turns, etc
    # the format for each turn

    class NoTypeError(Exception):
        pass

    @classmethod
    def alias_unique(cls, alias):
        return cls.objects.filter(alias=alias).count() == 0

    @classmethod
    def create(cls, admin, **kwargs):
        #if "start_time" not in kwargs:
        #    kwargs["start_time"] = datetime.datetime.now()
        uid = accounts.models.Option.objects.get(option_name="uid")
        uid.option_value = str(int(uid.option_value) + 1)
        kwargs["tour_id"] = str(100000 + int(uid.option_value))
        uid.save()
        if "alias" not in kwargs:
            kwargs["alias"] =  kwargs["tour_id"]
        else:
            if Tournament.is_unique(kwargs["alias"]):
                raise Exception
            #TODO
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
        if self.status == -1 and (datetime.datetime.now() -
                timezone.localtime(self.start_time).replace(tzinfo=None)).total_seconds() >= 0:
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

    def start(self, turn_number):
        self.status = turn_number
        turn = Turn.objects.create(
            tournament=self,
            turn_number=turn_number,
            standings="",
            bracket="",
            type=self._get_type(turn_number),
            status=0
        )
        turn.gen_bracket()

    def end(self):
        turn = self.get_current_turn()
        turn.gen_standings()
        turn.save()

    def stop(self):
        self.status = -3

    def is_over(self):
        return self.status == -3

    def __unicode__(self):
        return "%s (%s) %s" % (self.name, self.status, self.start_time)


class Player(models.Model):
    user = models.ForeignKey(accounts.models.PlayerUser)
    tournament = models.ForeignKey(Tournament)
    playerid = models.SmallIntegerField(unique=True)
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

    def set_log(self, status, foe=None):
        if status == 4:
            self.score += 3
            self.byes += 1
        elif status == 3:
            self.score += 1
            self.ties += 1
        elif status == 2:
            self.loses += 1
        elif status == 1:
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
    def _get_sorted(cls, tour, key, **kwargs):
        players = tour.player_set.filter(**kwargs)
        players = [x for x in players]
        players.sort(key=key)
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
    status = models.SmallIntegerField("status")  # count for log checked

    @staticmethod
    def _compare(a, b):
        if a.late and not b.late:
            return False
        if not a.late and b.late:
            return True
        if a.score > b.score:
            return True
        if a.score < b.score:
            return False
        ta = a.get_opponents_wp()
        tb = b.get_opponents_wp()
        if ta > tb:
            return True
        if ta < tb:
            return False
        ta = a.get_opps_opps_wp()
        tb = b.get_opps_opps_wp()
        if ta > tb:
            return True
        if ta < tb:
            return False
        ta = Log.search(a, b)
        if ta is not None:
            if ta.status == 1:
                return True
            elif ta.status == 2:
                return False
        else:
            ta = Log.search(b, a)
            if ta is not None:
                if ta.status == 1:
                    return False
                elif ta.status == 2:
                    return True
        return Turn._compare(a.foes.last(), b.foes.last())

    def _get_standings(self):
        tmp = [x for x in self.tournament.player_set.all()]
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
        return True

    # TODO: should be tested
    def gen_standings(self):
        if self.type == Tournament.SINGLE:
            self.standings = json.dumps(None)
            return None
        standings = self._get_standings()
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
                Log.create_from_players(self, players)
            else:
                players = Player.get_sorted_by_standing(self.tournament)
                # TODO: do it later
        else:
            raise Tournament.NoTypeError("Unknown type.")


class Log(models.Model):
    player_a = models.ForeignKey(Player, related_name="player_a_log")
    player_b = models.ForeignKey(Player, related_name="player_b_log", null=True)
    status = models.SmallIntegerField("status", default=0)  # 1 for a win, 2 for b win, 3 for tie, 4 for bye
    time = models.DateTimeField("time")
    turn = models.ForeignKey(Turn)

    def check(self, status):
        self.status = status
        self.time = timezone.now()
        self.player_a.set_log(status, self.player_b)
        self.player_a.save()
        if self.player_b is not None:
            self.player_b.set_log(status)
            self.player_b.save()

    def delete_status(self):
        self.player_a.delete_log(self.status, self.player_b)
        self.player_a.save()
        if self.player_b is not None:
            self.player_b.delete_log(self.status)
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

    @classmethod
    def create_from_players(cls, turn, players):
        for i in xrange(1, len(players) / 2 + 1):
            p1 = players[i * 2 - 1]
            p2 = players[i * 2]
            if p1.exited:
                if not p2.exited:
                    cls.create_bye(turn, p2)
            else:
                if p2.exted:
                    cls.create_bye(turn, p1)
                else:
                    cls.create_from_player(turn, p1, p2)

        if len(players) & 1 == 1:
            p1 = players[-1]
            cls.create_bye(turn, p1)
