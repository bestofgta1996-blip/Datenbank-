# Medical Literature RAG

Eine einfache, lokale Wissensdatenbank für medizinische Literatur (Bücher,
Leitlinien, Studien, PDFs, Textdateien, EPUBs). Du legst Dateien in einen
Ordner, das System macht sie durchsuchbar - und du kannst per
Kommandozeile gezielt Textstellen dazu finden, statt ganze Bücher in einen
Chat zu kopieren.

**Wichtiger Hinweis:** Dieses System ist eine **Literatur-Suchhilfe**, keine
Diagnosemaschine. Es findet Textstellen aus deiner eigenen Literatur - es
stellt keine Diagnosen und ersetzt keine ärztliche Abklärung.

---

## 1. Virtuelle Umgebung erstellen

Im Hauptverzeichnis dieses Repos:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

## 2. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

Das installiert u.a. ChromaDB (lokale Vektordatenbank), sentence-transformers
(lokale Embeddings) und PyMuPDF (PDF-Text-Extraktion). Alles läuft komplett
lokal auf deinem Rechner - es werden keine Dateien oder Inhalte an externe
Dienste geschickt.

Beim ersten Ingest-Lauf lädt sentence-transformers einmalig das
Embedding-Modell herunter (ca. 90 MB), danach läuft alles offline.

## 3. Dateien ablegen

Lege deine Dateien (PDF, TXT, Markdown, optional EPUB) in:

```
knowledge/raw/
```

Unterordner sind erlaubt, z.B. `knowledge/raw/leitlinien/`,
`knowledge/raw/lehrbuecher/` - das System durchsucht den Ordner rekursiv.

## 4. Index bauen

```bash
python src/ingest.py
```

Das Skript:
- liest alle Dateien in `knowledge/raw/` ein,
- zerlegt den Text in Chunks (ca. 800-1200 Wörter, mit Überlappung),
- erstellt lokale Embeddings,
- speichert alles in der lokalen ChromaDB-Datenbank unter `knowledge/index/`.

Dateien, die sich seit dem letzten Lauf nicht verändert haben, werden
automatisch übersprungen (erkannt am Datei-Hash). Ein Fehler bei einer
einzelnen Datei bricht den gesamten Lauf nicht ab, sondern wird nur
protokolliert.

## 5. Suche ausführen

```bash
python src/search.py "Welche Ursachen können einseitige Schluckbeschwerden haben?"
```

Optionen:

```bash
python src/search.py "Suchfrage" --top-k 10          # Anzahl Treffer
python src/search.py "Suchfrage" --source datei.pdf  # nur in einer Datei suchen
python src/search.py "Suchfrage" --json              # Ausgabe als JSON
```

Weitere Beispiele in [`examples/example_queries.md`](examples/example_queries.md).

## 6. Neue Dateien ergänzen

Einfach weitere Dateien in `knowledge/raw/` legen und erneut ausführen:

```bash
python src/ingest.py
```

Bereits verarbeitete, unveränderte Dateien werden übersprungen - es werden
nur die neuen bzw. geänderten Dateien verarbeitet.

## 7. Index komplett neu bauen

Falls du z.B. das Embedding-Modell in `src/config.py` (`EMBEDDING_MODEL`)
wechselst, musst du den Index neu bauen, da sich die Embeddings ändern:

```bash
rm -rf knowledge/index
rm -f knowledge/processed/manifest.json
python src/ingest.py
```

## 8. Wichtiger Hinweis

Dieses System ist **keine Diagnosemaschine**, sondern eine Hilfe, um in
deiner eigenen Literatur gezielt Textstellen zu finden. Bei konkreten
gesundheitlichen Beschwerden ersetzt es keine ärztliche Untersuchung oder
Abklärung.

Bitte nimm keine echten Patientendaten in die Literaturdatenbank auf und
schreibe keine personenbezogenen Gesundheitsdaten in Logs. Literatur darf
nur indexiert werden, wenn du die entsprechenden Nutzungsrechte hast.

---

## Projektstruktur

```
.
├─ CLAUDE.md              Anweisungen für Claude Code
├─ README.md              diese Datei
├─ requirements.txt
├─ knowledge/
│  ├─ raw/                deine Rohdateien (PDF, TXT, MD, EPUB)
│  ├─ processed/          Manifest mit bereits verarbeiteten Datei-Hashes
│  └─ index/              lokale ChromaDB-Datenbank
├─ src/
│  ├─ ingest.py           liest Dateien ein, chunked, erstellt Embeddings
│  ├─ search.py           Kommandozeilen-Suche
│  ├─ utils.py            Hilfsfunktionen (Hash, Chunking, Logging, ...)
│  └─ config.py           zentrale Einstellungen
└─ examples/
   └─ example_queries.md  Beispiel-Suchanfragen
```

## Wie Claude Code das System nutzt

Claude Code liest `CLAUDE.md` in diesem Ordner und ruft bei medizinischen
oder fachlichen Fragen automatisch `python src/search.py "..." --top-k 8`
im Terminal auf, statt dass du ganze Bücher in den Chat kopieren musst.

---

## Roadmap (spätere, mögliche Erweiterungen - nicht Teil des MVP)

- Einfache Weboberfläche statt Kommandozeile
- MCP-Anbindung, damit Claude direkt (ohne Terminal-Aufruf) suchen kann
- Automatischer Importer für PubMed/Leitlinien-Datenbanken
- Wechsel auf ein medizinisches Embedding-Modell (z.B. PubMedBERT-basiert)
- Re-Ranking der Suchergebnisse für noch relevantere Treffer
- Quellenbewertung nach Evidenzgrad (z.B. Leitlinie vs. Einzelstudie)
- PDF-OCR für gescannte (nicht durchsuchbare) Bücher
