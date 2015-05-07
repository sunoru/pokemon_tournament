# coding=utf-8
from django.db import models


class Option(models.Model):
    option_name = models.CharField("key", max_length=50, unique=True)
    option_value = models.TextField("value")

    class Meta:
        app_label = 'accounts'

    def __unicode__(self):
        return "%s %s" % (self.option_name, self.option_value)
