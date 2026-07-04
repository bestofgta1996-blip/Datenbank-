# Beispiel-Suchanfragen

Diese Datei zeigt, wie man das System per Kommandozeile befragt. Alle
Befehle werden aus dem Ordner `medical-literature-rag/` heraus ausgeführt.

## Einfache Suche

```
python src/search.py "Welche Ursachen können einseitige Schluckbeschwerden haben?"
```

## Mehr Treffer anfordern (Standard: 8, siehe config.py)

```
python src/search.py "Zusammenhang zwischen Nikotin Rauchen einseitigen Halsschmerzen Kehlkopf Dysphagie" --top-k 10
```

## Nur in einer bestimmten Datei suchen

```
python src/search.py "Nebenwirkungen von ACE-Hemmern" --source leitlinie_bluthochdruck.pdf
```

Der Wert von `--source` ist der Dateiname (bzw. relative Pfad), so wie die
Datei unter `knowledge/raw/` liegt.

## Ausgabe als JSON (z.B. zur Weiterverarbeitung durch andere Programme)

```
python src/search.py "Diagnosekriterien Migräne" --json
```
