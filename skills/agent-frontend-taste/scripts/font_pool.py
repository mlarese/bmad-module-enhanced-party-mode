#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Trenta accoppiate tipografiche — display, testo, terza voce.

Perché esiste, misurato il 2026-07-26 sulle cinque pagine consegnate: **`DM Mono`
era il mono di 5 su 5**, `DM Sans` il testo di 4 su 5, `Fraunces` il display di
3 su 5. Il mono era il punto cieco — display e testo si scelgono, la terza voce
si mette «quella che va bene» e diventa sempre la stessa.

Come per gli accenti: il catalogo non serve a togliere la scelta, serve a
toglierle il pregiudizio. Trenta accoppiate già in equilibrio, da cui il seed
pesca — e nessuna famiglia tipografica compare due volte nella stessa shortlist.

Tutti i caratteri sono webfont gratuiti (Google Fonts); `stack` è il ripiego di
sistema quando il font non si carica.

Usage:
    uv run scripts/font_pool.py --suggest 4 --seed 2026072712
    uv run scripts/font_pool.py --pick --seed 2026072712 --last fraunces-inter
    uv run scripts/font_pool.py --list
"""

from __future__ import annotations

import argparse
import json
import random
import sys

G = "https://fonts.googleapis.com/css2?family={}&display=swap"
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "system-ui, -apple-system, 'Segoe UI', sans-serif"
MONO = "ui-monospace, Menlo, Consolas, monospace"


def _c(fam: str) -> str:
    return G.format(fam.replace(" ", "+") + ":wght@400;500;700")


# id · display · body · mono/terza · genere (per non ripetere lo stesso registro)
COPPIE: list[tuple[str, str, str, str, str]] = [
    ("fraunces-inter",      "Fraunces",            "Inter",             "JetBrains Mono",   "serif-morbido"),
    ("playfair-worksans",   "Playfair Display",    "Work Sans",         "IBM Plex Mono",    "serif-alto"),
    ("bodoni-manrope",      "Bodoni Moda",         "Manrope",           "Space Mono",       "didone"),
    ("gloock-redhat",       "Gloock",              "Red Hat Text",      "Red Hat Mono",     "serif-alto"),
    ("newsreader-figtree",  "Newsreader",          "Figtree",           "Fira Code",        "serif-editoriale"),
    ("literata-syne",       "Literata",            "Syne",              "Anonymous Pro",    "serif-editoriale"),
    ("cormorant-sora",      "Cormorant Garamond",  "Sora",              "Azeret Mono",      "garaldo"),
    ("ebgaramond-epilogue", "EB Garamond",         "Epilogue",          "Martian Mono",     "garaldo"),
    ("lora-dmsans",         "Lora",                "DM Sans",           "DM Mono",          "serif-morbido"),
    ("spectral-karla",      "Spectral",            "Karla",             "Overpass Mono",    "serif-editoriale"),
    ("bricolage-sourcesans","Bricolage Grotesque", "Source Sans 3",     "Source Code Pro",  "grottesco-espressivo"),
    ("archivo-instrument",  "Archivo Expanded",    "Instrument Sans",   "Spline Sans Mono", "grottesco-largo"),
    ("anton-inter",         "Anton",               "Inter Tight",       "Roboto Mono",      "condensato"),
    ("oswald-lato",         "Oswald",              "Lato",              "Ubuntu Mono",      "condensato"),
    ("bebas-publicsans",    "Bebas Neue",          "Public Sans",       "Courier Prime",    "condensato"),
    ("unbounded-rubik",     "Unbounded",           "Rubik",             "Chivo Mono",       "geometrico-display"),
    ("clash-satoshi",       "Chakra Petch",        "Be Vietnam Pro",    "Geist Mono",       "tecnico"),
    ("spacegrotesk-inter",  "Space Grotesk",       "Inter",             "Space Mono",       "tecnico"),
    ("outfit-plexsans",     "Outfit",              "IBM Plex Sans",     "IBM Plex Mono",    "geometrico"),
    ("poppins-nunito",      "Poppins",             "Nunito Sans",       "Fira Mono",        "geometrico-morbido"),
    ("zillaslab-mulish",    "Zilla Slab",          "Mulish",            "Cousine",          "slab"),
    ("robotoslab-asap",     "Roboto Slab",         "Asap",              "Roboto Mono",      "slab"),
    ("bitter-cabin",        "Bitter",              "Cabin",             "Inconsolata",      "slab"),
    ("crimson-jost",        "Crimson Pro",         "Jost",              "Reddit Mono",      "garaldo"),
    ("marcellus-lexend",    "Marcellus",           "Lexend",            "Victor Mono",      "lapidario"),
    ("cinzel-barlow",       "Cinzel",              "Barlow",            "Share Tech Mono",  "lapidario"),
    ("italiana-hanken",     "Italiana",            "Hanken Grotesk",    "Fragment Mono",    "didone"),
    ("prata-albertsans",    "Prata",               "Albert Sans",       "Kode Mono",        "didone"),
    ("vollkorn-heebo",      "Vollkorn",            "Heebo",             "Sometype Mono",    "serif-morbido"),
    ("petrona-onest",       "Petrona",             "Onest",             "Departure Mono",   "serif-editoriale"),
]


def voce(t: tuple[str, str, str, str, str]) -> dict:
    i, d, b, m, genere = t
    return {"id": i, "genere": genere,
            "display": {"family": d, "stack": SERIF if "serif" in genere or genere in
                        ("didone", "garaldo", "slab", "lapidario") else SANS, "url": _c(d)},
            "body": {"family": b, "stack": SANS, "url": _c(b)},
            "mono": {"family": m, "stack": MONO, "url": _c(m)}}


def suggerisci(n: int, seed: str, escluse: list[str]) -> list[dict]:
    """Deterministica, e **mai due dallo stesso genere** nella stessa shortlist."""
    fuori = {v.strip().lower() for v in escluse if v.strip()}
    pool = [voce(t) for t in COPPIE
            if t[0] not in fuori and t[4] not in fuori
            and not (fuori & {t[1].lower(), t[2].lower(), t[3].lower()})]
    if not pool:
        pool = [voce(t) for t in COPPIE]
    rng = random.Random(f"{seed}|font-pool")
    rng.shuffle(pool)
    scelte, generi = [], set()
    for stretto in (True, False):
        for v in pool:
            if len(scelte) >= n:
                break
            if v in scelte or (stretto and v["genere"] in generi):
                continue
            scelte.append(v)
            generi.add(v["genere"])
    return scelte[:n]


def riga(v: dict) -> str:
    return (f"  {v['id']:22s} {v['display']['family']:20s} + {v['body']['family']:18s} "
            f"+ {v['mono']['family']:16s} ({v['genere']})")


def main() -> int:
    ap = argparse.ArgumentParser(description="Trenta accoppiate tipografiche")
    ap.add_argument("--suggest", type=int, metavar="N")
    ap.add_argument("--pick", action="store_true", help="LA coppia di questo lavoro, dal seed")
    ap.add_argument("--seed", default="")
    ap.add_argument("--last", default="", help="id, generi o nomi di font da escludere")
    ap.add_argument("--show", metavar="ID")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    args = ap.parse_args()

    if args.show:
        t = [c for c in COPPIE if c[0] == args.show.strip().lower()]
        if not t:
            print(f"accoppiata sconosciuta: {args.show}. Sono {len(COPPIE)}.", file=sys.stderr)
            return 1
        v = voce(t[0])
        print(json.dumps(v, ensure_ascii=False, indent=1) if args.format == "json" else riga(v))
        return 0

    if args.pick:
        v = suggerisci(1, args.seed or "no-seed", args.last.split(","))[0]
        print(json.dumps(v, ensure_ascii=False, indent=1) if args.format == "json" else riga(v))
        return 0

    scelte = ([voce(t) for t in COPPIE] if args.list or not args.suggest
              else suggerisci(args.suggest, args.seed or "no-seed", args.last.split(",")))
    if args.format == "json":
        print(json.dumps(scelte, ensure_ascii=False, indent=1))
        return 0
    print(f"# Accoppiate tipografiche — {len(scelte)} di {len(COPPIE)}\n")
    for v in scelte:
        print(riga(v))
    if args.suggest:
        print(f"\n{len({v['genere'] for v in scelte})} generi diversi su {len(scelte)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
