from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
from flask import Flask, render_template, url_for, request, redirect, session
from keys import summoner_names, SECRET_KEY

import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///matches.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = SECRET_KEY

db = SQLAlchemy(app)

# need this after db to stop circular imports
import models


@app.route('/', methods=['POST', 'GET'])
@app.route('/team', methods=['POST', 'GET'])
def who_is_champ():
    """WHICH SUMMONER"""
    if request.method == 'GET':
        return render_template('home.html')

    if request.method == 'POST':
        session['summ'] = request.form['individual']
        return redirect(url_for('choose_team'))


@app.route('/not-team', methods=['POST', 'GET'])
def choose_team():
    """WHICH TEAM"""
    if request.method == 'GET':
        sel = session['summ']
        if sel is None:
            return 'GET with no data'
        else:
            team = summoner_names.keys()
            team.remove(sel.title())
            return render_template('not-team.html', team=team)

    if request.method == 'POST':
        sel = session['summ']
        team = summoner_names.keys()
        team.remove(sel.title())

        queued = []
        for t in team:
            if request.form.get(t) == 'on':
                queued.append(t)

        # queued = ','.join(queued)
        session['queued'] = queued

        if queued is None:
            return redirect(url_for('choose_team'))
        return redirect(url_for('big_data'))


@app.route('/big-data', methods=['POST', 'GET'])
def big_data():
    """WHICH DATA"""
    if request.method == 'GET':
        return render_template('data-team.html')

    if request.method == 'POST':
        session['data_choice'] = request.form['top_data']
        return redirect(url_for('plot_team'))


@app.route('/plot-team', methods=['POST', 'GET'])
def plot_team():
    """HOW MUCH TEAM"""
    # TODO Filter so it's only summoner's rift
    # TODO Filter so it's games without team vs games with (currently all games vs with team)
    # TODO Lots of checking for empty lists (uses list[0] a lot without checking)
    if request.method == 'GET':
        team_names = [summoner_names[session['summ']]]
        for member in session['queued']:
            team_names.append(summoner_names[member])

        # get list of games that individual has played
        summ_game_list = db.session.query(models.MatchResult.date,
                                          models.MatchResult.match,
                                          models.MatchResult.summoner,
                                          select_to_tbl_col()) \
            .filter(models.MatchResult.summoner == summoner_names[session['summ']]) \
            .all()

        # get game ids that team has played
        team_id_list = db.session.query(models.MatchResult.match,
                                        models.MatchResult.summoner,
                                        func.count(models.MatchResult.match)) \
            .filter(models.MatchResult.summoner.in_(team_names)) \
            .group_by(models.MatchResult.match) \
            .having(func.count(models.MatchResult.match) == len(team_names)) \
            .all()

        # returns a tuple (id, summ, cnt), this removes cnt
        team_id_list = set([team_id[0] for team_id in team_id_list])

        # get list of games that team has played
        # list of tuples in form (date, match, summoner, data)
        games_with_team = [game for game in summ_game_list if game[1] in team_id_list]

        # get info from valid games
        dates_with_team = [game[0] for game in games_with_team]
        data_with_team = [game[3] for game in games_with_team]

        # only non numeric option
        # assumes data_with_team has len>0, not ideal
        if type(data_with_team[0]) is bool:
            data_with_team = [1 if win else 0 for win in data_with_team]

        avg_team_data = sum(data_with_team)/float(len(data_with_team))

        # get list of games without team and parse
        # same as above
        games_without_team = [game for game in summ_game_list if game[1] not in team_id_list]

        # get info from valid games
        dates_without_team = [game[0] for game in games_without_team]
        data_without_team = [game[3] for game in games_without_team]

        if type(data_without_team[0]) is bool:
            data_without_team = [1 if win else 0 for win in data_without_team]

        avg_no_team_data = sum(data_without_team)/float(len(data_without_team))
        # print data_without_team, avg_no_team_data

        phrase = phrase_lookup(session['data_choice'], avg_no_team_data, avg_team_data)

        team_str_data = ','.join(column_to_string(data_with_team))
        no_team_str_data = ','.join(column_to_string(data_without_team))

        team_str_time = ','.join(datetime_to_string(dates_with_team))
        no_team_str_time = ','.join(datetime_to_string(dates_without_team))

        print team_str_time
        print team_str_data
        return render_template('plot-team.html', phrase=phrase,
                               team_data=team_str_data,
                               team_time=team_str_time,
                               no_team_data=no_team_str_data,
                               no_team_time=no_team_str_time)

    if request.method == 'POST':
        if 'back' in request.form.keys():
            return redirect(url_for('big_data'))

        elif 'restart' in request.form.keys():
            return redirect(url_for('who_is_champ'))

        else:
            return 'sick you broke it'


def datetime_to_string(dt_list):
    """Converts list of datetimes to list of strings
    :param dt_list: list of datetimes
    :return :
    """
    return ["'" + dt.strftime('%m/%d/%y %H:%M') + "'" for dt in dt_list]


def phrase_lookup(data_type, summ_avg, team_avg):
    """Generate string that for summoner vs team comparisons
    win <x> more/less games
    earn <x> more/less gold
    place <x> more/less wards
    do <x> more/less damage
    get <x> more/less kills/deaths/assists/gold
    :param data_type: MatchResult.<what> -> DB Column
    :param summ_avg: average of summoner data in games without team
    :param team_avg: average of summoner data in games with team
    :return phrase: string sentence that represents the data (You do 1.7
    """
    if data_type == "wins":
        phrase = 'You get'
    elif data_type == "gold":
        phrase = 'You earn'
    elif data_type == "wards":
        phrase = 'You place'
    elif data_type == "damage":
        phrase = 'You do'
    else:
        phrase = 'You get'

    if summ_avg >= team_avg:
        percent_diff = 100*0.5*(summ_avg-team_avg)/(team_avg+summ_avg)
        phrase += ' {:.1f}%'.format(percent_diff)
        phrase += ' less'
    else:
        percent_diff = 100*0.5*(team_avg-summ_avg)/(team_avg+summ_avg)
        phrase += ' {:.1f}%'.format(percent_diff)
        phrase += ' more'

    phrase += ' ' + data_type + ' with team'

    print phrase
    return phrase


def column_to_string(column):
    """Converts list of column data to list of strings for plotting
    :param column: column from DB, a list of data
    :return output_str: converts column to str
    """
    if type(column[0]) == bool:
        output_str = ['1' if item else '0' for item in column]
    elif type(column[0]) == int:
        output_str = [str(item) for item in column]
    elif type(column[0]) == str or type(column[0]) == unicode:
        output_str = column
    return output_str


def select_to_tbl_col():
    """Converts stored select option to DB column for queries
    :return MatchResult.Column:
    """
    val = session['data_choice']
    if val == "wins":
        return models.MatchResult.win_game
    elif val == "kills":
        return models.MatchResult.kills
    elif val == "deaths":
        return models.MatchResult.deaths
    elif val == "assists":
        return models.MatchResult.assists
    elif val == "damage":
        return models.MatchResult.damage
    elif val == "gold":
        return models.MatchResult.gold
    elif val == "wards":
        return models.MatchResult.wards


if __name__ == '__main__':
    app.run(debug=True)
