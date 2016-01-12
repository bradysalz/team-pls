from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, url_for, request, redirect, session
from keys import summoner_names, SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///matches.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = SECRET_KEY

db = SQLAlchemy(app)


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
            print sel
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

        queued = ','.join(queued)
        session['queued'] = queued

        return redirect(url_for('big_data', summ=sel, team=queued))


@app.route('/big-data', methods=['POST', 'GET'])
def big_data():
    """WHICH DATA"""
    if request.method == 'GET':
        return render_template('data-team.html')

    if request.method == 'POST':
        session['data_choice'] = request.form['top_data']
        return redirect(url_for('plot_team'))


@app.route('/plot-team')
def plot_team():
    """HOW MUCH TEAM"""

    return '\n\n'.join(session.values())


if __name__ == '__main__':
    app.run(debug=True)
