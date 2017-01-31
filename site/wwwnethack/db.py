import sqlite3

def sql_connect(config, game):
    """ Connect to the nethack sqlite database."""

    conn = sqlite3.connect(config['NETHACKDB'][game])
    conn.row_factory = sqlite3.Row
    return conn

def sql_query(config, game, query, *args):
    """ Run a query on the database."""

    conn = sql_connect(config, game)
    cursor = conn.cursor()
    return cursor.execute(query, args).fetchall()

def connect_users(config):
    """ Connect to the gamelaunch users database."""

    conn = sqlite3.connect(config['GAMELAUNCHDB'])
    conn.row_factory = sqlite3.Row
    return conn


