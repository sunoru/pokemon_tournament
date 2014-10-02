from django.db import models
import accounts.models
import datetime

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
    start_time = models.DateTimeField("start time")
    description = models.TextField("description", null=True)
    status = models.SmallIntegerField("status", default=-2)
    players_count = models.SmallIntegerField("number of players", default=0)
    players = models.TextField("participants", null=True)
    admins = models.ManyToManyField(accounts.models.PlayerUser)
    remarks = models.TextField(null=True)  # use for the age separated swiss, swiss plus turns, etc
    # the format for each turn

    @classmethod
    def create(cls, admin, **kwargs):
        if "start_time" not in kwargs:
            kwargs["start_time"] = datetime.datetime.now()
        uid = accounts.models.Option.objects.get(option_name="uid")
        uid.option_value = str(int(uid.option_value) + 1)
        kwargs["tour_id"] = str(100000 + int(uid.option_value))
        uid.save()
        if "alias" not in kwargs:
            kwargs["alias"] =  kwargs["tour_id"]
        else:
            if cls.objects.filter(alias=kwargs["alias"]).count() != 0:
                return None
            #TODO
        tour = cls.objects.create(**kwargs)
        tour.admins.add(admin)
        return tour

    def __unicode__(self):
        return "%s (%s) %s" % (self.name, self.status, self.start_time)


class Player(models.Model):
    user = models.ForeignKey(accounts.models.PlayerUser)
    tournament = models.ForeignKey(Tournament)
    wins = models.SmallIntegerField(default=0)
    loses = models.SmallIntegerField(default=0)
    ties = models.SmallIntegerField(default=0)
    foes = models.ManyToManyField("self")
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
    standings = models.TextField("standings")  # the results
    bracket = models.TextField("bracket")
    status = models.SmallIntegerField("status")  # count for log checked


class Log(models.Model):
    player_a = models.ForeignKey(Player, related_name="player_a_log")
    player_b = models.ForeignKey(Player, related_name="player_b_log", null=True)
    status = models.BooleanField("status")
    result = models.CharField("result", max_length=20)
    time = models.DateTimeField("time")
    turn = models.ForeignKey(Turn)
