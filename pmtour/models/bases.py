# coding=utf-8
from django.db import models


class BaseModel(models.Model):

    class Meta:
        abstract = True
        app_label = "pmtour"

    class LoaddataError(Exception):
        pass

LOG_STATUS_UNKNOWN = 0
LOG_STATUS_A_WIN = 1
LOG_STATUS_B_WIN = 2
LOG_STATUS_TIE = 3
LOG_STATUS_BYE = 4
LOG_STATUS_BOTH_LOSE = 5
