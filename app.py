import datetime
import time
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template, make_response, jsonify

app = Flask(__name__)
stations = {}

def validate_callsign(callsign):
    url = f"https://ans.bundesnetzagentur.de/Amateurfunk/Rufzeichen.aspx"
    payload = {'Rufzeichen': callsign}
    response = requests.get(url, params=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    return bool(soup.find('span', text=callsign))

def cleanup_thread():
    while True:
        current_time = datetime.datetime.utcnow()
        keys_to_delete = [key for key, value in stations.items() if (current_time - value['timestamp']).total_seconds() > 24*60*60]
        for key in keys_to_delete:
            del stations[key]
        time.sleep(60)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        callsign = request.form.get('callsign')
        frequency = round(float(request.form.get('frequency')), 4)
        mode = request.form.get('mode')
        if validate_callsign(callsign):
            stations[callsign] = {
                'frequency': frequency,
                'mode': mode,
                'timestamp': datetime.datetime.utcnow()
            }
        resp = make_response(render_template('index.html', stations=stations))
        resp.set_cookie('callsign', callsign)
        resp.set_cookie('frequency', str(frequency))
        resp.set_cookie('mode', mode)
        return resp
    else:
        callsign = request.cookies.get('callsign')
        frequency = request.cookies.get('frequency')
        mode = request.cookies.get('mode')
        return render_template('index.html', stations=stations, callsign=callsign, frequency=frequency, mode=mode)

@app.route('/update', methods=['GET'])
def update():
    return jsonify(stations)

if __name__ == '__main__':
    cleanup = threading.Thread(target=cleanup_thread)
    cleanup.start()
    app.run(port=8080)
