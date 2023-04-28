import re
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, flash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Setzen Sie hier einen geheimen Schlüssel für die Flask-Anwendung

entries = {}
entries_file = 'entries.json'

def load_entries():
    try:
        with open(entries_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_entries(entries):
    with open(entries_file, 'w') as f:
        json.dump(entries, f)

def is_valid_call_sign(call_sign):
    url = 'https://ans.bundesnetzagentur.de/Amateurfunk/Rufzeichen.aspx'
    payload = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        'ctl00$ContentPlaceHolder1$tbxCallsign': call_sign,
        'ctl00$ContentPlaceHolder1$btnSubmit': 'Suchen'
    }

    session = requests.Session()
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extrahiere die benötigten ViewState und EventValidation Felder
    payload['__VIEWSTATE'] = soup.find('input', {'name': '__VIEWSTATE'})['value']
    payload['__VIEWSTATEGENERATOR'] = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    payload['__EVENTVALIDATION'] = soup.find('input', {'name': '__EVENTVALIDATION'})['value']

    response = session.post(url, data=payload)
    soup = BeautifulSoup(response.content, 'html.parser')
    result_table = soup.find('table', {'id': 'ctl00_ContentPlaceHolder1_gvCallSign'})

    return result_table is not None and len(result_table.find_all('tr')) > 1

@app.route('/', methods=['GET', 'POST'])
def index():
    global entries
    entries = load_entries()

    now = datetime.utcnow()

    # Entferne Einträge, die älter als 24 Stunden sind
    entries = {k: v for k, v in entries.items() if now - datetime.fromisoformat(v['timestamp']) < timedelta(hours=24)}

    if request.method == 'POST':
        rufzeichen = request.form['rufzeichen']
        frequenz = format(float(request.form['frequenz']), '.4f')
        betriebsart = request.form['betriebsart']

        if is_valid_call_sign(rufzeichen):
            entries[rufzeichen] = {
                'frequenz': frequenz,
                'betriebsart': betriebsart,
                'timestamp': now.isoformat()
            }
            save_entries(entries)
        else:
            flash('Ungültiges Rufzeichen. Bitte geben Sie ein gültiges Rufzeichen ein.')

    return render_template('index.html', entries=entries, now=now)

if __name__ == '__main__':
    app.run(debug=True)
