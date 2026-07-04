"""
Hilfsfunktionen, die sowohl von ingest.py als auch von search.py genutzt werden.

Alles hier ist bewusst einfach gehalten (keine externen Logging-Frameworks
o.ä.), damit auch als Einsteiger leicht nachvollziehbar bleibt, was passiert.
"""

import hashlib
import re
import sys
from datetime import datetime, timezone

import config


def compute_file_hash(file_path) -> str:
    """Berechnet einen SHA-256-Hash über den Dateiinhalt.

    Damit erkennt ingest.py, ob sich eine Datei seit dem letzten Lauf
    geändert hat: gleicher Hash = Datei unverändert = wird übersprungen.
    Anderer Hash = Datei neu oder geändert = wird (neu) verarbeitet.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            sha256.update(block)
    return sha256.hexdigest()


def clean_text(text: str) -> str:
    """Bereinigt extrahierten Text von typischen Extraktions-Artefakten.

    - Null-Bytes entfernen (kommen manchmal aus PDFs)
    - mehrfache Leerzeichen zu einem zusammenfassen
    - mehr als zwei Leerzeilen hintereinander auf zwei reduzieren
    """
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_indices(word_count: int, chunk_size: int, overlap: int):
    """Berechnet Start-/End-Indizes für überlappende Chunks über eine
    Liste von Wörtern, ohne die Wörter selbst zu kennen.

    Wird sowohl für einfachen Text (chunk_text) als auch für PDFs genutzt,
    bei denen wir zusätzlich wissen müssen, von welcher Seite jedes Wort
    stammt (siehe ingest.py).
    """
    if word_count <= 0:
        return []

    # step = wie viele Wörter zwischen zwei Chunk-Starts liegen.
    # Ist kleiner als chunk_size, weil sich Chunks überlappen sollen.
    step = max(chunk_size - overlap, 1)

    indices = []
    start = 0
    while start < word_count:
        end = min(start + chunk_size, word_count)
        indices.append((start, end))
        if end >= word_count:
            break
        start += step

    return indices


def chunk_text(text: str, chunk_size: int, overlap: int):
    """Zerlegt einen Text in überlappende Wort-Chunks (Liste von Strings)."""
    words = text.split()
    return [
        " ".join(words[start:end])
        for start, end in chunk_indices(len(words), chunk_size, overlap)
    ]


def build_metadata(source_file, file_type, document_hash, chunk_index, page_number=None):
    """Erstellt das Metadaten-Dictionary für einen einzelnen Chunk.

    ChromaDB akzeptiert in Metadaten nur einfache Typen (str, int, float,
    bool) und kein None. Deshalb wird eine fehlende Seitenzahl als -1
    gespeichert statt als None.
    """
    return {
        "source_file": source_file,
        "file_type": file_type,
        "page_number": page_number if page_number is not None else -1,
        "chunk_index": chunk_index,
        "document_hash": document_hash,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def log(message: str, level: str = "INFO"):
    """Einfache Konsolen-Log-Funktion.

    Bewusst kein Logging-Framework, damit der Ablauf für Einsteiger leicht
    lesbar bleibt. WICHTIG: Hier dürfen keine Patienten- oder sonstigen
    Gesundheitsdaten hineingeschrieben werden, nur technische Statusmeldungen
    (Dateinamen, Fehlermeldungen, Zähler).
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    stream = sys.stderr if level == "ERROR" else sys.stdout
    print(f"[{timestamp}] {level}: {message}", file=stream)


def get_collection():
    """Öffnet (oder erstellt) die lokale ChromaDB-Sammlung mit dem in
    config.py festgelegten Embedding-Modell.

    Diese Funktion wird sowohl von ingest.py als auch von search.py genutzt,
    damit garantiert immer dasselbe Modell und dieselbe Datenbank verwendet
    werden. Willst du das Embedding-Modell wechseln, änderst du nur
    config.EMBEDDING_MODEL – hier ändert sich nichts.
    """
    import chromadb
    from chromadb.utils import embedding_functions

    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=config.EMBEDDING_MODEL
    )

    client = chromadb.PersistentClient(path=str(config.INDEX_DIR))
    collection = client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        embedding_function=embedding_fn,
    )
    return collection
