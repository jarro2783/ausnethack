from flask import Flask, render_template
import sqlite3
import wwwnethack as wwwnh

app = Flask(__name__)
app.config.from_object("wwwconfig")
#app.config.servername = "AusNethack"

def sql_connect(game):
    conn = sqlite3.connect(app.config['NETHACKDB'][game])
    conn.row_factory = sqlite3.Row
    return conn

def sql_query(game, query):
    conn = sql_connect(game)
    cursor = conn.cursor()
    return cursor.execute(query).fetchall()

@app.route('/')
def main():
    #app.config.update(dict(title="nethack"))
    return render_template("index.html")

@app.route("/users")
def users():
    sql = sql_connect("360")
    c = sql.cursor()
    games = c.execute("""
      SELECT SUM(sessions.end_time - sessions.start_time) AS total,
        plname,
        COUNT(DISTINCT games.id) AS numgames
      FROM games JOIN sessions ON games.id = sessions.game GROUP BY plname
    """
    ).fetchall()

    app.config.pagename = "Users"
    return render_template("users.html", users = games)

def calculate_z(n):
    factor = 1.0
    z = 0
    i = 0
    while i < n:
        z += factor
        i += 1
        factor /= 2

    return z

@app.route("/zscores")
def zscores():
    conn = sql_connect("360")
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT plname, COUNT(ascended) AS number, role FROM games
        WHERE ascended = 1
        GROUP BY plname, role
    """).fetchall()

    scores = {}
    roles = {}

    for r in rows:
        plname = r['plname']
        role = r['role']
        roles[role] = 0
        if plname not in scores:
            scores[plname] = {'roles' : {}, 'total' : 0}
        zscore = calculate_z(r['number'])
        scores[plname]["total"] += zscore
        scores[plname]['roles'][role] = zscore

    score_list = []

    for player in sorted(scores.keys(), reverse=True):
        score_list.append(wwwnh.ZScore(player, scores[player]))

    return render_template("zscores.html", scores = score_list,
      roles = sorted(roles.keys()))

@app.route("/high_scores")
def high_scores():
    scores = sql_query("360",
      """
      SELECT games.*,
        sum(sessions.end_time - sessions.start_time) AS total_time
      FROM games JOIN sessions ON sessions.game = games.id
      WHERE score NOT NULL
      GROUP BY games.id
      ORDER BY score DESC LIMIT 2000
      """
    )

    return render_template("high_scores.html", scores = scores)

if __name__ == "__main__":
    app.run(debug=True)
