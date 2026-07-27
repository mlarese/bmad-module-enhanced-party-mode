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

    # --- il lock: differenziale sul seed, che e' il difetto che ha resistito -----
    # Con `YYYYMMDDHH` tre progetti nella stessa ora ricevevano scelte IDENTICHE.
    # Questo test lo avrebbe preso in tre secondi: due slug, stesso orario,
    # esiti diversi. E' la forma che il consiglio ha reso obbligatoria — acceso
    # contro spento devono differire, non basta che «funzioni».
    cl = load("craft_lock")
    a = cl.costruisci("hotel-mare", "2026072715", {})
    b = cl.costruisci("falegnameria", "2026072715", {})
    check("stesso orario, slug diversi → colori diversi",
          a["colore"]["id"] != b["colore"]["id"], True)
    check("…e caratteri diversi", a["font"]["id"] != b["font"]["id"], True)
    check("…e forme diverse", a["forma"]["id"] != b["forma"]["id"], True)
    check("stesso slug e stesso seed → stesso lock",
          cl.costruisci("hotel-mare", "2026072715", {})["colore"]["id"],
          a["colore"]["id"])
    check("lo slug entra nel seed", "hotel-mare" in a["seed"], True)

    # il clic dell'owner atterra nel lock
    scelto = cl.applica_scelte(cl.costruisci("x", "2026072715", {}), ["colore=cobalto"])
    check("la scelta dell'owner sovrascrive", scelto["colore"]["id"], "cobalto")
    check("e resta scritto chi ha deciso", scelto["colore"]["scelto_da"], "owner")

    # il confronto nomina lo scostamento
    rep = {"accent": {"hex": "#db7055", "famiglia": "rosso"},
           "typefaces": {"display": "Fraunces"},
           "layout": {"radius_family": "pill"}}
    lock = {"colore": {"id": "ottanio", "famiglia": "verde"},
            "font": {"display": "Petrona"},
            "forma": {"id": "soft-pieno", "radius_family": "soft"}}
    sc = cl.scostamenti(lock, rep)
    check("il confronto trova i tre scostamenti", len(sc), 3)
    check("e nomina il colore atteso e quello trovato",
          any("ottanio" in s and "db7055" in s for s in sc), True)
    check("una pagina conforme non produce scostamenti",
          cl.scostamenti(lock, {"accent": {"hex": "#33a8b3", "famiglia": "verde"},
                                "typefaces": {"display": "Petrona"},
                                "layout": {"radius_family": "soft"}}), [])

    # --- gli edge case, tutti misurati prima di essere corretti ---------------
    # E1. `slug in s` era una SOTTOSTRINGA: `--project hotel` con seed
    # `…-hotel-mare` vedeva «hotel» dentro, non aggiungeva niente, e i due
    # progetti ricevevano lo stesso identico seed — la collisione che il lock
    # esiste per chiudere, rientrata dalla finestra.
    check("slug diverso, seed diverso anche quando uno contiene l'altro",
          cl.semina("2026072715-hotel-mare", "hotel")
          != cl.semina("2026072715-hotel-mare", "hotel-mare"), True)
    check("un seed gia' completo non si allunga due volte",
          cl.semina("2026072715-hotel-mare", "hotel-mare"), "2026072715-hotel-mare")
    check("e i due progetti ricevono colori diversi",
          cl.costruisci("hotel", "2026072715-hotel-mare", {})["colore"]["id"]
          != cl.costruisci("hotel-mare", "2026072715-hotel-mare", {})["colore"]["id"], True)

    # E2. la riga la copia l'owner dal selettore: la maiuscola non e' un errore
    check("l'id dell'owner si accetta in maiuscolo",
          cl.applica_scelte(cl.costruisci("x", "2026072715-x", {}),
                            ["colore=COBALTO"])["colore"]["id"], "cobalto")

    # E3. due valori per lo stesso asse: uno si perdeva in silenzio
    try:
        cl.applica_scelte(cl.costruisci("x", "2026072715-x", {}),
                          ["colore=cobalto", "colore=lacca"])
        check("un asse scelto due volte viene rifiutato", False, True)
    except SystemExit as exc:
        check("un asse scelto due volte viene rifiutato", "due volte" in str(exc), True)

    # E4. confrontava la FAMIGLIA, non la scelta: `granata` al posto di `lacca`
    # passava liscio. E la sola misura angolare non basterebbe — `zafferano` e
    # `sabbia` distano 2°, `senape` e `grano` 1.9°: sono zone diverse del
    # catalogo che nessun angolo separa. Il valore esatto le separa tutte.
    rosso = {"colore": {"id": "lacca", "famiglia": "rosso", "accent": "#b7502f"}}
    pag = {"accent": {"hex": "#a33a3f", "famiglia": "rosso"}}
    sc = cl.scostamenti(rosso, pag, "<style>--accent:#a33a3f</style>")
    check("un altro rosso al posto di quello del lock e' uno scostamento", len(sc), 1)
    check("e nomina l'atteso e il trovato",
          "lacca" in sc[0] and "a33a3f" in sc[0], True)
    check("due zone a 2° di distanza non si confondono piu'",
          len(cl.scostamenti({"colore": {"id": "zafferano", "famiglia": "terra",
                                         "accent": "#c8892b"}},
                             {"accent": {"hex": "#c9a678", "famiglia": "terra"}},
                             "<style>--accent:#c9a678</style>")), 1)
    check("la pagina che porta il valore del lock passa",
          cl.scostamenti(rosso, {"accent": {"hex": "#b7502f", "famiglia": "rosso"}},
                         "<style>--accent:#B7502F</style>"), [])
    check("un colore identico scritto in hsl() non e' uno scostamento",
          cl.scostamenti(rosso, {"accent": {"hex": "#b7502f", "famiglia": "rosso"}},
                         "a{--accent:hsl(15 59% 45%)}"), [])
    check("anche scritto in rgb()",
          cl.scostamenti(rosso, {"accent": {"hex": "#c25a38", "famiglia": "rosso"}},
                         "a { color: rgb(183, 80, 47); }"), [])
    check("e senza testo si ricade sulla tinta invece di accusare",
          cl.scostamenti(rosso, {"accent": {"hex": "#c25a38", "famiglia": "rosso"}}), [])

    # E5. il silenzio passava: non dichiarare niente era il modo piu' semplice
    # di superare il cancello.
    muta = cl.scostamenti(lock, {"colours": [], "accent": {}, "typefaces": {}, "layout": {}})
    check("una pagina che non dichiara niente non passa piu'", len(muta), 3)
    check("il mono assente resta tollerato (una landing puo' non usarlo)",
          any("mono" in s for s in muta), False)
    check("con report vuoto tace: lo dice gia' `non misurabile`",
          cl.scostamenti(lock, {}), [])

    # E6. effetti e hero: scritti nel lock e letti da nessuno — inerti, la
    # stessa classe di `--prefer`.
    mot = {"effetti": ["curtain-up", "blur-in"], "hero": {"id": "h07"}}
    check("gli effetti del lock assenti dalla pagina sono uno scostamento",
          any("curtain-up" in s for s in cl.scostamenti(mot, {"a": 1}, "<html>niente</html>")), True)
    check("l'hero non firmato e' uno scostamento",
          any("hero" in s for s in cl.scostamenti(mot, {"a": 1}, "<html>niente</html>")), True)
    check("una pagina che li porta davvero non produce scostamenti",
          cl.scostamenti(mot, {"a": 1},
                         '<section data-hero="h07" class="fx-curtain-up blur-in">'), [])
    check("senza testo tace invece di accusare",
          cl.scostamenti(mot, {"a": 1}), [])

    # E7. gli id si cercano come TOKEN: dieci id del catalogo sono contenuti in
    # un altro, e con `in` nudo il lock che diceva `pin` si accontentava di uno
    # `spinner`.
    check("`pin` non si accontenta di uno `spinner`",
          any("pin" in s for s in
              cl.scostamenti({"effetti": ["pin"]}, {"a": 1}, '<div class="spinner">')), True)
    check("ma `.fx-pin` vale",
          cl.scostamenti({"effetti": ["pin"]}, {"a": 1}, '<div class="fx-pin">'), [])

    # E8. un lock legittimo senza cataloghi porta `{"non_sorteggiati": …}`:
    # iterarci sopra dava le chiavi, e accusava la pagina di non avere un
    # effetto chiamato «non_sorteggiati».
    check("un lock senza cataloghi non produce accuse fasulle",
          cl.scostamenti({"effetti": {"non_sorteggiati": "x"}}, {"a": 1}, "<html></html>"), [])
    check("un campo non-stringa si dichiara invece di esplodere",
          "lock da rifare" in
          " ".join(cl.scostamenti({"font": {"display": 123}},
                                  {"typefaces": {"display": "Inter"}})), True)

    # E9. la tenda e l'hero sono regole da LANDING: imporle a un back office
    # significa bocciare una dashboard perche' non ha una tenda.
    land = cl.costruisci("backoffice", "2026072715", {}, "marketing")
    dash = cl.costruisci("backoffice", "2026072715", {}, "dashboard")
    check("su una landing la tenda c'e' sempre",
          any(str(e).startswith("curtain") for e in land["effetti"]), True)
    check("su una dashboard non si impone", "hero" in dash, False)
    check("e la superficie resta scritta nel lock", dash["surface"], "dashboard")

    # E10. il peso per famiglia: il catalogo ha 8 zone verdi e 2 viola, e senza
    # il peso il verde usciva 27% contro il 5% del viola — la «predominanza del
    # verde» che l'owner vedeva. Acceso contro spento devono differire.
    # Il campione e' 300, non 120: con sette famiglie e 120 tiri la deviazione
    # e' di ~4 punti, e una soglia stretta boccia il caso perche' e' caso.
    import collections as _c
    N = 300
    fam = _c.Counter(cl.costruisci(f"p-{i}", "2026072715", {})["colore"]["famiglia"]
                     for i in range(N))
    grezzo = _c.Counter(ap.suggerisci(1, f"2026072715-p-{i}", [])[0]["famiglia"]
                        for i in range(N))
    check("senza peso una famiglia domina", max(grezzo.values()) / N > 0.24, True)
    check("col peso nessuna famiglia supera un quinto",
          max(fam.values()) / N <= 0.20, True)
    check("e nessuna resta sotto un decimo", min(fam.values()) / N >= 0.10, True)
    check("il divario fra la piu' e la meno frequente si dimezza",
          (max(fam.values()) / min(fam.values()))
          < (max(grezzo.values()) / min(grezzo.values())) / 2, True)
    check("il sorteggio resta deterministico",
          cl.costruisci("p-1", "2026072715", {})["colore"]["id"],
          cl.costruisci("p-1", "2026072715", {})["colore"]["id"])

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
