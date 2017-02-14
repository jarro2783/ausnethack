'''Login functions for wwwnethack.'''

import base64
import bcrypt
import flask
import os
import time

from . import db

def login_user(config, username, password):
    '''Logs a user in.'''

    session = flask.session

    connection = db.connect_users(config)
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ?', [username])
    user = cursor.fetchone()

    if user is not None:
        hashed = bcrypt.hashpw(password.encode('utf-8'), user['password'])

        if hashed == user['password']:

            session_id = base64.b16encode(os.urandom(64))

            session['session'] = session_id
            session['id'] = user['id']
            session['expiry'] = time.time()
            session['username'] = username

            cursor.execute(
                'INSERT INTO sessions (id, userid) VALUES (?, ?)',
                [
                    session_id,
                    user['id'],
                ])
            connection.commit()

            session.permanent = True
            return True

    return False

def logout(config):
    '''Log a user out.'''
    session = flask.session

    connection = db.connect_users(config)
    cursor = connection.cursor()

    cursor.execute('DELETE FROM sessions WHERE id = ?',
                   [session['session']])
    connection.commit()

    session.clear()

def select_user(config, session):
    '''Find a user's login session.'''
    connection = db.connect_users(config)
    cursor = connection.cursor()
    cursor.execute(
        '''
        SELECT * FROM sessions JOIN users ON users.id = sessions.userid
        WHERE sessions.id = ?
        ''',
        [session])

    return cursor.fetchone()

def validate_session(config, session):
    '''Revalidates a user's session in the database.'''
    # revalidate a session every ten minutes
    user = None
    now = time.time()
    if 'expiry' in session and now - session['expiry'] < 10 * 60:
        user = {'username' : session['username']}
    elif 'session' in session:
        row = select_user(config, session['session'])
        if row is None or row['userid'] != session['id']:
            session.clear()
        else:
            session['expiry'] = now
            user = {
                'username': row['username']
            }

    return user
