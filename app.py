from flask import Flask, request, render_template, make_response
import time
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect('database.db')       # Name der SQLite-Datenbank-Datei
        print(sqlite3.version)
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    try:
        sql_create_table = """ CREATE TABLE IF NOT EXISTS qso (
                                            id integer PRIMARY KEY AUTOINCREMENT,
                                            time text NOT NULL,
                                            callsign text NOT NULL,
                                            frequency real NOT NULL
                                        ); """
        if conn is not None:
            c = conn.cursor()
            c.execute(sql_create_table)
    except Error as e:
        print(e)

@app.route("/", methods=['GET', 'POST'])
def index():
    conn = create_connection()
    create_table(conn)
    if request.method == 'POST':
        callsign = request.form.get('callsign')
        frequency = round(float(request.form.get('frequency').replace(",", ".")), 4)
        cur = conn.cursor()
        cur.execute("INSERT INTO qso (time, callsign, frequency) VALUES (?, ?, ?)",
                    (time.strftime("%Y-%m-%d %H:%M:%S"), callsign, frequency))
        conn.commit()
        resp = make_response(render_template('index.html'))
        resp.set_cookie('callsign', callsign)
        return resp
    else:
        callsign = request.cookies.get('callsign')
        return render_template('index.html', callsign=callsign)

@app.route("/data", methods=['GET'])
def data():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM qso ORDER BY time DESC LIMIT 10")
    rows = cur.fetchall()
    return render_template('data.html', rows=rows)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
