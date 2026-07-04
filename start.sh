#!/bin/bash
# Einmaliger Rundum-Start für Mac/Linux: richtet alles ein und startet
# die Weboberfläche. Danach im Browser http://localhost:5000 öffnen.
#
# Aufruf:
#   bash start.sh
set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Erstelle virtuelle Umgebung (nur beim ersten Mal)..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installiere Abhängigkeiten (nur beim ersten Mal notwendig, kann etwas dauern)..."
pip install -q -r requirements.txt

echo "Baue/aktualisiere den Such-Index aus knowledge/raw/ ..."
python src/ingest.py

echo ""
echo "Starte Weboberfläche: http://localhost:5000"
echo "Vom Handy im gleichen WLAN: siehe README.md, Abschnitt 6."
echo "Zum Beenden: Strg+C"
echo ""
python src/webapp.py
