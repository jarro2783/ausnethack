"""
This is the main AusNethack web module.
"""

from flask import Flask, render_template
import os
import sqlite3
import wwwnethack as wwwnh
import yaml

app = Flask(__name__, static_folder='../static')
app.config.from_object('wwwconfig')

def dot_dirname(path):
    name = os.path.dirname(path)

    if name == '':
        return '.'
    else:
        return name

asset_map = yaml.load(open(dot_dirname(__file__) + '/assets.map.yaml'))

def sql_connect(game):
    """ Connect to the nethack sqlite database."""

    conn = sqlite3.connect(app.config['NETHACKDB'][game])
    conn.row_factory = sqlite3.Row
    return conn

def sql_query(game, query):
    """ Run a query on the database."""

    conn = sql_connect(game)
    cursor = conn.cursor()
    return cursor.execute(query).fetchall()

@app.context_processor
def utility_functions():
    def asset_url(path):
        return asset_map[path]
    return dict(asset_url=asset_url)

@app.template_filter('human_readable')
def human_readable_filter(seconds):
    return wwwnh.format_human_readable(seconds)

@app.route('/')
def main():
    """Index page."""
    #app.config.update(dict(title='nethack'))
    return render_template('index.html')

@app.route('/users')
def users():
    """Users page"""

    sql = sql_connect('360')
    cursor = sql.cursor()
    games = cursor.execute("""
      SELECT SUM(games.playing_time) AS total,
        plname,
        COUNT(DISTINCT games.id) AS numgames
      FROM games GROUP BY plname ORDER by plname
    """).fetchall()

    app.config.pagename = 'Users'
    return render_template('users.html', users=games)

@app.route('/zscores')
def zscores():
    """Zscores page."""

    conn = sql_connect('360')
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT plname, COUNT(ascended) AS number, role FROM games
        WHERE ascended = 1
        GROUP BY plname, role
    """).fetchall()

    scores, roles = wwwnh.calculate_zscores(rows)

    score_list = []

    for player in sorted(scores.keys(), reverse=True):
        score_list.append({'plname':player, 'zscore':scores[player]})

    return render_template('zscores.html', scores=score_list, roles=roles)

@app.route('/high_scores')
def high_scores():
    """High scores page."""

    scores = sql_query('360', """
        SELECT *
        FROM games
        WHERE score NOT NULL
        ORDER BY score DESC LIMIT 2000
        """)

    return render_template('high_scores.html', scores=scores)

if __name__ == '__main__':
    app.run(debug=True, port=6500)
