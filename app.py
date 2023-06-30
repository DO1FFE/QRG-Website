from flask import Flask, render_template, request, redirect, url_for, make_response
import shelve
import datetime
import threading
import time

app = Flask(__name__)
db = shelve.open('database.db', writeback=True)

def cleanup_thread():
    while True:
        now = datetime.datetime.utcnow()

        for key in list(db.keys()):
            if (now - db[key]['timestamp']).total_seconds() > 600:
                del db[key]

        time.sleep(60)

threading.Thread(target=cleanup_thread, daemon=True).start()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        callsign = request.form.get('callsign', '')
        frequency = request.form.get('frequency')
        mode = request.form.get('mode')

        if frequency:
            frequency = frequency.replace(',', '.')
            frequency = round(float(frequency), 4)
        else:
            frequency = 0

        resp = make_response(redirect(url_for('index')))

        db[callsign] = {
            'callsign': callsign,
            'frequency': frequency,
            'mode': mode,
            'timestamp': datetime.datetime.utcnow(),
        }

        resp.set_cookie('callsign', callsign)
        resp.set_cookie('frequency', str(frequency))
        resp.set_cookie('mode', mode)

        return resp

    callsign = request.cookies.get('callsign', '')
    frequency = request.cookies.get('frequency', '')
    mode = request.cookies.get('mode', '')

    return render_template('index.html', callsign=callsign, frequency=frequency, mode=mode)

@app.route('/data')
def data():
    return {
        'data': [
            {
                'callsign': entry['callsign'],
                'frequency': entry['frequency'],
                'mode': entry['mode'],
                'timestamp': entry['timestamp'].isoformat() + 'Z',
            }
            for entry in db.values()
        ]
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
