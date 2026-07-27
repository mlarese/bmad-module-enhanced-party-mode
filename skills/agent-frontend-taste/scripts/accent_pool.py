#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Trenta zone di accento — il colore della CTA smette di essere sempre lo stesso.

Perché esiste, misurato il 2026-07-27 sulle cinque pagine consegnate: l'accento
era **`rosso` su 3 su 5**, e i quattro esadecimali caldi — `#bf7865`, `#7e222a`,
`#B7502F`, `#e4b53e` — stavano tutti nella stessa zona terracotta-ocra. Il quinto
era un magenta a croma 10, cioè quasi neutro.

**Nessuna regola lo contava.** Il ledger registrava il settore dominante (che è
fatto di fondo e scuro, quasi sempre neutri) e la famiglia dello scuro. Mai
l'accento — che è il colore del pulsante, cioè l'unica tinta che l'occhio
guarda davvero. Il guard nacque proprio dall'osservazione opposta («l'accento
era diverso ogni volta: rame, zafferano, corallo, limone»): erano nomi diversi
nella stessa zona di ruota, ed è lo stesso errore di allora, un piano più giù.

**Zone, non esadecimali.** La palette resta derivata da `locale + register +
activity` — è legge (`craft-rules.md`). Qui non si sorteggia un colore: si
sorteggia **in che zona della ruota cercarlo**, e l'esadecimale preciso lo trova
Vesper dentro quella zona, sul luogo e sul carattere del business. Così la
varietà è garantita dalla geometria e il senso resta dal contesto.

Trenta zone coprono la ruota per intero, non i 130° caldi in cui il gusto
scivola da solo.

Usage:
    uv run scripts/accent_pool.py --suggest 4 --seed 2026072712
    uv run scripts/accent_pool.py --suggest 4 --seed … --last rosso,terra
    uv run scripts/accent_pool.py --show brace          # una zona sola
    uv run scripts/accent_pool.py --list                # tutte e trenta

Exit: 0 · 1 se una zona chiesta non esiste.
"""

from __future__ import annotations

import argparse
import json
import random
import sys

# (id, nome, hue centro, ampiezza±, croma indicativa, settore, quando regge)
ZONE: list[dict] = [
    # — rosso / magenta —
    {"id": "lacca",      "hue": 358, "spread": 8,  "chroma": 55, "nota": "rosso profondo laccato; teatri, sartorie, vini"},
    {"id": "granata",    "hue": 348, "spread": 8,  "chroma": 42, "nota": "rosso scuro terroso; cantine, macellerie di pregio"},
    {"id": "fucsia",     "hue": 330, "spread": 10, "chroma": 60, "nota": "magenta acceso; beauty, eventi, moda giovane"},
    {"id": "prugna",     "hue": 315, "spread": 10, "chroma": 35, "nota": "magenta scuro sobrio; gioielli, pasticceria d'autore"},
    {"id": "corallo",    "hue": 10,  "spread": 8,  "chroma": 58, "nota": "rosso-arancio caldo; mare, hotel, ristorazione"},
    # — terra / arancio —
    {"id": "mattone",    "hue": 18,  "spread": 8,  "chroma": 48, "nota": "terracotta piena; artigianato, forni, edilizia"},
    {"id": "rame",       "hue": 26,  "spread": 7,  "chroma": 52, "nota": "metallo caldo; birrifici, cucine, illuminazione"},
    {"id": "zafferano",  "hue": 38,  "spread": 7,  "chroma": 62, "nota": "arancio-oro; spezie, street food, mercati"},
    {"id": "ocra",       "hue": 44,  "spread": 6,  "chroma": 45, "nota": "giallo terroso; agriturismi, panifici, ceramiche"},
    {"id": "cuoio",      "hue": 30,  "spread": 6,  "chroma": 30, "nota": "bruno caldo desaturato; pelletterie, librerie"},
    # — giallo —
    {"id": "limone",     "hue": 55,  "spread": 6,  "chroma": 70, "nota": "giallo acido; gelaterie, sport, promo"},
    {"id": "senape",     "hue": 48,  "spread": 6,  "chroma": 50, "nota": "giallo spento; bistrot, vintage, editoria"},
    {"id": "grano",      "hue": 50,  "spread": 6,  "chroma": 32, "nota": "giallo pallido; pastifici, cosmetica naturale"},
    # — verde —
    {"id": "oliva",      "hue": 75,  "spread": 8,  "chroma": 38, "nota": "verde giallo smorzato; frantoi, erboristerie"},
    {"id": "felce",      "hue": 105, "spread": 10, "chroma": 40, "nota": "verde vegetale; vivai, outdoor, benessere"},
    {"id": "smeraldo",   "hue": 150, "spread": 8,  "chroma": 55, "nota": "verde freddo saturo; finanza, gioielli, cliniche"},
    {"id": "salvia",     "hue": 120, "spread": 10, "chroma": 22, "nota": "verde grigio tenue; spa, studi, interior"},
    {"id": "menta",      "hue": 160, "spread": 8,  "chroma": 45, "nota": "verde chiaro fresco; dentisti, tech leggero"},
    # — teal / ciano —
    {"id": "pino",       "hue": 172, "spread": 7,  "chroma": 40, "nota": "teal scuro; montagna, laghi, hotel di quota"},
    {"id": "ottanio",    "hue": 185, "spread": 7,  "chroma": 50, "nota": "teal saturo; nautica, piscine, prodotti"},
    {"id": "acqua",      "hue": 195, "spread": 7,  "chroma": 35, "nota": "azzurro-verde chiaro; terme, cliniche, estetica"},
    # — blu —
    {"id": "cobalto",    "hue": 220, "spread": 8,  "chroma": 62, "nota": "blu pieno; sport, logistica, software"},
    {"id": "oltremare",  "hue": 232, "spread": 8,  "chroma": 55, "nota": "blu profondo; assicurazioni, editoria, musei"},
    {"id": "notte",      "hue": 240, "spread": 8,  "chroma": 30, "nota": "blu scuro sobrio; studi legali, consulenza"},
    {"id": "polvere",    "hue": 210, "spread": 8,  "chroma": 20, "nota": "azzurro grigio; medicale, uffici, B2B quieto"},
    # — viola —
    {"id": "glicine",    "hue": 270, "spread": 8,  "chroma": 28, "nota": "viola tenue; floreale, wedding, profumeria"},
    # Croma 38, non 45: a 45 il rappresentante usciva `#8f39ac`, che cade nel
    # hard-reject «purple-indigo AI» (hue 235–295 con saturazione ≥45). Un
    # catalogo che propone un colore vietato e' un catalogo che ritira l'offerta
    # dopo averla fatta — l'ha preso il guard alla prima generazione.
    {"id": "ametista",   "hue": 285, "spread": 8,  "chroma": 38, "nota": "viola; eventi, musica, formazione"},
    {"id": "vinaccia",   "hue": 300, "spread": 8,  "chroma": 32, "nota": "viola rosato scuro; enoteche, teatri, atelier"},
    # — neutri caldi/freddi con una punta —
    {"id": "peltro",     "hue": 205, "spread": 15, "chroma": 12, "nota": "grigio freddo con punta; industria, archivi"},
    {"id": "sabbia",     "hue": 40,  "spread": 15, "chroma": 14, "nota": "grigio caldo con punta; minimal, gallerie"},
]

# `sector_of` del guard, replicato qui solo per etichettare le zone senza
# importare tutto il modulo: i confini sono gli stessi.
SECTORS = [("rosso", 345, 15), ("terra", 15, 45), ("giallo", 45, 70), ("verde", 70, 165),
           ("teal", 165, 200), ("blu", 200, 260), ("viola", 260, 300), ("magenta", 300, 345)]
FAMILY = {"verde": "verde", "teal": "verde"}


def settore(hue: float) -> str:
    for nome, a, b in SECTORS:
        if a > b:
            if hue >= a or hue < b:
                return nome
        elif a <= hue < b:
            return nome
    return "rosso"


def famiglia(hue: float) -> str:
    s = settore(hue)
    return FAMILY.get(s, s)


def arricchisci(z: dict) -> dict:
    s = settore(z["hue"])
    return {**z, "settore": s, "famiglia": FAMILY.get(s, s),
            "hue_range": f"{(z['hue'] - z['spread']) % 360:.0f}–{(z['hue'] + z['spread']) % 360:.0f}°"}


def suggerisci(n: int, seed: str, escluse: list[str]) -> list[dict]:
    """Shortlist deterministica, e **mai due dalla stessa famiglia**.

    È la regola che risolve il difetto: quattro proposte tutte terracotta sono
    una proposta sola mostrata quattro volte.
    """
    fuori = {v.strip().lower() for v in escluse if v.strip()}
    pool = [arricchisci(z) for z in ZONE
            if z["id"] not in fuori and settore(z["hue"]) not in fuori
            and famiglia(z["hue"]) not in fuori]
    if not pool:
        pool = [arricchisci(z) for z in ZONE]
    rng = random.Random(f"{seed}|accent-pool")
    rng.shuffle(pool)
    scelte: list[dict] = []
    viste: set[str] = set()
    for passo in (True, False):          # prima una per famiglia, poi riempi
        for z in pool:
            if len(scelte) >= n:
                break
            if z in scelte:
                continue
            if passo and z["famiglia"] in viste:
                continue
            scelte.append(z)
            viste.add(z["famiglia"])
    return scelte[:n]


def _hex(h: float, c: float, l: float) -> str:
    """HSL→hex con la croma del guard (che e' saturazione pesata sulla luminosita)."""
    import colorsys
    k = 1 - abs(2 * l / 100 - 1)
    s = min(1.0, (c / 100) / k) if k else 0.0
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l / 100, s)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def come_colore(z: dict) -> dict:
    """Una zona diventa un colore concreto: accento, carta, inchiostro.

    L'inchiostro resta **quasi-neutro** (croma 3, sotto la soglia 4 del guard):
    lo scuro strutturale colorato e' un hard-reject, e proporre trenta colori
    che il guard poi rifiuta sarebbe un catalogo di cose non scegliibili.
    """
    z = arricchisci(z)
    return {"id": z["id"], "settore": z["settore"], "famiglia": z["famiglia"],
            "accent": _hex(z["hue"], z["chroma"], 45),
            "paper": _hex(z["hue"], 6, 95),
            "ink": _hex(z["hue"], 3, 12)}


def scegli(seed: str, escluse: list[str]) -> dict:
    """LA zona di questo lavoro, dal seed — non dal gusto.

    E' il punto che mancava. Il catalogo esisteva e nessuno lo consultava: su
    cinque CTA consegnate quattro stavano entro venti gradi di tinta (12°, 13°,
    15°, 355°), pur avendo 21 zone fredde disponibili. Una regola in prosa non
    sposta un pregiudizio; un sorteggio si'. Stesso schema dell'archetipo di
    hero e del motion, che per questa ragione si prendono da seed.
    """
    return suggerisci(1, seed, escluse)[0]


def riga(z: dict) -> str:
    return (f"  {z['id']:11s} {z['hue_range']:>11s}  croma ~{z['chroma']:<3d} "
            f"{z['settore']:8s} {z['nota']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Trenta zone di accento per la CTA")
    ap.add_argument("--suggest", type=int, metavar="N", help="shortlist deterministica")
    ap.add_argument("--seed", default="", help="seed YYYYMMDDHH")
    ap.add_argument("--last", default="", help="id, settori o famiglie da escludere")
    ap.add_argument("--show", metavar="ID", help="una zona sola")
    ap.add_argument("--list", action="store_true", help="tutte e trenta")
    ap.add_argument("--as-colours", action="store_true",
                    help="le zone come colori concreti {id, ink, paper, accent}")
    ap.add_argument("--pick", action="store_true",
                    help="LA zona di questo lavoro, dal seed: non si sceglie a naso")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    args = ap.parse_args()

    if args.show:
        trovata = [z for z in ZONE if z["id"] == args.show.strip().lower()]
        if not trovata:
            print(f"zona sconosciuta: {args.show}. Sono {len(ZONE)}: "
                  f"{', '.join(z['id'] for z in ZONE)}", file=sys.stderr)
            return 1
        z = arricchisci(trovata[0])
        print(json.dumps(z, ensure_ascii=False, indent=1) if args.format == "json" else riga(z))
        return 0

    if args.pick:
        z = come_colore(scegli(args.seed or "no-seed", args.last.split(",")))
        print(json.dumps(z, ensure_ascii=False, indent=1) if args.format == "json"
              else f"  {z['id']}  accent {z['accent']}  paper {z['paper']}  ink {z['ink']}"
                   f"  ({z['famiglia']})")
        return 0

    if args.as_colours:
        col = [come_colore(z) for z in ZONE]
        if args.format == "json":
            print(json.dumps(col, ensure_ascii=False, indent=1))
        else:
            for c in col:
                print(f"  {c['id']:11s} accent {c['accent']}  paper {c['paper']}  "
                      f"ink {c['ink']}  ({c['famiglia']})")
        return 0

    scelte = ([arricchisci(z) for z in ZONE] if args.list or not args.suggest
              else suggerisci(args.suggest, args.seed or "no-seed",
                              args.last.split(",")))
    if args.format == "json":
        print(json.dumps(scelte, ensure_ascii=False, indent=1))
        return 0
    print(f"# Zone di accento — {len(scelte)} di {len(ZONE)}\n")
    for z in scelte:
        print(riga(z))
    if args.suggest:
        fam = {z["famiglia"] for z in scelte}
        print(f"\n{len(fam)} famiglie diverse su {len(scelte)} proposte: "
              f"{', '.join(sorted(fam))}.")
        print("L'esadecimale preciso lo scegli tu dentro la zona, da locale + "
              "register + activity — la zona garantisce che non sia sempre lo stesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
