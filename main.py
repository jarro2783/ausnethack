from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
app.config.from_object("wwwconfig")
#app.config.servername = "AusNethack"

@app.route('/')
def main():
    #app.config.update(dict(title="nethack"))
    return render_template("index.html")

@app.route("/users")
def users():
    sql = sqlite3.connect(app.config['NETHACKDB']['360'])
    sql.row_factory = sqlite3.Row
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

if __name__ == "__main__":
    app.run(debug=True)
