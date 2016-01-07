import requests

from keys import API_KEY, summoner_names
from models import MatchResult

test_get_summ_id = False

base_url = 'https://na.api.pvp.net/api/lol/na/'
url_key = {'api_key' : API_KEY}


def get_summ_id(summoner_names):
    """Turns summoner names into summoner ids
    Expects summoner_names as a dictionary {'Real Name' : 'Summoner Name'}
    Returns ids as a dictionary {'Real Name' : 'id'}
    """
    get_summoner_name_url = 'v1.4/summoner/by-name/'

    sum_ids = {}
    for name in summoner_names:
        curr_url = base_url + get_summoner_name_url + summoner_names[name].lower()
        req = requests.get(curr_url, params=url_key)
        # print curr_url

        if req.status_code == 200:
            req = req.json()
            sum_ids[name] = req[summoner_names[name]]['id']

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
        if MatchResult.query.filter_by(match=game['gameId']).first() is None:
            add_to_db(game)


def parse_match_to_row(match):
    """Turns JSON match object into database object
    """
    pass


def add_to_db(game_data):
    """Adds MatchResult to database"""
    print 'Adding match {0}'.format(str(game_data['gameId']))


if __name__ == '__main__':
    print 'testing'

    check_recent_matches(26658116)

    if test_get_summ_id:
        ids = get_summ_id(summoner_names)
        with open('team.csv', 'w') as team:
            for name in ids:
                row = name+','+summoner_names[name]+','+str(ids[name])+'\n'
                team.write(row)