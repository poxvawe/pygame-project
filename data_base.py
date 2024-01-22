import sqlite3


def save_score(name, score):
    con = sqlite3.connect("aota2.sqlite")
    cur = con.cursor()
    query = "INSERT INTO players(name, score) VALUES (?, ?);"
    cur.execute(query, (name, str(score)))
    con.commit()
    cur.close()
    con.close()
