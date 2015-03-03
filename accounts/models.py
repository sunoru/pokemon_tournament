from django.db import models
from django.contrib.auth.models import User
import datetime
import random


class PlayerUser(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField("name", max_length=100, default="")
    player_id = models.CharField("Play Pokemon ID", max_length=100, default='test', unique=True)
    birthday = models.DateField("birthday", default=datetime.date.today())

    @classmethod
    def create(cls, **kwargs):
        playeruser = cls.objects.create(**kwargs)
        if playeruser.name == "":
            playeruser.name = playeruser.user.username
        return playeruser

    @classmethod
    def create_test_player(cls, tour, name, pid, **kwargs):
        pwd = "%s" % random.randint(100000, 999999)
        usr = "test_%s_%s" % (tour.tour_id, pid)
        q = 0
        while User.objects.filter(username=usr):
            q += 1
            usr = "test_%s_%s_%s" % (tour.tour_id, pid, q)
        user = User.objects.create_user(usr, "%s@moon.moe" % usr, pwd)
        playeruser = cls.objects.create(user=user, name=name, player_id=usr, **kwargs)
        return playeruser

    @classmethod
    def create_existed_player(cls, player_id, name):
        user = User.objects.create_user(player_id, "%s@moon.moe" % player_id, "%s" % random.randint(100000,999999))
        playeruser = cls.objects.create(
            user=user,
            player_id=player_id,
            name=name
        )
        return playeruser

    def get_age_division(self):
        fy = datetime.date.today().year - 10
        if self.birthday.year >= fy:
            return 1  # for Junior
        fy -= 4
        if self.birthday.year >= fy:
            return 2  # for Senior
        return 3  # for Masters

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.player_id)


class Option(models.Model):
    option_name = models.CharField("key", max_length=50, unique=True)
    option_value = models.TextField("value")

    def __unicode__(self):
        return "%s %s" % (self.option_name, self.option_value)
