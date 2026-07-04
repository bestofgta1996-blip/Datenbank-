"""
Zentrale Konfiguration für das medizinische Literatur-RAG-System.

Alle wichtigen Einstellungen stehen hier an EINEM Ort. Wenn du z.B. später
ein besseres, medizinisches Embedding-Modell nutzen willst, änderst du nur
EMBEDDING_MODEL weiter unten – der restliche Code muss nicht angefasst werden.
"""

from pathlib import Path

# Basisverzeichnis des Projekts (der Ordner "medical-literature-rag/")
BASE_DIR = Path(__file__).resolve().parent.parent

# Hier legst du deine Rohdateien ab (PDF, TXT, Markdown, EPUB)
RAW_DIR = BASE_DIR / "knowledge" / "raw"

# Hier merkt sich das System, welche Dateien schon verarbeitet wurden
# (Manifest-Datei mit Datei-Hashes), damit nichts doppelt verarbeitet wird
PROCESSED_DIR = BASE_DIR / "knowledge" / "processed"

# Hier legt ChromaDB seine lokale Vektordatenbank ab
INDEX_DIR = BASE_DIR / "knowledge" / "index"

# Name der Sammlung ("Tabelle") innerhalb von ChromaDB
COLLECTION_NAME = "medical_literature"

# Embedding-Modell für sentence-transformers.
# Standard: kleines, schnelles Allzweck-Modell, läuft gut auf einem normalen
# Rechner ganz ohne Grafikkarte (CPU).
#
# Später kannst du hier z.B. ein medizinisches Modell eintragen, etwa:
#   "pritamdeka/S-PubMedBert-MS-MARCO"
# Der Wechsel erfordert KEINE Änderung an ingest.py oder search.py – du musst
# nur den Index einmal neu bauen (siehe README.md), weil sich die
# Embeddings mit einem anderen Modell ändern.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking-Einstellungen (in Wörtern, nicht Zeichen)
CHUNK_SIZE = 1000       # Zielgröße eines Chunks (Vorgabe: ca. 800-1200 Wörter)
CHUNK_OVERLAP = 150     # Überlappung zwischen zwei aufeinanderfolgenden Chunks

# Wie viele Treffer eine Suche standardmäßig zurückgibt, wenn --top-k nicht
# angegeben wird
DEFAULT_TOP_K = 8

# Welche Dateiendungen werden beim Ingest berücksichtigt?
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".epub"}
