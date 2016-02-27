# coding=utf-8
from django.db import models
from django.utils import timezone
from accounts.models import Option
from pmtour.models import BaseModel, Tournament, Player, Turn


class Log(BaseModel):
    player_a = models.ForeignKey(Player, related_name="player_a_log")
    player_b = models.ForeignKey(Player, related_name="player_b_log", null=True)
    status = models.SmallIntegerField("status", default=0)  # 1 for a win, 2 for b win, 3 for tie, 4 for bye
    results = models.TextField("results", default="")
    time = models.DateTimeField("time", null=True)
    turn = models.ForeignKey(Turn)
    table_id = models.SmallIntegerField("table id")

    STATUS_DICT = {
        1: 2,
        2: 1,
        3: 3,
    }

    def check_status(self, status):
        if 0 < self.status < 4:
            self.delete_status()
        self.status = status
        t = timezone.now()
        self.time = t.strftime("%Y-%m-%dT%H:%M:%S%z")
        if self.turn.type == Tournament.SWISS:
            self.player_a.set_log(status, self.player_b)
            self.player_a.save()
            if self.player_b is not None:
                self.player_b.set_log(Log.STATUS_DICT[status])
                self.player_b.save()
        elif self.turn.type == Tournament.SINGLE:
            if status == 1:
                self.player_b.eliminated = True
            elif status == 2:
                self.player_a.eliminated = True
            self.player_a.set_log(status, self.player_b, False)
            self.player_a.save()
            if self.player_b is not None:
                self.player_b.set_log(Log.STATUS_DICT[status], False)
                self.player_b.save()

    def delete_status(self):
        if self.status == 0 or self.status == 4:
            return
        if self.turn.type == Tournament.SWISS:
            self.player_a.delete_log(self.status, self.player_b)
            self.player_a.save()
            if self.player_b is not None:
                self.player_b.delete_log(Log.STATUS_DICT[self.status])
                self.player_b.save()
        elif self.turn.type == Tournament.SINGLE:
            if self.status == 1:
                self.player_b.eliminated = False
            elif self.status == 2:
                self.player_a.eliminated = False
            self.player_a.delete_log(self.status, self.player_b, False)
            self.player_a.save()
            if self.player_b is not None:
                self.player_b.delete_log(Log.STATUS_DICT[self.status], self.player_a, False)
                self.player_b.save()
        self.status = 0

    def __unicode__(self):
        if self.status == 0:
            return "%s %s vs. %s" % (unicode(self.turn), self.player_a.name, self.player_b.name)
        if self.status == 1:
            return "%s %s won against %s" % (unicode(self.turn), self.player_a.name, self.player_b.name)
        if self.status == 2:
            return "%s %s won against %s" % (unicode(self.turn), self.player_a.name, self.player_b.name)
        if self.status == 3:
            return "%s %s and %s tied" % (unicode(self.turn), self.player_a.name, self.player_b.name)
        if self.status == 4:
            return "%s %s byed" % (unicode(self.turn), self.player_a.name)

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
    def create_from_player(cls, turn, table_id, p1, p2):
        cls.objects.create(
            player_a=p1,
            player_b=p2,
            turn=turn,
            table_id=table_id
        )

    @classmethod
    def create_bye(cls, turn, table_id, p1):
        log = cls.objects.create(
            player_a=p1,
            player_b=None,
            turn=turn,
            table_id=table_id
        )
        log.check_status(4)
        log.save()

    @classmethod
    def create_from_player_pairs(cls, turn, start_table_id, player_pairs):
        table_id = start_table_id - 1
        for pair in player_pairs:
            table_id += 1
            p1 = pair[0]
            p2 = pair[1]
            if p2 is None:
                cls.create_bye(turn, table_id, p1)
            else:
                cls.create_from_player(turn, table_id, p1, p2)

    @classmethod
    def create_from_players(cls, turn, players):
        for i in xrange(0, len(players) / 2):
            p1 = players[i * 2]
            p2 = players[i * 2 + 1]
            cls.create_from_player(turn, i+1, p1, p2)

        if len(players) & 1 == 1:
            p1 = players[-1]
            cls.create_bye(turn, len(players)/2+1, p1)

    @classmethod
    def create_from_data(cls, turn, data):
        try:
            player_a = turn.tournament.player_set.get(playerid=data["player_a"])
            if data["player_b"]:
                player_b = turn.tournament.player_set.get(playerid=data["player_b"])
            else:
                player_b = None
        except Player.DoesNotExist:
            raise cls.LoaddataError
        if "results" not in data or not data["results"]:
            data["results"] = ""
        try:
            log = cls.objects.create(
                player_a=player_a,
                player_b=player_b,
                status=data["status"],
                results=data["results"],
                time=data["time"],
                table_id=data["table_id"],
                turn=turn
            )
        except Exception:
            raise cls.LoaddataError("Error creating logs")
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
                "table_id": tlog.table_id
            }
            logs.append(alog)
        return logs

    @classmethod
    def loaddata(cls, turn, logs_data):
        def cancel_load(data):
            for p in data:
                p.delete()
        logs = []
        i = 0
        for log_data in logs_data:
            i += 1
            if 'table_id' not in log_data:
                log_data['table_id'] = i
            try:
                log = cls.create_from_data(turn, log_data)
            except cls.LoaddataError as e:
                cancel_load(logs)
                return e.message
            log.save()
            logs.append(log)
        return ""
