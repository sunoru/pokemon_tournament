from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import PlayerUser, Option
import random


def add_test_users(n, m=0):
    for i in xrange(m, n):
        pwd = "%s" % random.randint(100000, 999999)
        usr = "%s_test%s" % (datetime.date.today().strftime("%y%m%d"), i + 1)
        user = User.objects.create_user(usr, "%s@moon.moe" % usr, pwd)
        playeruser = PlayerUser.objects.create(user=user, name=user.username, player_id=user.username)
        print "add new user: %s %s" % (usr, pwd)


def init():
    Option.objects.create(option_name="uid", option_value="-1")
    playeruser = PlayerUser.objects.create(user=User.objects.all()[0], name="admin", player_id="root")
    import getpass
    usr = raw_input("Username: ")
    email = raw_input("Email(default: %s@moon.moe): " % usr)
    if email == "":
        email = "%s@moon.moe" % usr
    pas = getpass.getpass()
    newuser = User.objects.create_superuser(usr, email, pas)
    print "add new superuser: %s" % newuser
    num = input("the number of test players: ")
    add_test_users(num)


