from django.test import TestCase


def init():
    from accounts.models import Option
    Option.objects.create(option_name="uid", option_value="0")
