# coding=utf-8
from django.db import models
import json
from accounts.models import PlayerUser
from pmtour.models import BaseModel, Tournament


class Player(BaseModel):
    user = models.ForeignKey(PlayerUser)
    name = models.CharField("name", max_length=100, default="")  # 参赛时候的名字，可以跟self.user.name不一样
    tournament = models.ForeignKey(Tournament)
    playerid = models.SmallIntegerField()
    wins = models.SmallIntegerField(default=0)
    loses = models.SmallIntegerField(default=0)
    ties = models.SmallIntegerField(default=0)
    byes = models.SmallIntegerField(default=0)
    foes = models.ManyToManyField("self")
    standing = models.SmallIntegerField(default=0)
    late = models.BooleanField(default=False)
    eliminated = models.BooleanField(default=False)
    exited = models.BooleanField(default=False)
    score = models.IntegerField(default=0)

    class Meta:
        app_label = 'pmtour'

    @classmethod
    def create(cls, **kwargs):
        player = cls.objects.create(**kwargs)
        if player.late and player.tournament.status > 0:
            player.loses += player.tournament.status
            player.save()
        return player

    @classmethod
    def create_from_data(cls, tour, data):
        if data["player_id"].find("test") == -1:
            q = PlayerUser.objects.filter(player_id=data["player_id"])
            if q:
                if data.get("username", data["player_id"]) == q[0].name:
                    playeruser = q[0]
                else:
                    raise cls.LoaddataError("the username doesn't match to the player id.")
            else:
                playeruser = PlayerUser.create_existed_player(
                    player_id=data["player_id"],
                    name=data.get("username", data["player_id"])
                )
        else:
            playeruser = PlayerUser.create_test_player(tour, data["name"], data["playerid"])
        if not data["standing"]:
            data["standing"] = ""
        player = cls.create(
            user=playeruser,
            name=data.get("name", data["playerid"]),
            tournament=tour,
            playerid=data["playerid"],
            wins=data["wins"],
            loses=data["loses"],
            ties=data["ties"],
            byes=data["byes"],
            standing=data["standing"],
            late=data["late"],
            eliminated=data["eliminated"],
            exited=data["exited"],
            score=data["score"]
        )
        return player

    @classmethod
    def dumpdata(cls, tour):
        players = []
        for player in tour.player_set.all():
            aplayer = {
                "username": player.user.name,
                "player_id": player.user.player_id,
                "name": player.name,
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
        return players

    @classmethod
    def loaddata(cls, tour, players_data):
        def cancel_load(data):
            for p in data:
                p[0].user.delete()
                p[0].delete()
        players = []
        for player_data in players_data:
            try:
                player = cls.create_from_data(tour, player_data)
            except cls.LoaddataError:
                cancel_load(players)
                return "Error creating players."
            players.append((player, player_data["foes"]))
        for player, foes_data in players:
            foes = json.loads(foes_data)
            for foe_id in foes:
                try:
                    foe = tour.player_set.get(playerid=foe_id)
                except cls.DoesNotExist:
                    cancel_load(players)
                    return "Error loading foes."
                player.foes.add(foe)
            player.save()
        return False


    def __unicode__(self):
        return "%s(%s) (%s) %s" % (self.name, self.user.name, self.get_printable(), self.score)

    def get_printable(self):
        return "%s/%s/%s" % (self.wins + self.byes, self.loses, self.ties)

    def get_winning_persentage(self):
        re = self.wins + self.loses + self.ties + self.byes
        if re == 0:
            return 0.0
        re = float(self.wins) / re
        if re < 0.25:
            re = 0.25
        if self.exited and re > 0.75:
            re = 0.75
        return re

    def get_opponents_wp(self):
        # 有空写成Property
        if len(self.foes.all()) == 0:
            return 0.0
        else:
            return sum([x.get_winning_persentage() for x in self.foes.all()]) / self.foes.count()

    def get_opps_opps_wp(self):
        if len(self.foes.all()) == 0:
            return 0.0
        else:
            return sum([x.get_opponents_wp() for x in self.foes.all()]) / self.foes.count()

    def gen_standing_dict(self):
        return {
            "standing": self.standing,
            "pid": self.playerid,
            "match": self.get_printable(),
            "score": self.score,
            "opswin": "{0:.2%}".format(self.get_opponents_wp()),
            "opsopswin": "{0:.2%}".format(self.get_opps_opps_wp()),
        }

    def set_log(self, status, foe=None, scored=True):
        if status == 4:
            if scored:
                self.score += 3
            self.byes += 1
        elif status == 3:
            if scored:
                self.score += 1
            self.ties += 1
        elif status == 2:
            self.loses += 1
        elif status == 1:
            if scored:
                self.score += 3
            self.wins += 1
        if foe is not None:
            self.foes.add(foe)

    def delete_log(self, status, foe=None):
        if status == 4:
            self.score -= 3
            self.byes -= 1
        elif status == 3:
            self.score -= 1
            self.ties -= 1
        elif status == 2:
            self.loses -= 1
        elif status == 1:
            self.score -= 3
            self.wins -= 1
        if foe is not None:
            self.foes.remove(foe)

    def exit(self):
        self.exited = True

    def eliminate(self):
        self.eliminated = True

    def has_meeted(self, another):
        return another in self.foes.all()

    @staticmethod
    def _by_playerid(a, b):
        if a.playerid > b.playerid:
            return 1
        return -1

    @staticmethod
    def _by_standing(a, b):
        if a.standing > b.standing:
            return 1
        else:
            return -1

    @classmethod
    def _get_sorted(cls, tour, compare, **kwargs):
        players = tour.player_set.filter(**kwargs)
        players = [x for x in players]
        players.sort(cmp=compare)
        return players

    @classmethod
    def get_sorted_by_playerid(cls, tour):
        return cls._get_sorted(tour, cls._by_playerid, exited=False, eliminated=False)

    @classmethod
    def get_sorted_by_standing(cls, tour):
        return cls._get_sorted(tour, cls._by_standing, exited=False, eliminated=False)

    @classmethod
    def get_sorted_for_elims(cls, tour):
        players = cls._get_sorted(tour, cls._by_standing)
        elims = tour.get_option("elims")
        if elims == 8:
            q = [1, 8, 4, 5, 3, 6, 2, 7]
        elif elims == 4:
            q = [1, 4, 2, 3]
        elif elims == 2:
            q = [1, 2]
        else:
            raise Tournament.NoTypeError("the number of players is wrong")
        players = [players[i - 1] for i in q if not players[i - 1].eliminated]
        return players

