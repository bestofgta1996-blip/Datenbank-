"""
ingest.py – Liest alle unterstützten Dateien aus knowledge/raw/ ein,
zerlegt sie in Chunks, erstellt lokale Embeddings und speichert alles in
der lokalen ChromaDB-Datenbank unter knowledge/index/.

Aufruf:
    python src/ingest.py

Wird eine Datei erneut verarbeitet, obwohl sie sich nicht verändert hat,
wird sie automatisch übersprungen (erkannt am Datei-Hash). Ändert sich eine
Datei, werden ihre alten Chunks ersetzt.
"""

import json
from pathlib import Path

import config
import utils

MANIFEST_PATH = config.PROCESSED_DIR / "manifest.json"


def load_manifest() -> dict:
    """Lädt die Liste bereits verarbeiteter Dateien (Name -> Hash, Anzahl Chunks)."""
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def save_manifest(manifest: dict):
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def extract_pdf_pages(file_path: Path):
    """Liest eine PDF-Datei und gibt eine Liste von (Seitenzahl, Text) zurück."""
    import fitz  # PyMuPDF

    pages = []
    doc = fitz.open(str(file_path))
    for i, page in enumerate(doc, start=1):
        pages.append((i, page.get_text()))
    doc.close()
    return pages


def extract_epub_text(file_path: Path) -> str:
    """Liest ein EPUB und gibt den reinen Text aller Kapitel zurück.

    EPUBs haben keine festen "Seiten" wie PDFs, daher gibt es hier keine
    Seitenzahl-Metadaten (page_number bleibt leer).
    """
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup

    book = epub.read_epub(str(file_path))
    texts = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            texts.append(soup.get_text())
    return "\n\n".join(texts)


def build_chunks_for_pdf(file_path: Path, relative_name: str, file_hash: str):
    """Chunking für PDFs: behält dabei mit, von welcher Seite jeder Chunk
    stammt (Seite des ersten Worts im Chunk)."""
    pages = extract_pdf_pages(file_path)

    words = []
    word_pages = []
    for page_num, page_text in pages:
        page_text = utils.clean_text(page_text)
        for word in page_text.split():
            words.append(word)
            word_pages.append(page_num)

    documents, metadatas, ids = [], [], []
    indices = utils.chunk_indices(len(words), config.CHUNK_SIZE, config.CHUNK_OVERLAP)

    for chunk_index, (start, end) in enumerate(indices):
        chunk_str = " ".join(words[start:end])
        page_number = word_pages[start] if words else None

        documents.append(chunk_str)
        metadatas.append(
            utils.build_metadata(relative_name, "pdf", file_hash, chunk_index, page_number)
        )
        ids.append(f"{file_hash}_{chunk_index}")

    return documents, metadatas, ids


def build_chunks_for_plain_text(text: str, file_type: str, relative_name: str, file_hash: str):
    """Chunking für TXT/Markdown/EPUB: keine Seitenzahlen verfügbar."""
    text = utils.clean_text(text)
    documents, metadatas, ids = [], [], []

    for chunk_index, chunk_str in enumerate(
        utils.chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    ):
        documents.append(chunk_str)
        metadatas.append(
            utils.build_metadata(relative_name, file_type, file_hash, chunk_index, None)
        )
        ids.append(f"{file_hash}_{chunk_index}")

    return documents, metadatas, ids


def build_chunks_for_file(file_path: Path, relative_name: str, file_hash: str):
    """Wählt je nach Dateityp die passende Extraktions-/Chunking-Methode."""
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return build_chunks_for_pdf(file_path, relative_name, file_hash)

    if suffix == ".txt":
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        return build_chunks_for_plain_text(text, "text", relative_name, file_hash)

    if suffix == ".md":
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        return build_chunks_for_plain_text(text, "markdown", relative_name, file_hash)

    if suffix == ".epub":
        text = extract_epub_text(file_path)
        return build_chunks_for_plain_text(text, "epub", relative_name, file_hash)

    raise ValueError(f"Nicht unterstützter Dateityp: {suffix}")


def main():
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(
        p
        for p in config.RAW_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in config.SUPPORTED_EXTENSIONS
    )

    if not files:
        utils.log(
            f"Keine unterstützten Dateien in {config.RAW_DIR} gefunden. "
            f"Bitte PDF/TXT/MD/EPUB-Dateien dort ablegen und erneut ausführen."
        )
        return

    utils.log("Lade Embedding-Modell (beim ersten Mal wird es einmalig heruntergeladen)...")
    collection = utils.get_collection()

    manifest = load_manifest()
    total = len(files)
    processed = skipped = failed = 0

    for i, file_path in enumerate(files, start=1):
        relative_name = str(file_path.relative_to(config.RAW_DIR))
        utils.log(f"[{i}/{total}] Verarbeite: {relative_name}")

        try:
            file_hash = utils.compute_file_hash(file_path)
            previous = manifest.get(relative_name)

            if previous and previous.get("hash") == file_hash:
                utils.log("  -> unverändert, wird übersprungen.")
                skipped += 1
                continue

            if previous and previous.get("hash") != file_hash:
                utils.log("  -> Datei wurde geändert, alte Chunks werden ersetzt.")
                collection.delete(where={"document_hash": previous["hash"]})

            documents, metadatas, ids = build_chunks_for_file(file_path, relative_name, file_hash)

            if not documents:
                utils.log("  -> Kein Text extrahierbar, überspringe.", level="WARN")
                continue

            collection.upsert(documents=documents, metadatas=metadatas, ids=ids)

            manifest[relative_name] = {"hash": file_hash, "chunks": len(documents)}
            processed += 1
            utils.log(f"  -> {len(documents)} Chunks gespeichert.")

        except Exception as exc:
            # Fehler bei einer einzelnen Datei sollen den gesamten Lauf nicht
            # abbrechen - wir loggen den Fehler und machen mit der nächsten
            # Datei weiter.
            failed += 1
            utils.log(f"  -> FEHLER bei {relative_name}: {exc}", level="ERROR")
            continue

    save_manifest(manifest)

    utils.log("Fertig.")
    utils.log(f"Verarbeitet: {processed} | Übersprungen (unverändert): {skipped} | Fehler: {failed}")


if __name__ == "__main__":
    main()
