"""
webapp.py – Einfache, mobil-taugliche Weboberfläche für die lokale
Literatursuche.

Läuft komplett lokal in deinem Heimnetzwerk. Es werden keine Daten an
externe Dienste geschickt - dieselbe Suche wie in search.py, nur mit
Browser-Oberfläche statt Kommandozeile.

Start:
    python src/webapp.py

Danach im Browser öffnen:
    http://localhost:5000

Vom Handy aus (im GLEICHEN WLAN wie dein Rechner):
    http://<lokale-IP-deines-Rechners>:5000

Die lokale IP findest du z.B. mit:
    Linux/Mac: hostname -I
    Windows:   ipconfig
"""

from flask import Flask, render_template, request

import config
from search import run_search

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").strip()
    top_k = request.args.get("top_k", config.DEFAULT_TOP_K, type=int)
    source = request.args.get("source", "").strip() or None

    hits = run_search(query, top_k, source) if query else []

    return render_template(
        "search.html",
        query=query,
        top_k=top_k,
        source=source or "",
        hits=hits,
        searched=bool(query),
    )


if __name__ == "__main__":
    # host="0.0.0.0" statt "127.0.0.1": macht die App im lokalen Netzwerk
    # erreichbar (z.B. vom Handy), nicht nur auf diesem Rechner selbst.
    app.run(host="0.0.0.0", port=5000, debug=False)
