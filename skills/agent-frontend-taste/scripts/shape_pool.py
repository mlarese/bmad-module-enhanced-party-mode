#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Trenta forme di pulsante — raggio, riempimento, respiro, maiuscoletto.

Perché esiste, misurato il 2026-07-26 sulle cinque pagine consegnate:
**`--r-btn: 999px` su 5 su 5**. La pillola ovunque. `last_radius_families` in
MEMORY mostrava varietà — pill, soft, micro, sharp, mixed — ma quella è
l'**etichetta**: la geometria consegnata era sempre la stessa.

Come per accenti e caratteri, il catalogo toglie il pregiudizio, non la scelta:
trenta forme già coerenti, e nella stessa shortlist mai due con lo stesso
raggio.

Usage:
    uv run scripts/shape_pool.py --suggest 4 --seed 2026072712
    uv run scripts/shape_pool.py --pick --seed 2026072712 --last pill
    uv run scripts/shape_pool.py --list
"""

from __future__ import annotations

import argparse
import json
import random
import sys

# id · raggio · riempimento · respiro · maiuscoletto · famiglia di raggio
FORME: list[tuple[str, str, str, str, bool, str]] = [
    ("taglio-secco",     "0",      "pieno",      ".85em 1.6em",  False, "sharp"),
    ("taglio-largo",     "0",      "pieno",      "1em 2.4em",    False, "sharp"),
    ("taglio-maiusc",    "0",      "pieno",      ".8em 1.8em",   True,  "sharp"),
    ("taglio-contorno",  "0",      "contornato", ".85em 1.6em",  False, "sharp"),
    ("taglio-sottile",   "0",      "sottolineato", ".4em .1em",  True,  "sharp"),
    ("micro-pieno",      "2px",    "pieno",      ".8em 1.5em",   False, "micro"),
    ("micro-contorno",   "2px",    "contornato", ".8em 1.5em",   False, "micro"),
    ("micro-maiusc",     "3px",    "pieno",      ".75em 1.7em",  True,  "micro"),
    ("micro-stretto",    "2px",    "pieno",      ".6em 1.1em",   False, "micro"),
    ("micro-doppio",     "3px",    "contornato", ".9em 2em",     True,  "micro"),
    ("soft-pieno",       "6px",    "pieno",      ".8em 1.5em",   False, "soft"),
    ("soft-largo",       "6px",    "pieno",      ".95em 2.2em",  False, "soft"),
    ("soft-contorno",    "5px",    "contornato", ".8em 1.5em",   False, "soft"),
    ("soft-maiusc",      "8px",    "pieno",      ".75em 1.6em",  True,  "soft"),
    ("soft-compatto",    "6px",    "pieno",      ".55em 1em",    False, "soft"),
    ("tondo-pieno",      "12px",   "pieno",      ".85em 1.6em",  False, "rounded"),
    ("tondo-largo",      "16px",   "pieno",      "1em 2.4em",    False, "rounded"),
    ("tondo-contorno",   "12px",   "contornato", ".85em 1.6em",  False, "rounded"),
    ("tondo-maiusc",     "14px",   "pieno",      ".8em 1.8em",   True,  "rounded"),
    ("tondo-morbido",    "20px",   "pieno",      ".9em 1.9em",   False, "rounded"),
    ("tondo-doppio",     "18px",   "contornato", ".95em 2.1em",  True,  "rounded"),
    ("pillola-piena",    "999px",  "pieno",      ".8em 1.7em",   False, "pill"),
    ("pillola-larga",    "999px",  "pieno",      "1em 2.6em",    False, "pill"),
    ("pillola-contorno", "999px",  "contornato", ".8em 1.7em",   False, "pill"),
    ("pillola-maiusc",   "999px",  "pieno",      ".75em 1.9em",  True,  "pill"),
    ("pillola-compatta", "999px",  "pieno",      ".5em 1.1em",   False, "pill"),
    ("misto-alto",       "10px",   "pieno",      "1.1em 1.6em",  False, "rounded"),
    ("misto-basso",      "4px",    "pieno",      ".45em 1.8em",  True,  "soft"),
    ("linea-sola",       "0",      "sottolineato", ".35em .05em", False, "sharp"),
    ("linea-maiusc",     "0",      "sottolineato", ".4em .05em",  True,  "sharp"),
]



def _seed_o_muori(seed: str) -> str:
    """Senza seed non si sceglie: una costante di ripiego e' peggio di un errore.

    Il default era `"no-seed"`, cioe' una **costante**: senza `--seed` ogni
    invocazione restituiva per sempre la stessa voce, e nessuno se ne accorgeva
    perche' l'output sembrava una scelta. Misurato il 2026-07-27.

    E il seed deve contenere **lo slug del progetto**, non solo l'ora: con
    `YYYYMMDDHH-<slug>` due landing fatte nella stessa ora ricevevano accento, font,
    forma, hero e motion **identici** — ed e' esattamente il «prende sempre gli
    stessi template» che l'owner vedeva.
    """
    s = (seed or "").strip()
    if not s:
        raise SystemExit(
            "manca --seed. Serve `YYYYMMDDHH-<slug>`, per esempio "
            "`--seed 2026072715-hotel-mare`: senza, la scelta e' sempre la "
            "stessa; con la sola ora, due progetti fatti nello stesso momento "
            "ricevono le stesse identiche scelte."
        )
    if "-" not in s and "|" not in s:
        print(f"! seed `{s}` senza slug di progetto: due lavori nella stessa ora "
              "avranno le stesse scelte. Usa `YYYYMMDDHH-<slug>`.", file=__import__("sys").stderr)
    return s


def voce(t) -> dict:
    i, radius, shape, pad, case, fam = t
    return {"id": i, "radius": radius, "shape": shape, "pad": pad,
            "case": "maiuscoletto" if case else "normale", "radius_family": fam}


def suggerisci(n: int, seed: str, escluse: list[str]) -> list[dict]:
    """Deterministica, e **mai due con la stessa famiglia di raggio**."""
    fuori = {v.strip().lower() for v in escluse if v.strip()}
    pool = [voce(t) for t in FORME if t[0] not in fuori and t[5] not in fuori]
    if not pool:
        pool = [voce(t) for t in FORME]
    rng = random.Random(f"{seed}|shape-pool")
    rng.shuffle(pool)
    scelte, viste = [], set()
    for stretto in (True, False):
        for v in pool:
            if len(scelte) >= n:
                break
            if v in scelte or (stretto and v["radius_family"] in viste):
                continue
            scelte.append(v)
            viste.add(v["radius_family"])
    return scelte[:n]


def riga(v: dict) -> str:
    return (f"  {v['id']:18s} raggio {v['radius']:>6s}  {v['shape']:12s} "
            f"respiro {v['pad']:>12s}  {v['case']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Trenta forme di pulsante")
    ap.add_argument("--suggest", type=int, metavar="N")
    ap.add_argument("--pick", action="store_true", help="LA forma di questo lavoro, dal seed")
    ap.add_argument("--seed", default="")
    ap.add_argument("--last", default="", help="id o famiglie di raggio da escludere")
    ap.add_argument("--show", metavar="ID")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    args = ap.parse_args()

    if args.show:
        t = [f for f in FORME if f[0] == args.show.strip().lower()]
        if not t:
            print(f"forma sconosciuta: {args.show}. Sono {len(FORME)}.", file=sys.stderr)
            return 1
        v = voce(t[0])
        print(json.dumps(v, ensure_ascii=False, indent=1) if args.format == "json" else riga(v))
        return 0

    if args.pick:
        v = suggerisci(1, _seed_o_muori(args.seed), args.last.split(","))[0]
        print(json.dumps(v, ensure_ascii=False, indent=1) if args.format == "json" else riga(v))
        return 0

    scelte = ([voce(t) for t in FORME] if args.list or not args.suggest
              else suggerisci(args.suggest, _seed_o_muori(args.seed), args.last.split(",")))
    if args.format == "json":
        print(json.dumps(scelte, ensure_ascii=False, indent=1))
        return 0
    print(f"# Forme di pulsante — {len(scelte)} di {len(FORME)}\n")
    for v in scelte:
        print(riga(v))
    if args.suggest:
        print(f"\n{len({v['radius_family'] for v in scelte})} famiglie di raggio su {len(scelte)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
