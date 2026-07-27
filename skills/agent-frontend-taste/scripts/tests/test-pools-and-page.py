#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""I tre cataloghi e il selettore — i test che la scheda chiedeva e che mancavano.

Scritti dopo una review che li ha trovati assenti: avevo consegnato un selettore
riscritto da capo e tre cataloghi nuovi con **zero test**, e il lint non se n'era
accorto perche' controlla il cablaggio, non la copertura. Un file di test che non
esiste non fallisce mai.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
_ISO = tempfile.mkdtemp(prefix="pool-test-")
_ENV = {**os.environ, "VESPER_CRAFT_LEDGER": str(Path(_ISO) / "ledger.json")}

fails = 0


def check(label: str, got, want=True) -> None:
    global fails
    if got == want:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}\n  atteso: {want}\n  ottenuto: {got}")
        fails += 1


def load(nome: str):
    spec = importlib.util.spec_from_file_location(nome, SCRIPTS / f"{nome}.py")
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    sys.modules[nome] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    ap, fp, sp = load("accent_pool"), load("font_pool"), load("shape_pool")
    pg = load("repeat_guard")

    # --- trenta per asse, id distinti ---------------------------------------
    for nome, voci in (("accenti", ap.ZONE), ("caratteri", fp.COPPIE), ("forme", sp.FORME)):
        check(f"trenta {nome}", len(voci), 30)
    check("id degli accenti distinti", len({z["id"] for z in ap.ZONE}), 30)
    check("id dei caratteri distinti", len({t[0] for t in fp.COPPIE}), 30)
    check("id delle forme distinti", len({t[0] for t in sp.FORME}), 30)

    # --- i trenta colori sono tutti LEGALI ----------------------------------
    # Il guard ne aveva bocciato uno del catalogo stesso: `ametista` a croma 45
    # cadeva nel hard-reject purple-indigo. Un catalogo che propone un colore
    # vietato ritira l'offerta dopo averla fatta.
    illegali = []
    for z in ap.ZONE:
        c = ap.come_colore(z)
        css = (f'x {{ --ink: {c["ink"]}; --paper: {c["paper"]}; --accent: {c["accent"]}; }}\n'
               f'.page {{ background: var(--paper); color: var(--ink); }}\n'
               f'.band {{ background: var(--ink); color: var(--paper); }}\n'
               f'.btn {{ background: var(--accent); color: var(--paper); }}\n')
        pairs, painted, small, ok = pg.measured_pairs(css)
        rep = pg.analyse(pairs, painted, small)
        if pg.hard_rejects(css, pg.palette_colours(css, rep["colours"])):
            illegali.append(c["id"])
    check("nessun colore del catalogo e' un hard-reject", illegali, [])

    inchiostri = [z["id"] for z in ap.ZONE
                  if pg.chroma(*pg.to_hsl(ap.come_colore(z)["ink"])[1:]) > 4]
    check("ogni inchiostro resta quasi-neutro", inchiostri, [])
    check("gli accenti coprono almeno sei famiglie",
          len({ap.come_colore(z)["famiglia"] for z in ap.ZONE}) >= 6, True)

    # --- shortlist: deterministiche e non imparentate ------------------------
    for nome, mod, chiave in (("accenti", ap, "famiglia"), ("caratteri", fp, "genere"),
                              ("forme", sp, "radius_family")):
        a = mod.suggerisci(4, "2026072712", [])
        b = mod.suggerisci(4, "2026072712", [])
        check(f"{nome}: stesso seed → stessa shortlist",
              [x["id"] for x in a], [x["id"] for x in b])
        check(f"{nome}: nella shortlist nessuna coppia imparentata",
              len({x[chiave] for x in a}), len(a))
        diverse = {tuple(x["id"] for x in mod.suggerisci(4, f"202607271{i}", []))
                   for i in range(6)}
        check(f"{nome}: seed diversi danno shortlist diverse", len(diverse) >= 4, True)

    # --- il selettore --------------------------------------------------------
    out = Path(_ISO) / "palette.html"
    r = subprocess.run(["uv", "run", str(SCRIPTS / "palette_page.py"),
                        "--out", str(out), "--seed", "2026072712", "--no-ledger"],
                       capture_output=True, text=True, env=_ENV)
    check("il selettore si genera", r.returncode, 0)
    t = out.read_text(encoding="utf-8") if out.is_file() else ""
    for g, eti in (("c", "colori"), ("f", "caratteri"), ("s", "forme")):
        check(f"trenta bottoni per {eti}", len(re.findall(rf'data-g="{g}"', t)), 30)
    # Si contano solo i BOTTONI: `.opt[aria-pressed="true"]` nel CSS e' la quarta
    # occorrenza, e contare la stringa nuda faceva sembrare rotta una pagina giusta.
    check("una voce preselezionata per asse",
          len(re.findall(r'<button[^>]*aria-pressed="true"', t)), 3)
    check("la firma che fa saltare close_check", 'data-generated-by="palette_page.py"' in t, True)
    check("la riga di esito e copiabile", 'id="outLine"' in t and 'id="copy"' in t, True)

    # niente prosa: sono le formule della versione precedente
    prosa = [w for w in ("per cambiare", "in uso", "motivo dichiarato", '"why"')
             if w in t.lower()]
    check("nessuna prosa della vecchia pagina", prosa, [])

    # --- rifiuta cio' che non si potrebbe scegliere --------------------------
    meta = Path(_ISO) / "uguali.json"
    meta.write_text(json.dumps({"project": "x", "colours": [
        {"id": "a", "ink": "#14181c", "paper": "#f6f2ec", "accent": "#B7502F"},
        {"id": "b", "ink": "#17191a", "paper": "#f2efe9", "accent": "#bf7865"}]}))
    r = subprocess.run(["uv", "run", str(SCRIPTS / "palette_page.py"), str(meta),
                        "--out", str(Path(_ISO) / "x.html"), "--no-ledger"],
                       capture_output=True, text=True, env=_ENV)
    check("accenti tutti imparentati → exit 2", r.returncode, 2)

    meta2 = Path(_ISO) / "illegale.json"
    meta2.write_text(json.dumps({"project": "x", "colours": [
        {"id": "a", "ink": "#1d5b62", "paper": "#f6f2ec", "accent": "#B7502F"},
        {"id": "b", "ink": "#17191a", "paper": "#f2efe9", "accent": "#2f6f7a"}]}))
    r = subprocess.run(["uv", "run", str(SCRIPTS / "palette_page.py"), str(meta2),
                        "--out", str(Path(_ISO) / "y.html"), "--no-ledger"],
                       capture_output=True, text=True, env=_ENV)
    check("un colore che il guard rifiuta → exit 1", r.returncode, 1)
    check("e lo nomina", "1d5b62" in r.stderr or "a —" in r.stderr, True)

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
