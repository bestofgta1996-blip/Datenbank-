# Anweisungen für Claude Code: Medical Literature RAG

Dieses Projekt ist eine lokale, durchsuchbare Wissensdatenbank für
medizinische Literatur (Bücher, Leitlinien, Studien). Claude Code soll sie
gezielt nutzen, statt sich auf reines Vorwissen zu verlassen oder ganze
Bücher in den Chat kopieren zu lassen.

## Regel 1: Vor medizinischen/fachlichen Antworten immer zuerst lokal suchen

Bei medizinischen, gutachterlichen oder sonst fachlich anspruchsvollen
Fragen IMMER zuerst die lokale Literaturdatenbank durchsuchen, bevor eine
inhaltliche Antwort gegeben wird:

```
python src/search.py "<Suchfrage>" --top-k 8
```

- Formuliere die Suchfrage möglichst konkret und mit den wichtigsten
  Fachbegriffen (siehe `examples/example_queries.md`).
- Nutze bei Bedarf `--top-k` höher (z.B. 10-15) für breitere Themen oder
  `--source <datei>`, um gezielt in einer bestimmten Quelle zu suchen.

## Regel 2: Treffer als Quellenbasis nutzen

- Stütze die Antwort auf die zurückgegebenen Textausschnitte (Datei, Seite,
  Ausschnitt, Score).
- Zitiere/nenne die Quelle (Dateiname + Seite), auf die sich eine Aussage
  stützt.
- **Keine Diagnose erfinden.** Wenn die Literatur eine Aussage nicht
  hergibt, das offen so sagen (siehe Regel 4).

## Regel 3: Immer zwischen Evidenzgraden unterscheiden

Bei jeder inhaltlichen Aussage transparent machen, auf welcher Basis sie
steht:

- **Gesicherte Evidenz** - klar durch die gefundenen Quellen belegt.
- **Mögliche Hypothese** - plausibel, aber nicht eindeutig durch die
  gefundenen Quellen belegt.
- **Unklare Datenlage** - die Literatur äußert sich widersprüchlich oder
  unvollständig dazu.
- **Reine Spekulation** - keine Basis in der lokalen Literatur, ausdrücklich
  als solche kennzeichnen.

## Regel 4: Wenn keine ausreichenden Quellen gefunden werden

Offen sagen, dass die lokale Literatursuche nichts Belastbares geliefert
hat - nicht durch allgemeines Sprachmodell-Wissen kaschieren, ohne das
kenntlich zu machen.

## Regel 5: Bei konkreten Beschwerden auf ärztliche Abklärung verweisen

Geht es um konkrete gesundheitliche Beschwerden (z.B. eines Patienten oder
des Nutzers selbst), immer darauf hinweisen, dass eine ärztliche
Untersuchung/Abklärung nötig ist. Dieses System ersetzt keine Diagnose.

## Regel 6: Datenschutz und Datensparsamkeit

- Keine sensiblen Patientendaten unnötig in Logs schreiben.
- Keine medizinischen Diagnosen, Patientennamen oder sonstigen
  Gesundheitsdaten an externe Dienste senden. Die Suche
  (`src/search.py`) läuft lokal; das muss so bleiben.
- Keine echten Patientendaten in `knowledge/raw/` ablegen bzw. indexieren
  lassen.
- Literatur darf nur indexiert werden, wenn Nutzungsrechte/Zugriff darauf
  bestehen.

## Regel 7: Bei Coding-Aufgaben an diesem Projekt

Vor Änderungen am Code zuerst `README.md` (und, falls vorhanden,
`docs/Architekturhinweise.md`) lesen, um Aufbau und Konventionen des
Projekts zu verstehen, bevor `ingest.py`, `search.py`, `utils.py` oder
`config.py` geändert werden.
