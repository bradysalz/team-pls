import datetime

from teampls import db


class MatchResult(db.Model):
    # team match results for a player
    # comments refer to API tag

    # match ID data
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)        # createDate
    match = db.Column(db.Integer)        # gameId
    summoner = db.Column(db.String(18))  # summoner name, all lowercase ('dahtguy')
    mode = db.Column(db.String(25))      # gameMode (NORMAL, SOLO_5X5, etc)

    # game data
    win_game = db.Column(db.Boolean)  # win (True = Victory, False = Arnold)
    kills = db.Column(db.Integer)     # championsKilled
    deaths = db.Column(db.Integer)    # numDeaths
    assists = db.Column(db.Integer)   # assists

    damage = db.Column(db.Integer)  # totalDamageDealtToChampions
    gold = db.Column(db.Integer)    # gold [gold earned]
    wards = db.Column(db.Integer)   # wardsPlaced

    lane = db.Column(db.Integer)  # playerPosition
    role = db.Column(db.Integer)  # playerRole

    def __init__(self, date=None, match=0, summoner='', mode='',
                 win_game=False, kills=0, deaths=0, assists=0,
                 damage=0, gold=0, wards=0, lane=0, role=0):

        if date is None:
            self.date = datetime.datetime.utcnow()
        else:
            self.date = date

        self.match = match
        self.summoner = summoner
        self.mode = mode
        self.win_game = win_game
        self.kills = kills
        self.deaths = deaths
        self.assists = assists
        self.damage = damage
        self.gold = gold
        self.wards = wards
        self.lane = lane
        self.role = role

    def __repr__(self):
        won = 'won' if self.win_game else 'lost'
        summoner = 'N/A' if self.summoner == '' else self.summoner
        match = 'N/A' if self.match == 0 else self.match
        return '<Match {0} was {1} by Player {2}>'.format(match, won, summoner)

