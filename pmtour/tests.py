from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import PlayerUser
import random

def add_test_users(n):
    for i in xrange(n):
        pwd = "%s" % random.randint(100000, 999999)
        user = User.objects.create(username="test%s" % (i + 1), password=pwd)
        playeruser = PlayerUser.objects.create(user=user, name=user.username, player_id=user.username)
        print playeruser

