import requests
import datetime
import time

from keys import API_KEY, summoner_names, id_lookup
from models import MatchResult
from teampls import db

test_get_summ_id = False
test_get_recent_matches = True

base_url = 'https://na.api.pvp.net/api/lol/na/'
url_key = {'api_key': API_KEY}


def get_summ_id(sum_names):
    """Turns summoner names into summoner ids
    Expects summoner_names as a dictionary {'Real Name' : 'Summoner Name'}
    Returns ids as a dictionary {'Real Name' : 'id'}
    """
    get_summoner_name_url = 'v1.4/summoner/by-name/'

    sum_ids = {}
    for name in sum_names:
        curr_url = base_url + get_summoner_name_url + sum_names[name].lower()
        req = requests.get(curr_url, params=url_key)
        # print curr_url

        if req.status_code == 200:
            req = req.json()
            sum_ids[name] = req[sum_names[name]]['id']

    return sum_ids


def check_recent_matches(summoner_id):
    """Takes summoner_id, checks to see if match in database, adds if not
    If not in database, parses the match and adds to database
    """
    get_matches_url = 'v1.3/game/by-summoner/'  # don't forget to append recent
    if type(summoner_id) != str:
        summoner_id = str(summoner_id)

    req_url = base_url + get_matches_url + summoner_id + '/recent/'
    hit = requests.get(req_url, params=url_key)

    if hit.status_code == 200:
        data = hit.json()
    else:
        return -1

    games = data['games']
    for game in games:
        # if not already in database, add to database
        game_exists = MatchResult.query.filter_by(match=game['gameId'], summoner=id_lookup[float(summoner_id)])
        if game_exists.first() is None:
            add_to_db(game, data['summonerId'])


def parse_match_to_db(game, summ_id):
    """Turns JSON match data into database object
    """
    date = datetime.datetime.fromtimestamp(float(game['createDate'])/1000.)
    match = game['gameId']
    summoner = id_lookup[summ_id].lower()
    mode = game['subType']

    stats = game['stats']
    win_game = stats.get('win',0)
    kills = stats.get('championsKilled',0)
    deaths = stats.get('numDeaths',0)
    assists = stats.get('assists',0)
    damage = stats.get('totalDamageDealtToChampions',0)
    gold = stats.get('goldEarned',0)
    wards = stats.get('wardPlaced',0)
    lane = stats.get('playerPosition',0)
    role = stats.get('playerRole',0)


    return MatchResult(date, match, summoner, mode, win_game,
                       kills, deaths, assists, damage, gold,
                       wards, lane, role)


def add_to_db(game_data, summ_id):
    """Adds MatchResult to database"""
    if type(game_data) != MatchResult:
        game_data = parse_match_to_db(game_data, summ_id)

    db.session.add(game_data)
    db.session.commit()

    print 'Added match {0}'.format(str(game_data.match))


if __name__ == '__main__':
    print 'testing'

    if test_get_recent_matches:
        for x in [169964, 19908711, 20294405, 26658116]:
            check_recent_matches(x)
            time.sleep(1)

    if test_get_summ_id:
        ids = get_summ_id(summoner_names)
        with open('team.csv', 'w') as team:
            for name in ids:
                row = name+','+summoner_names[name]+','+str(ids[name])+'\n'
                team.write(row)