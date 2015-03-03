# coding=utf-8
from django.db import models
from django.utils import timezone
from pmtour.models import BaseModel, Tournament, Player, Turn


class Log(BaseModel):
    player_a = models.ForeignKey(Player, related_name="player_a_log")
    player_b = models.ForeignKey(Player, related_name="player_b_log", null=True)
    status = models.SmallIntegerField("status", default=0)  # 1 for a win, 2 for b win, 3 for tie, 4 for bye
    results = models.TextField("results", default="")
    time = models.DateTimeField("time", null=True)
    turn = models.ForeignKey(Turn)

    _STATUS_DICT = {
        1: 2,
        2: 1,
        3: 3
    }

    class Meta:
        app_label = 'pmtour'

    def check(self, status):
        if self.status != 0:
            self.delete_status()
        self.status = status
        t = timezone.now()
        self.time = t.strftime("%Y-%m-%dT%H:%M:%S%z")
        if self.turn.type == Tournament.SWISS:
            self.player_a.set_log(status, self.player_b)
            self.player_a.save()
            if self.player_b is not None:
                self.player_b.set_log(Log._STATUS_DICT[status])
                self.player_b.save()
        elif self.turn.type == Tournament.SINGLE:
            self.player_a.set_log(status, self.player_b, False)
            if status == 1:
                self.player_b.eliminated = True
                self.player_b.set_log(Log._STATUS_DICT[status], scored=False)
                self.player_b.save()
            elif status == 2:
                self.player_a.eliminated = True
                self.player_b.set_log(Log._STATUS_DICT[status], scored=False)
                self.player_b.save()
            self.player_a.save()

    def delete_status(self):
        if self.status == 0 or self.status == 4:
            return
        self.player_a.delete_log(self.status, self.player_b)
        self.player_a.save()
        if self.player_b is not None:
            self.player_b.delete_log(Log._STATUS_DICT[self.status])
            self.player_b.save()
        self.status = 0

    def __unicode__(self):
        if self.status == 0:
            return "%s vs. %s" % (self.player_a, self.player_b)
        if self.status == 1:
            return "%s won against %s" % (self.player_a, self.player_b)
        if self.status == 2:
            return "%s won against %s" % (self.player_b, self.player_a)
        if self.status == 3:
            return "%s and %s tied" % (self.player_a, self.player_b)
        if self.status == 4:
            return "%s byed" % self.player_a

    def get_winner(self):
        if self.status == 3:
            return None
        if self.status == 2:
            return self.player_b
        return self.player_a

    def get_loser(self):
        if self.status == 3:
            return None
        if self.status == 2:
            return self.player_a
        return self.player_b

    @staticmethod
    def search(a, b):
        try:
            log = a.player_a_log.get(player_b=b)
        except Log.DoesNotExist:
            return None
        return log

    @classmethod
    def create_from_player(cls, turn, p1, p2):
        cls.objects.create(
            player_a=p1,
            player_b=p2,
            turn=turn
        )

    @classmethod
    def create_bye(cls, turn, p1):
        log = cls.objects.create(
            player_a=p1,
            player_b=None,
            turn=turn
        )
        log.check(4)
        log.save()

    @classmethod
    def create_from_player_pairs(cls, turn, player_pairs):
        for pair in player_pairs:
            p1 = pair[0]
            p2 = pair[1]
            if p2 is None:
                cls.create_bye(turn, p1)
            else:
                cls.create_from_player(turn, p1, p2)

    @classmethod
    def create_from_players(cls, turn, players):
        for i in xrange(0, len(players) / 2):
            p1 = players[i * 2]
            p2 = players[i * 2 + 1]
            cls.create_from_player(turn, p1, p2)

        if len(players) & 1 == 1:
            p1 = players[-1]
            cls.create_bye(turn, p1)

    @classmethod
    def create_from_data(cls, turn, data):
        try:
            player_a = turn.tournament.player_set.get(playerid=data["player_a"])
            player_b = turn.tournament.player_set.get(playerid=data["player_b"])
        except Player.DoesNotExist:
            raise cls.LoaddataError
        try:
            log = cls.objects.create(
                player_a=player_a,
                player_b=player_b,
                status=data["status"],
                results=data["results"],
                time=data["time"],
                turn=turn
            )
        except Exception:
            raise cls.LoaddataError
        return log

    @classmethod
    def dumpdata(cls, turn):
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
        return logs

    @classmethod
    def loaddata(cls, turn, logs_data):
        def cancel_load(data):
            for p in data:
                p.delete()
        logs = []
        for log_data in logs_data:
            try:
                log = cls.create_from_data(turn, log_data)
            except cls.LoaddataError:
                cancel_load(logs)
                return False
            log.save()
            logs.append(log)
        return True
