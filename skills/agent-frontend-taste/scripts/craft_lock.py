#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Il lock: le decisioni di craft materializzate **prima** che la pagina esista.

Deciso in consiglio il 2026-07-27, su una diagnosi che nessuno aveva formulato
così: il problema non era l'inventario, era **l'esecuzione**, e il buco stava
esattamente dove il lavoro accade.

    cataloghi (decidono prima)  →  [ qui si scrive la pagina ]  →  guard (dopo)
                                          ^ niente

I cataloghi si potevano ignorare senza che nessuno se ne accorgesse, perché
nessuno confrontava il consegnato con ciò che il catalogo aveva detto. E i guard
sono **statistici**: guardano lo storico, che era quasi vuoto (`accent_family` su
2 voci su 11) e arriva comunque tardi — quando scattano, la pagina è già scritta
e correggere costa un rifacimento. Un controllo che costa un rifacimento è un
controllo che si impara a saltare.

Il lock chiude il buco. Le scelte si sorteggiano dal seed **col progetto dentro**,
si scrivono su disco, e `close_check` confronta la pagina **con il lock** invece
che con la storia: «il lock diceva `salvia`, la pagina è `#db7055`» non lascia
margine di interpretazione e non ha bisogno di nessun campione.

Due condizioni poste al tavolo, e rispettate qui:

  · **Senza lock non si consegna** (Murat): se fosse opzionale, in tre giorni
    nessuno lo scriverebbe più.
  · **Il lock contiene *cosa*, non *perché*** (Vesper): le motivazioni stanno nel
    DESIGN, o torna a essere il verbale che il registro del consiglio ha già
    sostituito.

Il craft resta di Vesper: il lock lo produce il suo seed, non un voto. Smette
solo di essere una cosa che si *dice* di aver fatto.

Usage:
    uv run scripts/craft_lock.py --project hotel-mare --seed 2026072715 \\
        --out apps/hotel-mare/craft-lock.json
    uv run scripts/craft_lock.py --project … --seed … --out … --pick colore=salvia
    uv run scripts/craft_lock.py --show apps/hotel-mare/craft-lock.json

Exit: 0 scritto · 1 una scelta chiesta non esiste · 2 argomenti mancanti.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERA = HERE.parent.parent / "agent-web-animations" / "scripts"


def _mod(nome: str, base: Path = HERE):
    spec = importlib.util.spec_from_file_location(nome, base / f"{nome}.py")
    if not spec or not spec.loader:
        raise SystemExit(f"{nome}.py non trovato in {base}")
    m = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(nome, m)
    spec.loader.exec_module(m)
    return m


def semina(seed: str, slug: str) -> str:
    """Ora **e** progetto. Con la sola ora due landing fatte nello stesso momento
    ricevevano accento, carattere, forma, hero e motion identici — misurato."""
    s = (seed or "").strip()
    if not s:
        raise SystemExit("manca --seed (YYYYMMDDHH)")
    return s if slug in s else f"{s}-{slug}"


def costruisci(slug: str, seed: str, escluse: dict) -> dict:
    ap, fp, sp = _mod("accent_pool"), _mod("font_pool"), _mod("shape_pool")
    s = semina(seed, slug)

    colore = ap.come_colore(ap.scegli(s, escluse.get("colore", [])))
    font = fp.suggerisci(1, s, escluse.get("font", []))[0]
    forma = sp.suggerisci(1, s, escluse.get("forma", []))[0]

    lock = {
        "project": slug,
        "seed": s,
        "colore": {"id": colore["id"], "famiglia": colore["famiglia"],
                   "accent": colore["accent"], "paper": colore["paper"],
                   "ink": colore["ink"]},
        "font": {"id": font["id"], "display": font["display"]["family"],
                 "body": font["body"]["family"], "mono": font["mono"]["family"]},
        "forma": {"id": forma["id"], "radius": forma["radius"],
                  "radius_family": forma["radius_family"], "shape": forma["shape"],
                  "case": forma["case"]},
    }

    # hero ed effetti: se i cataloghi ci sono si sorteggiano, altrimenti si
    # dichiara l'assenza invece di inventare un valore.
    try:
        hg = _mod("hero_gallery")
        arche = hg.load()["archetypes"] if hasattr(hg, "load") else []
        if arche:
            h = hg.suggest(arche, 1, s, escluse.get("hero", []))[0]
            lock["hero"] = {"id": h.get("id") or h.get("n"), "media": h.get("media"),
                            "placement": h.get("placement"), "panel": h.get("panel")}
    except Exception as exc:
        lock["hero"] = {"non_sorteggiato": str(exc)[:80]}

    try:
        fx = _mod("effects_gallery", VERA)
        eff = fx.load()["effects"]
        scelti = fx.suggest(eff, 3, s, escluse.get("effetti", []))
        tende = [e for e in eff if e["id"].startswith("curtain")]
        if tende and not any(e["id"].startswith("curtain") for e in scelti):
            # Regola dell'owner: su una landing almeno una tenda, sempre.
            import random
            scelti[-1] = random.Random(f"{s}|curtain").choice(tende)
        lock["effetti"] = [e["id"] for e in scelti]
    except Exception as exc:
        lock["effetti"] = {"non_sorteggiati": str(exc)[:80]}

    return lock


def applica_scelte(lock: dict, scelte: list[str]) -> dict:
    """Il clic dell'owner atterra qui: una cosa sola con due sorgenti.

    Senza questo, la riga `colore=… · font=… · forma=…` che il selettore produce
    e' un clic che muore — l'ha detto Sally, ed era l'unica sua riga.
    """
    ap, fp, sp = _mod("accent_pool"), _mod("font_pool"), _mod("shape_pool")
    for raw in scelte or []:
        asse, _, valore = raw.partition("=")
        asse, valore = asse.strip().lower(), valore.strip()
        if not valore:
            raise SystemExit(f"scelta malformata: '{raw}'. Serve `asse=id`.")
        if asse == "colore":
            z = [x for x in ap.ZONE if x["id"] == valore]
            if not z:
                raise SystemExit(f"colore sconosciuto: {valore}")
            c = ap.come_colore(z[0])
            lock["colore"] = {"id": c["id"], "famiglia": c["famiglia"], "accent": c["accent"],
                              "paper": c["paper"], "ink": c["ink"], "scelto_da": "owner"}
        elif asse == "font":
            t = [x for x in fp.COPPIE if x[0] == valore]
            if not t:
                raise SystemExit(f"font sconosciuto: {valore}")
            v = fp.voce(t[0])
            lock["font"] = {"id": v["id"], "display": v["display"]["family"],
                            "body": v["body"]["family"], "mono": v["mono"]["family"],
                            "scelto_da": "owner"}
        elif asse == "forma":
            t = [x for x in sp.FORME if x[0] == valore]
            if not t:
                raise SystemExit(f"forma sconosciuta: {valore}")
            v = sp.voce(t[0])
            lock["forma"] = {**{k: v[k] for k in ("id", "radius", "radius_family",
                                                  "shape", "case")}, "scelto_da": "owner"}
        else:
            raise SystemExit(f"asse sconosciuto: {asse}. Sono colore, font, forma.")
    return lock


def scostamenti(lock: dict, report: dict) -> list[str]:
    """Il confronto: cosa dice il lock, cosa dice la pagina consegnata.

    Esatto, non statistico. E' la differenza fra «rosso su 3 delle ultime 5,
    cambia famiglia» e «il lock diceva salvia, la pagina e' #db7055».
    """
    out = []
    acc = report.get("accent") or {}
    atteso = (lock.get("colore") or {}).get("famiglia")
    if atteso and acc.get("famiglia") and acc["famiglia"] != atteso:
        out.append(f"accento: il lock dice `{lock['colore']['id']}` ({atteso}), "
                   f"la pagina ha {acc['hex']} ({acc['famiglia']})")

    faces = report.get("typefaces") or {}
    for ruolo in ("display", "body", "mono"):
        voluto = (lock.get("font") or {}).get(ruolo)
        avuto = faces.get(ruolo)
        if voluto and avuto and voluto.lower() != avuto.lower():
            out.append(f"{ruolo}: il lock dice `{voluto}`, la pagina ha `{avuto}`")

    lay = report.get("layout") or {}
    voluto = (lock.get("forma") or {}).get("radius_family")
    avuto = lay.get("radius_family")
    if voluto and avuto and voluto != avuto:
        out.append(f"raggio: il lock dice `{lock['forma']['id']}` ({voluto}), "
                   f"la pagina ha {avuto}")
    return out


def main() -> int:
    ap_ = argparse.ArgumentParser(description="Il lock delle decisioni di craft")
    ap_.add_argument("--project", help="slug del progetto")
    ap_.add_argument("--seed", default="", help="YYYYMMDDHH (lo slug lo aggiunge lui)")
    ap_.add_argument("--out", help="apps/<slug>/craft-lock.json")
    ap_.add_argument("--pick", action="append", metavar="ASSE=ID",
                     help="la scelta dell'owner: colore=… font=… forma=…")
    ap_.add_argument("--last", action="append", metavar="ASSE=v,v",
                     help="esclusioni per asse")
    ap_.add_argument("--show", metavar="FILE", help="stampa un lock esistente")
    args = ap_.parse_args()

    if args.show:
        p = Path(args.show)
        if not p.is_file():
            print(f"nessun lock in {p}", file=sys.stderr)
            return 1
        print(json.dumps(json.loads(p.read_text(encoding="utf-8")),
                         ensure_ascii=False, indent=1))
        return 0

    if not args.project or not args.out:
        print("servono --project e --out (o --show)", file=sys.stderr)
        return 2

    escluse: dict[str, list[str]] = {}
    for raw in args.last or []:
        a, _, v = raw.partition("=")
        escluse[a.strip().lower()] = [x.strip() for x in v.split(",") if x.strip()]

    lock = applica_scelte(costruisci(args.project, args.seed, escluse), args.pick)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(lock, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    c, f, s = lock["colore"], lock["font"], lock["forma"]
    print(f"{out}")
    print(f"  colore  {c['id']:12s} {c['accent']}  ({c['famiglia']})"
          + ("  ← owner" if c.get("scelto_da") else ""))
    print(f"  font    {f['id']:12s} {f['display']} + {f['body']} + {f['mono']}"
          + ("  ← owner" if f.get("scelto_da") else ""))
    print(f"  forma   {s['id']:12s} raggio {s['radius']} · {s['shape']}"
          + ("  ← owner" if s.get("scelto_da") else ""))
    if isinstance(lock.get("effetti"), list):
        print(f"  effetti {', '.join(lock['effetti'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
