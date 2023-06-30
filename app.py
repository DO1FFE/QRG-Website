from flask import Flask, request, render_template, make_response, redirect, url_for, jsonify
import json
import threading
import datetime
from datetime import timedelta
import time
from requests import get

app = Flask(__name__)
db = {}

def cleanup_thread():
    while True:
        now = datetime.datetime.utcnow()
        to_delete = [callsign for callsign, data in db.items() if now - data['timestamp'] > timedelta(hours=24)]
        for callsign in to_delete:
            del db[callsign]
        time.sleep(60)

cleanup_thread = threading.Thread(target=cleanup_thread)
cleanup_thread.start()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        callsign = request.form.get('callsign')
        frequency = round(float(request.form.get('frequency')), 4)
        mode = request.form.get('mode')

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

@app.route('/data', methods=['GET'])
def data():
    return jsonify(db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
