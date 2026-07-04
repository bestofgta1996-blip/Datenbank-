@echo off
REM Einmaliger Rundum-Start fuer Windows: richtet alles ein und startet
REM die Weboberflaeche. Danach im Browser http://localhost:5000 oeffnen.
REM
REM Aufruf: Doppelklick auf diese Datei, oder in der Eingabeaufforderung:
REM   start.bat

cd /d %~dp0

if not exist ".venv" (
    echo Erstelle virtuelle Umgebung ^(nur beim ersten Mal^)...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installiere Abhaengigkeiten ^(nur beim ersten Mal notwendig^)...
pip install -q -r requirements.txt

echo Baue/aktualisiere den Such-Index aus knowledge\raw\ ...
python src\ingest.py

echo.
echo Starte Weboberflaeche: http://localhost:5000
echo Vom Handy im gleichen WLAN: siehe README.md, Abschnitt 6.
echo Zum Beenden: Strg+C
echo.
python src\webapp.py
