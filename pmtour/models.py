from django.contrib.auth.models import User
from django.db import models


class PlayerUser(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField("name", max_length=100)
    player_id = models.CharField("Play Pokemon ID", max_length=100)
    birthday = models.DateField("birthday")


class Tournament(models.Model):
    SWISS = "swiss"
    SINGLE = "single"
    SWISS_PLUS_SINGLE = "swiss_single"
    TYPE_CHOICES = (
        (SWISS, "Swiss"),
        (SINGLE, "Single Elimination"),
        (SWISS_PLUS_SINGLE, "Swiss plus Single Elimination")
    )
    name = models.CharField("name", max_length=100)
    alias = models.CharField("alias", max_length=20)
    tournament_type = models.CharField("type", max_length=100, choices=TYPE_CHOICES)
    start_time = models.DateTimeField("start time")
    description = models.TextField("description")
    status = models.SmallIntegerField("status", default=-1)
    players = models.TextField("participators")
    remarks = models.TextField()  # use for the age separated swiss


class Player(models.Model):
    user = models.ForeignKey(PlayerUser)
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
            return sum([x.get_winning_persentage() for x in self.foes.all()]) / len(self.foes.all())


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
