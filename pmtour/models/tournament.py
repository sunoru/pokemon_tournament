# coding=utf-8
from django.db import models
from django.utils import timezone
import accounts.models
import datetime
import json


class Tournament(models.Model):
    SWISS = "swiss"
    SINGLE = "single"
    SWISS_PLUS_SINGLE = "swiss_single"
    TYPE_CHOICES = (
        (SWISS, "Swiss"),
        (SINGLE, "Single Elimination"),
        (SWISS_PLUS_SINGLE, "Swiss plus Single Elimination")
    )
    name = models.CharField("name", max_length=100, default='a tournament')
    tour_id = models.CharField("tour_id", max_length=20, unique=True)
    alias = models.CharField("alias", max_length=20, unique=True)
    tournament_type = models.CharField("type", max_length=100, choices=TYPE_CHOICES)
    start_time = models.DateTimeField("start time", default=datetime.datetime(2014, 10, 6, 13, 0))
    description = models.TextField("description", default="")
    status = models.SmallIntegerField("status", default=-2)
    admins = models.ManyToManyField(accounts.models.PlayerUser)
    remarks = models.TextField(default="{}")  # use for the age separated swiss, swiss plus turns, etc
    # the format for each turn

    class NoTypeError(Exception):
        pass

    class InvalidAliasError(Exception):
        pass

    class InvalidNumberError(Exception):
        pass

    class TourOverError(Exception):
        pass

    class Meta:
        app_label = 'pmtour'

    @classmethod
    def alias_unique(cls, alias):
        return cls.objects.filter(alias=alias).count() == 0

    @classmethod
    def create(cls, admin, **kwargs):
        uid = accounts.models.Option.objects.get(option_name="uid")
        uid.option_value = str(int(uid.option_value) + 1)
        kwargs["tour_id"] = str(100000 + int(uid.option_value))
        uid.save()
        if "alias" not in kwargs:
            kwargs["alias"] = kwargs["tour_id"]
        else:
            if Tournament.is_unique(kwargs["alias"]):
                raise Tournament.InvalidAliasError
        tour = cls.objects.create(**kwargs)
        tour.admins.add(admin)
        return tour

    def dumpdata(self):
        data = {
            "name": self.name,
            "alias": self.alias,
            "tournament_type": self.tournament_type,
            "start_time": self.start_time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "description": self.description,
            "remarks": self.remarks,
        }
        players = []
        for player in self.player_set.all():
            aplayer = {
                "playerid": player.playerid,
                "wins": player.wins,
                "loses": player.loses,
                "ties": player.ties,
                "byes": player.byes,
                "foes": json.dumps([x.playerid for x in player.foes.all()]),
                "standing": player.standing,
                "late": player.late,
                "eliminated": player.eliminated,
                "exited": player.exited,
                "score": player.score
            }
            players.append(aplayer)
        data["players"] = players
        turns = []
        for turn in self.turn_set.all():
            aturn = {
                "turn_number": turn.turn_number,
                "standings": turn.standings,
                "type": turn.type,
            }
            logs = []
            for tlog in turn.log_set.all():
                alog = {
                    "player_a": tlog.player_a.playerid,
                    "player_b": tlog.player_b.playerid if tlog.player_b is not None else None,
                    "status": tlog.status,
                    "results": tlog.results,
                    "time": tlog.time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                }
                logs.append(alog)
            aturn["logs"] = logs
            turns.append(aturn)
        data["turns"] = turns
        return json.dumps(data)

    @staticmethod
    def loaddata(datas):
        data = json.loads(datas)

        #TODO: load data here
        pass

    def set_option(self, option_name, option_value=None):
        pst = json.loads(self.remarks)
        pst[option_name] = option_value
        self.remarks = json.dumps(pst)

    def get_option(self, option_name):
        pst = json.loads(self.remarks)
        return pst.get(option_name, None)

    def get_current_turn(self):
        if self.is_over():
            return self.turn_set.last()
        else:
            return self.turn_set.get(turn_number=self.status)

    def get_last_turn(self):
        from pmtour.models import Turn
        try:
            if self.is_over():
                return self.turn_set.last()
            return self.turn_set.get(turn_number=self.status - 1)
        except Turn.DoesNotExist:
            return None

    def get_players_count(self):
        return self.player_set.count()

    def get_available_playerid(self):
        playerids = [x.playerid for x in self.player_set.all()]
        if len(playerids) == 0:
            return 1
        playerids.sort()
        for u in xrange(1, len(playerids)):
            if playerids[u] != playerids[u - 1] + 1:
                return playerids[u - 1] + 1
        return playerids[-1] + 1

    def refresh(self):
        if self.status == -1 and (
            datetime.datetime.now() - timezone.localtime(self.start_time).replace(tzinfo=None)
        ).total_seconds() >= 0:
            self.status = 0
            self.save()

    def _get_type(self, turn_number):
        if self.tournament_type == Tournament.SWISS or self.tournament_type == Tournament.SINGLE:
            return self.tournament_type
        elif self.tournament_type == Tournament.SWISS_PLUS_SINGLE:
            return Tournament.SWISS if turn_number <= self.get_option("turns") else Tournament.SINGLE
        else:
            raise Tournament.NoTypeError

    def ready(self):
        self.status = -1

    def begin(self):
        t = timezone.now()
        self.start_time = t.strftime("%Y-%m-%dT%H:%M:%S%z")
        self.status = 0

    def _should_end(self):
        if self.tournament_type == Tournament.SWISS:
            return self.status >= self.get_option("turns")
        return self.player_set.filter(eliminated=False).count() == 1

    def start(self, turn_number):
        from pmtour.models import Turn
        if self._should_end():
            self.stop()
            return
        self.status = turn_number
        turn = Turn.objects.create(
            tournament=self,
            turn_number=turn_number,
            standings="",
            type=self._get_type(turn_number),
            status=0
        )
        turn.start()
        turn.save()

    def end(self):
        turn = self.get_current_turn()
        turn.end()
        turn.save()

    def get_current_champion(self):
        from pmtour.models import Player
        if self.tournament_type == Tournament.SWISS:
            turn = self.get_last_turn()
            return self.player_set.get(playerid=turn.get_standing()[0]["pid"])
        try:
            return self.player_set.get(eliminated=False)
        except Player.MultipleObjectsReturned:
            return None

    def on_swiss_over(self, turn_number=None):
        if turn_number is None:
            turn_number = self.status
        return self.tournament_type == Tournament.SWISS_PLUS_SINGLE and self.get_option("turns") <= turn_number

    def stop(self):
        turn = self.get_current_turn()
        turn.gen_last_standings()
        turn.save()
        self.set_option("champion", self.get_current_champion().playerid)
        self.set_option("total_turns", self.status)
        self.status = -3

    def is_over(self):
        return self.status == -3

    def __unicode__(self):
        return "%s (%s) %s" % (self.name, self.status, self.start_time)
