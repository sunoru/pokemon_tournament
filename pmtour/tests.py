from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import PlayerUser, Option
import random


def add_test_users(n):
    for i in xrange(n):
        pwd = "%s" % random.randint(100000, 999999)
        user = User.objects.create(username="test%s" % (i + 1), password=pwd)
        playeruser = PlayerUser.objects.create(user=user, name=user.username, player_id=user.username)
        print playeruser


def init():
    Option.objects.create(option_name="uid", option_value="-1")
    playeruser = PlayerUser.objects.create(user=User.objects.all()[0], name="admin", player_id="root")
    print playeruser
