# coding=utf-8
from django.db import models
from accounts.models.bases import BaseModel


class Option(BaseModel):
    option_name = models.CharField("key", max_length=50, unique=True)
    option_value = models.TextField("value", default="")

    def __unicode__(self):
        return "%s %s" % (self.option_name, self.option_value)

    @classmethod
    def create(cls, name, value):
        return cls.objects.create(option_name=name, option_value=value)

    @classmethod
    def get(cls, name):
        return cls.objects.get_or_create(option_name=name)

