# coding=utf-8
from django.db import models
from accounts.models.bases import BaseModel


class Option(BaseModel):
    option_name = models.CharField("key", max_length=50, unique=True)
    option_value = models.TextField("value")

    def __unicode__(self):
        return "%s %s" % (self.option_name, self.option_value)
