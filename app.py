from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime
import sqlite3
from contextlib import closing
import threading
import time

DATABASE = 'datenbank.db'

app = Flask(__name__)

def connect_db():
    return sqlite3.connect(DATABASE)

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_first_request
def initialize_database():
    init_db()

def cleanup_thread():
    while True:
        now = datetime.utcnow()
        with closing(connect_db()) as db:
            db.execute("DELETE FROM entries WHERE strftime('%s', 'now') - strftime('%s', timestamp) > 600")
            db.commit()
        time.sleep(60)

threading.Thread(target=cleanup_thread, daemon=True).start()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        rufzeichen = request.form.get('rufzeichen', '')
        frequenz = request.form.get('frequenz', '')
        betriebsart = request.form.get('betriebsart', '')

        if frequenz:
            frequenz = frequenz.replace(',', '.')
            frequenz = round(float(frequenz), 4)
        else:
            frequenz = 0

        with closing(connect_db()) as db:
            db.execute("INSERT INTO entries (rufzeichen, frequenz, betriebsart, timestamp) VALUES (?, ?, ?, ?)",
                       (rufzeichen, frequenz, betriebsart, datetime.utcnow()))
            db.commit()

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
    with closing(connect_db()) as db:
        cursor = db.execute("SELECT rufzeichen, frequenz, betriebsart, timestamp FROM entries")
        entries = cursor.fetchall()
        data = []
        for entry in entries:
            rufzeichen, frequenz, betriebsart, timestamp = entry
            minutes_ago = int((datetime.utcnow() - datetime.fromisoformat(timestamp)).total_seconds() / 60)
            data.append({
                'rufzeichen': rufzeichen,
                'frequenz': frequenz,
                'betriebsart': betriebsart,
                'timestamp': timestamp,
                'minutes_ago': minutes_ago,
            })
        return {'data': data}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
