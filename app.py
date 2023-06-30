from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3
import datetime
import threading
import time

app = Flask(__name__)
db = sqlite3.connect('datenbank.db', check_same_thread=False)

def create_table():
    db.execute('''CREATE TABLE IF NOT EXISTS eintraege (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rufzeichen TEXT NOT NULL,
                    frequenz REAL NOT NULL,
                    betriebsart TEXT NOT NULL,
                    zeitstempel TEXT NOT NULL)''')
    db.commit()

def cleanup_thread():
    while True:
        now = datetime.datetime.utcnow()
        db.execute("DELETE FROM eintraege WHERE strftime('%s', 'now') - strftime('%s', zeitstempel) > 600")
        db.commit()
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

        zeitstempel = datetime.datetime.utcnow().isoformat()

        db.execute("INSERT INTO eintraege (rufzeichen, frequenz, betriebsart, zeitstempel) VALUES (?, ?, ?, ?)",
                   (rufzeichen, frequenz, betriebsart, zeitstempel))
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
    cursor = db.execute("SELECT * FROM eintraege ORDER BY zeitstempel DESC")
    rows = cursor.fetchall()
    cursor.close()

    data = []
    for row in rows:
        eintrag = {
            'rufzeichen': row[1],
            'frequenz': row[2],
            'betriebsart': row[3],
            'zeitstempel': row[4],
            'minuten_seit_eintrag': berechne_minuten_seit_eintrag(row[4])
        }
        data.append(eintrag)

    return {'data': data}

def berechne_minuten_seit_eintrag(zeitstempel):
    now = datetime.datetime.utcnow()
    eintrag_zeit = datetime.datetime.fromisoformat(zeitstempel)
    delta = now - eintrag_zeit
    minuten = delta.total_seconds() // 60

    if minuten < 60:
        return f'{int(minuten)} Minuten'
    else:
        stunden = minuten // 60
        minuten %= 60
        return f'{int(stunden)} Stunden, {int(minuten)} Minuten'

if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=8080, debug=True)
