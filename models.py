from flask import Flask, db
from teampls import db

app = Flask(__name___)

class MatchResult(db.Model):
	# team match results for a player
	
	# match ID data
	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.DateTime)
	match = db.Column(db.Integer)
	summoner = db.Column(db.String(18)) # summoner name, all lowercase ('dahtguy')
	mode = db.Column(db.String(25)) # game mode (NORMAL, SOLO_5X5, etc)

	# game data
	win_game = db.Column(db.Boolean) # True = Victory, False = Arnold
	kills = db.Column(db.Integer)
	deaths = db.Column(db.Integer)
	assists = db.Column(db.Integer)

	damage = db.Column(db.Integer) # totalDamageDealtToChampions
	gold = db.Column(db.Integer)   # gold earned
	wards = db.Column(db.Integer)  # wards placed

	lane = db.Column(db.Integer) # playerPosition
	role = db.Column(db.Integer) # playerRole

	def __init__(self, date, match=0, summoner='', mode='', 
					win_game=False, kills=0, deaths=0, assists=0,
					damage=0, gold=0, wards=0, lane=0, role=0):

		self.date  = date
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
		won = 'won' if win_game else 'lost'
		return '<Match {0} was {1} by Player {2}>'.format(match, won, summoner)

