# coding=utf-8
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
import json
import random
import logging
from accounts.models.bases import BaseModel


class PlayerUser(BaseModel):
    user = models.OneToOneField(User)
    name = models.CharField("name", max_length=100, default="")
    player_id = models.CharField("Play Pokemon ID", max_length=100, default='test', unique=True)
    birthday = models.DateField("birthday", auto_now_add=True)
    information = models.TextField("information", default="{}", null=True)

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
        user = User.objects.create_user(usr, "%s@%s" % (usr, settings.EMAIL_SUFFIX), pwd)
        playeruser = cls.objects.create(user=user, name=name, player_id=usr, **kwargs)
        return playeruser

    @classmethod
    def create_existed_player(cls, player_id, name):
        pwd = "%s" % random.randint(100000, 999999)
        logging.warn("%s %s" % (player_id, pwd))
        user = User.objects.create_user(player_id, "%s@%s" % (player_id, settings.EMAIL_SUFFIX), pwd)
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

    def __str__(self):
        return "%s %s" % (self.player_id, self.name)

    def get_age_division(self):
        fy = timezone.now().year - 10
        if self.birthday.year >= fy:
            return 1  # for Junior
        fy -= 4
        if self.birthday.year >= fy:
            return 2  # for Senior
        return 3  # for Masters

    def get_info(self, key):
        _tmp_info = json.loads(self.information)
        if key in _tmp_info:
            return _tmp_info[key]
        return None

    def set_info(self, key, value):
        _tmp_info = json.loads(self.information)
        _tmp_info[key] = value
        self.information = json.dumps(_tmp_info)
