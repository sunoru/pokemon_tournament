# coding=utf-8
from django.db import models
from django.utils import timezone
from accounts.models import Option
from pmtour.models import (
    BaseModel, Tournament, Player, Turn,
    LOG_STATUS_UNKNOWN, LOG_STATUS_A_WIN, LOG_STATUS_B_WIN,
    LOG_STATUS_TIE, LOG_STATUS_BYE, LOG_STATUS_BOTH_LOSE,
)

class Log(BaseModel):
    player_a = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player_a_log")
    player_b = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player_b_log", null=True)
    status = models.SmallIntegerField("status", default=LOG_STATUS_UNKNOWN)
    results = models.TextField("results", default="")
    time = models.DateTimeField("time", null=True)
    turn = models.ForeignKey(Turn, on_delete=models.CASCADE)
    table_id = models.SmallIntegerField("table id")

    STATUS_DICT = {
        LOG_STATUS_A_WIN: LOG_STATUS_B_WIN,
        LOG_STATUS_B_WIN: LOG_STATUS_A_WIN,
        LOG_STATUS_TIE: LOG_STATUS_TIE,
        LOG_STATUS_BOTH_LOSE: LOG_STATUS_BOTH_LOSE,
    }

    def check_status(self, status):
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
            if status in (LOG_STATUS_A_WIN, LOG_STATUS_BOTH_LOSE):
                self.player_b.eliminated = True
            if status in (LOG_STATUS_B_WIN, LOG_STATUS_BOTH_LOSE):
                self.player_a.eliminated = True
            self.player_a.set_log(status, self.player_b, False)
            self.player_a.save()
            if self.player_b is not None:
                self.player_b.set_log(Log.STATUS_DICT[status], self.player_a, False)
                self.player_b.save()

    def delete_status(self):
        status = self.status
        if status in (LOG_STATUS_UNKNOWN, LOG_STATUS_BYE):
            return
        pa, pb = self.player_a, self.player_b
        if self.turn.type == Tournament.SWISS:
            pa.delete_log(status, pb)
            pa.save()
            if pb is not None:
                pb.delete_log(Log.STATUS_DICT[status])
                pb.save()
        elif self.turn.type == Tournament.SINGLE:
            if status in (LOG_STATUS_A_WIN, LOG_STATUS_BOTH_LOSE):
                pb.eliminated = False
            if status in (LOG_STATUS_B_WIN, LOG_STATUS_BOTH_LOSE):
                pa.eliminated = False
            pa.delete_log(status, pb, False)
            pa.save()
            if pb is not None:
                pb.delete_log(Log.STATUS_DICT[self.status], pa, False)
                pb.save()
        self.status = LOG_STATUS_UNKNOWN

    def __str__(self):
        if self.status == LOG_STATUS_UNKNOWN:
            return "%s %s vs. %s" % (str(self.turn), self.player_a.name, self.player_b.name)
        if self.status == LOG_STATUS_A_WIN:
            return "%s %s won against %s" % (str(self.turn), self.player_a.name, self.player_b.name)
        if self.status == LOG_STATUS_B_WIN:
            return "%s %s won against %s" % (str(self.turn), self.player_a.name, self.player_b.name)
        if self.status == LOG_STATUS_TIE:
            return "%s %s and %s tied" % (str(self.turn), self.player_a.name, self.player_b.name)
        if self.status == LOG_STATUS_BYE:
            return "%s %s byed" % (str(self.turn), self.player_a.name)
        if self.status == LOG_STATUS_BOTH_LOSE:
            return "%s %s and %s both lost" % (str(self.turn), self.player_a.name, self.player_b.name)

    def get_winner(self):
        if self.status == LOG_STATUS_A_WIN:
            return self.player_a
        if self.status == LOG_STATUS_B_WIN:
            return self.player_b
        return None

    def get_loser(self):
        if self.status == LOG_STATUS_A_WIN:
            return self.player_b
        if self.status == LOG_STATUS_B_WIN:
            return self.player_a
        return None

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
        log.check_status(LOG_STATUS_BYE)
        log.save()

    @classmethod
    def create_from_player_pairs(cls, turn, start_table_id, player_pairs, byed_players=[]):
        table_id = start_table_id - 1
        for player in byed_players:
            table_id += 1
            cls.create_bye(turn, table_id, player)
        for pair in player_pairs:
            table_id += 1
            p1 = pair[0]
            p2 = pair[1]
            if p2 is None:
                cls.create_bye(turn, table_id, p1)
            else:
                cls.create_from_player(turn, table_id, p1, p2)

    @classmethod
    def create_from_players(cls, turn, players, byed_players=[]):
        table_id = 0
        for player in byed_players:
            table_id += 1
            cls.create_bye(turn, table_id, player)
        for i in range(0, len(players) // 2):
            table_id += 1
            p1 = players[i * 2]
            p2 = players[i * 2 + 1]
            cls.create_from_player(turn, table_id, p1, p2)
        if len(players) & 1 == 1:
            table_id += 1
            p1 = players[-1]
            cls.create_bye(turn, table_id, p1)

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
