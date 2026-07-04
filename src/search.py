"""
search.py – Durchsucht die lokale Literatur-Datenbank nach einer Frage
und gibt die passendsten Textausschnitte mit Quellenangabe zurück.

Aufruf-Beispiele:
    python src/search.py "Welche Ursachen können einseitige Schluckbeschwerden haben?"
    python src/search.py "Frage" --top-k 5
    python src/search.py "Frage" --source leitlinie.pdf
    python src/search.py "Frage" --json
"""

import argparse
import json

import config
import utils


def format_page(page_number) -> str:
    if page_number is None or page_number < 0:
        return "unbekannt"
    return str(page_number)


def make_excerpt(text: str, max_length: int = 500) -> str:
    """Kürzt einen Chunk-Text für die Anzeige auf eine lesbare Länge,
    ohne mitten im Wort abzuschneiden."""
    text = text.strip()
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + " ..."


def run_search(query: str, top_k: int, source_filter: str = None):
    """Führt die eigentliche Vektorsuche aus und gibt eine Liste von
    Treffer-Dictionaries zurück."""
    collection = utils.get_collection()

    where = {"source_file": source_filter} if source_filter else None

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    hits = []
    for doc, meta, distance in zip(documents, metadatas, distances):
        # ChromaDB liefert eine "Distanz" zurück (kleiner = ähnlicher).
        # Wir rechnen das in einen Score zwischen 0 und 1 um (größer = besser),
        # damit es für Menschen leichter lesbar ist.
        score = 1.0 / (1.0 + distance)

        hits.append(
            {
                "source_file": meta.get("source_file"),
                "page_number": meta.get("page_number"),
                "chunk_index": meta.get("chunk_index"),
                "score": round(score, 3),
                "excerpt": make_excerpt(doc),
            }
        )

    return hits


def print_hits(hits, query: str):
    if not hits:
        print(f'Keine Treffer für "{query}" gefunden.')
        print("Hinweis: Wurde bereits `python src/ingest.py` ausgeführt und liegen Dateien in knowledge/raw/?")
        return

    for i, hit in enumerate(hits, start=1):
        print(f"\nTreffer {i}")
        print(f"Quelle: {hit['source_file']}")
        print(f"Seite: {format_page(hit['page_number'])}")
        print(f"Score: {hit['score']}")
        print("Ausschnitt:")
        print(hit["excerpt"])


def main():
    parser = argparse.ArgumentParser(
        description="Durchsucht die lokale medizinische Literatur-Datenbank."
    )
    parser.add_argument("query", help="Die Suchfrage (in Anführungszeichen).")
    parser.add_argument(
        "--top-k", type=int, default=config.DEFAULT_TOP_K, help="Anzahl der Treffer (Standard: siehe config.py)."
    )
    parser.add_argument(
        "--source", default=None, help="Nur in dieser Datei suchen (Dateiname wie in knowledge/raw/)."
    )
    parser.add_argument(
        "--json", action="store_true", help="Ausgabe als JSON statt als lesbarer Text."
    )

    args = parser.parse_args()
    hits = run_search(args.query, args.top_k, args.source)

    if args.json:
        print(json.dumps({"query": args.query, "results": hits}, indent=2, ensure_ascii=False))
    else:
        print_hits(hits, args.query)


if __name__ == "__main__":
    main()
