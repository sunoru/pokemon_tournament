class Player(object):

    def __init__(self, name):
        self.name = name
        self.win = self.lose = self.tie = 0


class Tournament(object):

    def __new__(cls, kind, players):
        if kind.lower() == "swiss":
            return Swiss(players)
        else:
            raise KindError


class Swiss(Tournament):

    def __init__(self, players):
        if isinstance(players[0], string):
            players = [Player(x) for x in players]
        self.playsrs = players
        self.round = 0
        self.log = []
        self.started = False

    def strat(self):
        self.started = True

    def start_round(self, round=-1):
        if not self.started:
            raise TournamentError
        if round >= 0:
            self.round = round
        else:
            self.round += 1

    def stop(self):
        pass


class TournamentError(Exception):
    _mes = 'Unknown Error.'

    def __init__(self):
        Ecception.__init__(self, self._mes)


class KindError(TournamentError):
    _mes = 'No such kind of tournament!'


class NotStartedError(TournamentError):
    _mes = 'The tournament is not running!'
