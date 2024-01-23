import sqlite3


def save_score(name, score):
    con = sqlite3.connect("aota2.sqlite")
    cur = con.cursor()
    query = "INSERT INTO players(name, score) VALUES (?, ?);"
    cur.execute(query, (name, int(score)))
    con.commit()
    cur.close()
    con.close()


def score_from_bd():
    con = sqlite3.connect("aota2.sqlite")
    cur = con.cursor()
    query = "SELECT name, score FROM players ORDER BY score DESC;"
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    con.close()
    return data
