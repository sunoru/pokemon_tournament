from django.db import models
from django.contrib.auth.models import User
import datetime


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
