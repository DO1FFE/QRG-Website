from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3
import datetime
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
            zeitstempel TEXT
        )
    ''')
    conn.commit()
    conn.close()

def cleanup_thread():
    while True:
        now = datetime.datetime.utcnow()

        # Entfernen Sie Einträge, die älter als 10 Minuten sind
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM eintraege WHERE strftime('%s', 'now') - strftime('%s', zeitstempel) > 600")
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

        if frequenz:
            frequenz = frequenz.replace(',', '.')
            frequenz = round(float(frequenz), 4)
        else:
            frequenz = 0

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO eintraege (rufzeichen, frequenz, betriebsart, zeitstempel)
            VALUES (?, ?, ?, ?)
        ''', (rufzeichen, frequenz, betriebsart, datetime.datetime.utcnow().isoformat()))
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

    data = []
    for row in rows:
        rufzeichen, frequenz, betriebsart, zeitstempel = row
        entry = {
            'rufzeichen': rufzeichen,
            'frequenz': frequenz,
            'betriebsart': betriebsart,
            'zeitstempel': zeitstempel,
        }
        data.append(entry)

    return {'data': data}

if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=8080, debug=True)
