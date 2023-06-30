# Amateurfunk-Stationen Tracker

Dieses Projekt ist eine einfache Web-Anwendung, die Amateurfunk-Stationen und ihre aktiven Frequenzen und Betriebsarten erfasst. Nutzer können ihre Amateurfunk-Rufzeichen, ihre Frequenz in MHz und ihre Betriebsart eingeben. Die Anwendung überprüft das Rufzeichen auf Gültigkeit und zeigt dann eine aktualisierte Liste aller aktiven Stationen an.

## Technologien

Dieses Projekt verwendet Python und das Flask-Web-Framework. Die Daten werden in einem in-memory Python-Dictionary gespeichert und auf der Client-Seite mit AJAX aktualisiert. jQuery wird für die AJAX-Anfragen und zum Manipulieren des DOM verwendet. Die Website ist responsiv und kann auf Desktop- und Mobilgeräten verwendet werden.

## Installation

1. Stellen Sie sicher, dass Python und pip auf Ihrem System installiert sind.
2. Klonen Sie dieses Repository und wechseln Sie in das Projektverzeichnis.
3. Installieren Sie die erforderlichen Pakete mit `pip install -r requirements.txt`.
4. Starten Sie den Server mit `python app.py`.

Öffnen Sie Ihren Web-Browser und navigieren Sie zu `http://localhost:8080`, um die Anwendung zu nutzen.

## Verwendung

Geben Sie Ihr Rufzeichen, die Frequenz und die Betriebsart in die entsprechenden Felder ein und klicken Sie auf "Submit". Die Tabelle unten wird aktualisiert und zeigt alle aktiven Stationen an, sortiert nach dem Zeitpunkt des letzten Updates. Die Seite wird alle 30 Sekunden automatisch aktualisiert, um die neuesten Daten anzuzeigen.

## Hinweise

Dieses Projekt dient nur zu Demonstrationszwecken und sollte nicht in einer Produktionsumgebung eingesetzt werden, da es keine persistente Datenbank und keine Authentifizierung bietet. Es überprüft auch nicht die Gültigkeit der eingegebenen Rufzeichen, Frequenzen oder Betriebsarten.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe die `LICENSE`-Datei für Details.
