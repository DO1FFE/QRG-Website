from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3
import datetime
from datetime import timezone, timedelta
import threading
import time

app = Flask(__name__)
db_path = 'datenbank.db'

def create_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eintraege (
            rufzeichen TEXT PRIMARY KEY,
            frequenz REAL,
            betriebsart TEXT,
            talkgroup TEXT,
            zeitstempel TEXT
        )
    ''')
    conn.commit()
    conn.close()

def convert_to_local_timezone(utc_timestamp):
    local_timezone = timezone(timedelta(hours=2)) # CET (Central European Time)
    return utc_timestamp.replace(tzinfo=timezone.utc).astimezone(local_timezone)

def cleanup_thread():
    while True:
        now = datetime.datetime.utcnow()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM eintraege WHERE strftime('%s', 'now') - strftime('%s', zeitstempel) > 86400")
        conn.commit()
        conn.close()
        time.sleep(60)

threading.Thread(target=cleanup_thread, daemon=True).start()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        rufzeichen = request.form.get('rufzeichen', '')
        frequenz = request.form.get('frequenz')
        betriebsart = request.form.get('betriebsart')
        talkgroup = request.form.get('talkgroup')

        if frequenz:
            frequenz = frequenz.replace(',', '.')
            frequenz = round(float(frequenz), 4)
        else:
            frequenz = 0

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO eintraege (rufzeichen, frequenz, betriebsart, talkgroup, zeitstempel)
            VALUES (?, ?, ?, ?, ?)
        ''', (rufzeichen, frequenz, betriebsart, talkgroup, datetime.datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()

        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('rufzeichen', rufzeichen)
        resp.set_cookie('frequenz', str(frequenz))
        resp.set_cookie('betriebsart', betriebsart)
        return resp

    rufzeichen = request.cookies.get('rufzeichen', '')
    frequenz = request.cookies.get('frequenz', '')
    betriebsart = request.cookies.get('betriebsart', '')

    return render_template('index.html', rufzeichen=rufzeichen, frequenz=frequenz, betriebsart=betriebsart)

@app.route('/data')
def data():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eintraege")
    rows = cursor.fetchall()
    conn.close()

    new_entries = []
    old_entries = []
    for row in rows:
        rufzeichen, frequenz, betriebsart, talkgroup, zeitstempel = row
        utc_timestamp = datetime.datetime.fromisoformat(zeitstempel)
        local_timestamp = convert_to_local_timezone(utc_timestamp).isoformat()
        entry = {
            'rufzeichen': rufzeichen,
            'frequenz': frequenz,
            'betriebsart': betriebsart,
            'talkgroup': talkgroup,
            'zeitstempel': local_timestamp,
        }
        time_difference = (datetime.datetime.utcnow() - utc_timestamp).total_seconds()
        if time_difference < 600: # Less than 10 minutes
            new_entries.append(entry)
        else:
            old_entries.append(entry)

    return {'new_entries': new_entries, 'old_entries': old_entries}

if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=8080, debug=True)
