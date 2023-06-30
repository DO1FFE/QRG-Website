from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3
import datetime
import threading
import time

app = Flask(__name__)
app.config['DATABASE'] = 'datenbank.db'

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    db = getattr(app, '_database', None)
    if db is not None:
        db.close()

def cleanup_thread():
    while True:
        now = datetime.datetime.utcnow()

        db = get_db()
        db.execute("DELETE FROM entries WHERE strftime('%s', 'now') - strftime('%s', timestamp) > 600")
        db.commit()

        time.sleep(60)

threading.Thread(target=cleanup_thread, daemon=True).start()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        callsign = request.form.get('rufzeichen', '')
        frequency = request.form.get('frequenz')
        mode = request.form.get('betriebsart')

        if frequency:
            frequency = frequency.replace(',', '.')
            frequency = round(float(frequency), 4)
        else:
            frequency = 0

        db = get_db()
        db.execute("INSERT INTO entries (rufzeichen, frequenz, betriebsart, timestamp) VALUES (?, ?, ?, ?)",
                   (callsign, frequency, mode, datetime.datetime.utcnow()))
        db.commit()

        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('rufzeichen', callsign)
        resp.set_cookie('frequenz', str(frequency))
        resp.set_cookie('betriebsart', mode)

        return resp

    callsign = request.cookies.get('rufzeichen', '')
    frequency = request.cookies.get('frequenz', '')
    mode = request.cookies.get('betriebsart', '')

    db = get_db()
    rows = db.execute("SELECT * FROM entries ORDER BY timestamp DESC").fetchall()

    return render_template('index.html', rufzeichen=callsign, frequenz=frequency, betriebsart=mode, rows=rows)

@app.route('/data')
def data():
    db = get_db()
    rows = db.execute("SELECT * FROM entries ORDER BY timestamp DESC").fetchall()

    data = [
        {
            'rufzeichen': row['rufzeichen'],
            'frequenz': row['frequenz'],
            'betriebsart': row['betriebsart'],
            'timestamp': row['timestamp'].isoformat() + 'Z',
            'minutes_ago': int((datetime.datetime.utcnow() - row['timestamp']).total_seconds() // 60)
        }
        for row in rows
    ]

    return {'data': data}

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=True)
