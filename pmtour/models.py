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

    def players_count(self):
        return self.player_set.count()

    def refresh(self):
        if self.status == -1:
            if (datetime.datetime.now() - timezone.localtime(self.start_time).replace(tzinfo=None)).total_seconds()\
                    >= 0:
                self.status = 0
                self.save()

    def _get_type(self, turn_number):
        if self.tournament_type == Tournament.SWISS or self.tournament_type == Tournament.SINGLE:
            return self.tournament_type
        elif self.tournament_type == Tournament.SWISS_PLUS_SINGLE:
            return Tournament.SWISS if turn_number <= int(self.get_option("turns")) else Tournament.SINGLE
        else:
            raise Tournament.NoTypeError

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
        players = self.player_set.filter(eliminated=False)


    def __unicode__(self):
        return "%s (%s) %s" % (self.name, self.status, self.start_time)


class Player(models.Model):
    user = models.ForeignKey(accounts.models.PlayerUser)
    tournament = models.ForeignKey(Tournament)
    playerid = models.SmallIntegerField(unique=True)
    wins = models.SmallIntegerField(default=0)
    loses = models.SmallIntegerField(default=0)
    ties = models.SmallIntegerField(default=0)
    foes = models.ManyToManyField("self")
    late = models.BooleanField(default=False)
    eliminated = models.BooleanField(default=False)
    exited = models.BooleanField(default=False)
    score = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s (%s/%s/%s (%s))" % (self.user.name, self.wins, self.loses, self.ties, self.score)

    def get_winning_persentage(self):
        re = self.wins + self.loses + self.ties
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


class Turn(models.Model):
    tournament = models.ForeignKey(Tournament)
    turn_number = models.SmallIntegerField("turn number")
    standings = models.TextField("standings")  # the results
    bracket = models.TextField("bracket")
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
            p = {
                "standing": i + 1,
                "name": tmp[i].user.name,
                "match": "%s/%s/%s (%s)" % (tmp[i].wins, tmp[i].loses, tmp[i].ties, tmp[i].score),
                "points": str(tmp[i].score),
                "opswin": "{0:.2%}".format(tmp[i].get_opponents_wp()),
                "opsopswin": "{0:.2%}".format(tmp[i].get_opps_opps_wp()),
            }
            standings.append(p)
        return standings

    # TODO: should be tested
    def gen_standings(self):
        if self.type == Tournament.SINGLE:
            self.standings = json.dumps(None)
            return None
        standings = self._get_standings()
        self.standings = json.dumps(standings)
        return standings


class Log(models.Model):
    player_a = models.ForeignKey(Player, related_name="player_a_log")
    player_b = models.ForeignKey(Player, related_name="player_b_log", null=True)
    status = models.SmallIntegerField("status", default=0)  # 1 for a win, 2 for b win, 3 for tie
    result = models.CharField("result", max_length=20)
    time = models.DateTimeField("time")
    turn = models.ForeignKey(Turn)

    @staticmethod
    def search(a, b):
        try:
            log = a.player_a_log.get(player_b=b)
        except Log.DoesNotExist:
            return None
        return log
