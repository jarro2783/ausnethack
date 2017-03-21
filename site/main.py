"""
This is the main AusNethack web module.
"""

import base64
from datetime import datetime
from flask import Flask, Markup, render_template, request, send_from_directory
from flask import redirect, url_for
import flask
import functools
import os
from wwwnethack import db
import wwwnethack as wwwnh
from wwwnethack import login
import yaml

app = Flask(__name__, static_folder='../assets/', static_url_path="/assets")
app.config.from_object('wwwconfig')

app.secret_key = wwwnh.get_secret_key()

try:
    app.config.from_pyfile('local.cfg')
# pylint:disable=bare-except
except:
    pass
app.config.from_envvar('WWWNETHACK_CONFIG', True)

def dot_dirname(path):
    """Dirname with a dot if empty."""
    name = os.path.dirname(path)

    if name == '':
        return '.'
    else:
        return name

# pylint:disable=invalid-name
asset_map = yaml.load(open(dot_dirname(__file__) + '/assets.map.yaml'))

@app.context_processor
def utility_functions():
    """Functions available in templates."""
    def asset_url(path):
        """Generate a versioned asset url."""
        return asset_map[path]
    return dict(asset_url=asset_url)

@app.template_filter('render_conducts')
def conducts_filter(conducts):
    """ An html rendering of the conducts. """

    if not isinstance(conducts, int):
        return ""

    text = [
        ('F', 'Foodless'),
        ('V', 'Vegetarian'),
        ('V', 'Vegan'),
        ('A', 'Atheist'),
        ('W', 'Weaponless'),
        ('P', 'Pacifist'),
        ('I', 'Illiterate'),
        ('Pp', 'Polypileless'),
        ('Ps', 'Polyselfless'),
        ('W', 'Wishless'),
        ('Wa', 'ArtiWishing'),
        ('G', 'Genocideless'),
    ]

    result = ""
    for i in range(0, 12):
        if conducts & 1:
            result += '''<span
                class="conduct {title}" title={title}>{short}</span>'''.format(
                    short=text[i][0],
                    title=text[i][1])
        conducts >>= 1

    return Markup(result)

@app.template_filter('human_readable')
def human_readable_filter(seconds):
    """The human readable seconds filter or templates."""
    return wwwnh.format_human_readable(seconds)

@app.template_filter('format_time')
def format_time(seconds):
    """Format time in seconds as human readable."""
    return datetime.fromtimestamp(seconds).strftime('%b %-d %Y %-H:%M')

def csrf(handler):
    '''Generate a csrf token for a request.'''
    @functools.wraps(handler)
    def generate_csrf(*args, **kwargs):
        '''Generate the actual csrf.'''
        flask.g.csrf = base64.b64encode(os.urandom(32)).decode('utf-8')

        response = handler(*args, **kwargs)
        response.set_cookie('csrf', flask.g.csrf)

        return response

    return generate_csrf

@app.before_request
def logged_in():
    '''Check if a user is logged in every request.'''
    user = login.validate_session(app.config, flask.session)
    flask.g.user = user

@app.route('/')
def main():
    """Index page."""
    #app.config.update(dict(title='nethack'))
    return render_template('index.html')

@app.route('/static/<path:path>')
def sources(path):
    """Source asset files in dev."""
    return send_from_directory('../static', path)

@app.route('/maps/<path:path>')
def maps(path):
    """Sourcemaps path in dev."""
    return send_from_directory('../.build', path)

@app.route('/users')
def users():
    """Users page"""

    sql = db.sql_connect(app.config, '360')
    cursor = sql.cursor()
    games = cursor.execute("""
      SELECT SUM(games.playing_time) AS total,
        plname,
        COUNT(DISTINCT games.id) AS numgames
      FROM games GROUP BY plname ORDER by plname
    """).fetchall()

    return render_template('users.html', users=games, pagename='Users')

@app.route('/zscores')
def zscores():
    """Zscores page."""

    conn = db.sql_connect(app.config, '360')
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

    return render_template(
        'zscores.html',
        scores=score_list,
        roles=roles,
        pagename='ZScores')

@app.route('/high_scores')
def high_scores():
    """High scores page."""

    scores = db.sql_query(app.config, '360', """
        SELECT *
        FROM games
        WHERE score NOT NULL
        ORDER BY score DESC LIMIT 2000
        """)

    return render_template(
        'high_scores.html',
        scores=scores,
        pagename='High Scores')

def find_user(f):
    ''' Decorator to find a user for user pages. '''
    @functools.wraps(f)
    def decorator(username, *args, **kwargs):
        ''' Find a user page.

        Returns 404 if it could not be found, otherwise calls
        the real user page function.
        '''
        connection = db.connect_users(app.config)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            [username])

        user = cursor.fetchone()

        if user is None:
            return render_template('404.html'), 404
        else:
            return f(user_row=user, *args, **kwargs)

    return decorator

@app.route('/user/<username>')
def user_page(username):
    """The user page."""

    connection = db.connect_users(app.config)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", [username])

    user = cursor.fetchone()

    nh360_conn = db.sql_connect(app.config, '360')
    cursor = nh360_conn.cursor()
    cursor.execute(
        'SELECT COUNT(*) AS games FROM games WHERE plname = ? AND death NOT NULL',
        [username])

    games = cursor.fetchone()['games']

    cursor = nh360_conn.cursor()
    cursor.execute(
        'SELECT COUNT(*) AS asc FROM games WHERE plname = ? AND ascended = 1',
        [username])

    ascended = cursor.fetchone()['asc']

    cursor = nh360_conn.cursor()
    cursor.execute(
        'SELECT MAX(score) AS maximum, SUM(score) as total FROM games where plname = ?',
        [username])

    scores = cursor.fetchone()
    total = scores['total']
    high = scores['maximum']

    nh360 = {
        'ascended': ascended,
        'games': games,
        'high': high,
        'total': total,
    }

    if user is None:
        return render_template('404.html'), 404
    else:
        return render_template(
            'user_page.html',
            userdata=user,
            nh360=nh360,
            pagename=username)

@app.route('/recordings/<username>')
def recordings(username):
    ''' List the recordings of a player.'''
    client = wwwnh.get_recordings_backend(app.config)
    files = client.list_files(username)

    return render_template(
        'player_recordings.html',
        files=files,
        username=username,
        pagename='{}:recordings'.format(username))

@app.route('/user/<username>/config', methods=['GET', 'POST'])
@find_user
@csrf
def user_config(user_row):
    ''' Game configuration.'''

    user = flask.g.user
    kwargs = {}

    if request.method == 'POST':
        if wwwnh.validate_csrf(request.form['csrf']):
            if wwwnh.save_configuration(
                    app.config,
                    request.form['config'],
                    user):
                kwargs['savemessage'] = "Configuration saved successfully"
            else:
                kwargs['savemessage'] = 'Error saving configuration'
        else:
            kwargs['savemessage'] = "Invalid credentials"
    username = user_row['username']
    config_file = open(app.config['GAME_ROOT'] +
                       '/users/' + username + '/nh360config.txt')
    contents = config_file.read()
    return flask.make_response(render_template(
        "user_config.html",
        username=user_row['username'],
        contents=contents,
        **kwargs))

@app.route('/user/<username>/games')
def player_games(username):
    """ List a player's games."""

    scores = db.sql_query(
        app.config,
        '360',
        """
        SELECT *
        FROM games
        WHERE plname = ?
        ORDER BY start_time ASC
        """,
        username)

    return render_template(
        'player_games.html',
        player=username,
        scores=scores)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    '''The login page.'''
    if request.method == 'POST':
        form = request.form
        response = flask.make_response()
        response.status = '302'
        if login.login_user(app.config, form['username'], form['password']):
            response.headers['Location'] = wwwnh.redirect_login()
        else:
            flask.flash('Invalid credentials')
            response.headers['Location'] = url_for('login_page')

        return response

    else:
        return render_template(
            'login.html'
        )

# This endpoint is vulnerable to a csrf attack
# I'm not too worried about that since it just logs you out.
@app.route('/logout')
def logout_handler():
    '''Log a user out.'''
    login.logout(app.config)
    return redirect(url_for('main'))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('ausnethack')
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()

    kwargs = {}

    if args.all:
        kwargs['host'] = '0.0.0.0'

    app.run(debug=True, port=6500, extra_files=['assets.map.yaml'], **kwargs)
