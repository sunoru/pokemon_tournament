# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json
import random


class BaseModel(models.Model):

    class Meta:
        abstract = True
        app_label = "accounts"


class PlayerUser(BaseModel):
    user = models.OneToOneField(User)
    name = models.CharField("name", max_length=100, default="")
    player_id = models.CharField("Play Pokemon ID", max_length=100, default='test', unique=True)
    birthday = models.DateField("birthday", auto_now_add=True)
    information = models.TextField("information", default="{}", null=True)
    _tmp_info = None

    class Meta:
        app_label = 'accounts'

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

    def __init__(self, *arg, **kwargs):
        super(PlayerUser, self).__init__(*arg, **kwargs)
        if not self.information:
            self.information = "{}"
        self._tmp_info = json.loads(self.information)

    def get_age_division(self):
        fy = timezone.now().year - 10
        if self.birthday.year >= fy:
            return 1  # for Junior
        fy -= 4
        if self.birthday.year >= fy:
            return 2  # for Senior
        return 3  # for Masters

    def get_info(self, key):
        if key in self._tmp_info:
            return self._tmp_info[key]
        return None

    def set_info(self, key, value):
        self._tmp_info[key] = value

<<<<<<< HEAD:accounts/models.py
class Option(BaseModel):
    option_name = models.CharField("key", max_length=50, unique=True)
    option_value = models.TextField("value")
=======
    def save(self, **kwargs):
        self.information = json.dumps(self._tmp_info)
        super(PlayerUser, self).save(**kwargs)
>>>>>>> d37bdc3027f0568946172fcab403b2fc4997432f:accounts/models/playeruser.py

    class Meta:
        app_label = 'accounts'

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.player_id)