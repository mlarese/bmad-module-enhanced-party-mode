#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Italiano scritto contro italiano tradotto — i due lati della misura.

Il test che tiene in piedi tutto e' il primo: **le 75 stringhe di copy buono del
catalogo hero devono restare pulite**. Un marcatore che accusa «Cento anni di
carte, una stanza» non e' severo, e' rotto — e il modo piu' rapido di insegnare
a ignorare il referto. Il secondo lato e' il differenziale: le frasi tradotte
devono essere prese quasi tutte, o la misura non misura niente.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
_ISO = Path(tempfile.mkdtemp(prefix="copy-test-"))

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


# Frasi che in italiano nessuno direbbe: sono inglese con le scarpe italiane.
TRADOTTE = [
    "Scopri di più sulla nostra struttura",
    "Prenota la tua vacanza da sogno",
    "Inizia ora il tuo percorso",
    "Soluzioni su misura per il tuo business",
    "Noi crediamo nell'ospitalità",
    "Che tu sia in viaggio di lavoro o in famiglia",
    "Il partner ideale per il tuo evento",
    "Un'esperienza unica ti aspetta",
    "Tecnologia all'avanguardia",
    "Ecco perché ci scelgono in tanti",
    "Alimentato da energia solare",
    "Il modo migliore per organizzare il soggiorno",
    "Porta il tuo hotel al prossimo livello",
    "Non si tratta di dormire, ma di ricaricarsi",
    "Oggi più che mai serve un partner",
    "Sblocca tutte le funzionalità",
    "Potenzia il tuo business",
    "Progettato per offrirti il meglio",
    "La scelta giusta per la tua famiglia",
    "Un servizio senza soluzione di continuità",
]

CORPUS = """Hotel Bellavista, Riva del Garda. Struttura a conduzione familiare,
34 camere. Mezza pensione e pensione completa. La caparra si versa alla
prenotazione, il saldo alla partenza. Navetta dalla stazione su richiesta.
Reception aperta dalle 7 alle 22, check-in dalle 14. Camera doppia uso singola
fuori stagione. Sala colazioni con prodotti del lago. Il ristorante propone
carne salada e pesce di lago. Parcheggio coperto, deposito bici con officina.
Spiaggia convenzionata a 200 metri. Escursioni al Monte Brione."""


def main() -> int:
    cc = load("copy_check")
    cl = load("copy_lock")

    # --- il lato che conta: il copy buono resta pulito -----------------------
    catalogo = json.loads((SCRIPTS.parent / "assets" / "hero-catalog.json")
                          .read_text(encoding="utf-8"))
    buone: list[str] = []

    def raccogli(o) -> None:
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("copy", "headline", "kicker", "sub", "cta", "eyebrow",
                         "title") and isinstance(v, str):
                    buone.append(v)
                else:
                    raccogli(v)
        elif isinstance(o, list):
            for x in o:
                raccogli(x)

    raccogli(catalogo)
    check("il catalogo hero ha copy da controllare", len(buone) >= 50, True)
    falsi = [(t, [m["id"] for m in cc.marcatori(t)]) for t in buone if cc.marcatori(t)]
    check("nessun falso positivo sul copy buono del catalogo", falsi, [])

    # --- e il differenziale: il tradotto viene preso -------------------------
    presi = [t for t in TRADOTTE if cc.marcatori(t)]
    check("il copy tradotto viene riconosciuto", len(presi), len(TRADOTTE))
    check("il referto nomina l'originale inglese",
          "learn more" in cc.marcatori("Scopri di più")[0]["inglese"], True)
    check("e dice cosa scrivere invece",
          bool(cc.marcatori("Prenota la tua vacanza")[0]["invece"]), True)

    # --- il lessico del dominio ---------------------------------------------
    corpus = _ISO / "ricerca.md"
    corpus.write_text(CORPUS, encoding="utf-8")
    lock = cl.costruisci("hotel-bellavista", [corpus], ["carne salada"])
    check("il lessico si raccoglie dal corpus", len(lock["lessico"]) >= 20, True)
    check("le parole del mestiere ci sono",
          {"navetta", "caparra", "reception", "pensione"} <= set(lock["lessico"]), True)
    check("i termini dichiarati a mano vengono per primi",
          lock["lessico"][0], "carne")

    # `navetta` compare una volta sola nel corpus: la prima versione la buttava
    # via, e il titolo giusto «Navetta dalla stazione» finiva accusato.
    buona = """<html><body><h1>Trentaquattro camere sopra il lago</h1>
      <h2>La mezza pensione, con la carne salada del giovedì</h2>
      <h2>Navetta dalla stazione, se ci scrivi il treno</h2>
      <a href="#p">Chiedi il preventivo</a></body></html>"""
    check("una pagina scritta in italiano non produce niente",
          cc.problemi(buona, lock["lessico"]), [])

    tradotta = """<html><body><h1>Scopri di più sulla tua vacanza da sogno</h1>
      <h2>Un'esperienza unica ti aspetta</h2>
      <a href="#p">Inizia ora</a></body></html>"""
    guai = cc.problemi(tradotta, lock["lessico"])
    check("una pagina tradotta viene presa", len(guai) >= 4, True)
    check("e si dice quale titolo non parla del dominio",
          any("qualunque cliente" in g for g in guai), True)

    # Senza lessico i marcatori girano lo stesso: non dipendono da niente.
    check("i marcatori girano anche senza lessico",
          len(cc.problemi(tradotta, [])) >= 3, True)
    check("e senza lessico nessun titolo viene accusato",
          any("qualunque cliente" in g for g in cc.problemi(buona, [])), False)

    # --- le CTA non portano il vincolo del lessico --------------------------
    # Sono corte per mestiere: «Chiedi il preventivo» e' giusto e non contiene
    # nessuna parola del corpus.
    solo_cta = '<html><body><a href="#x">Chiedi il preventivo</a></body></html>'
    check("le CTA non vengono accusate di non parlare del dominio",
          cc.problemi(solo_cta, lock["lessico"]), [])

    # --- il corpus si trova da solo -----------------------------------------
    # Chiedere di elencare a mano i file della ricerca era la fragilita' dei
    # cataloghi che nessuno lanciava: se dipende dal ricordarsi, prima o poi non
    # succede e il lessico resta vuoto senza che nessuno se ne accorga. La
    # ricerca del consiglio e' gia' su disco, in planning-artifacts/.
    finto = _ISO / "progetto"
    (finto / "_bmad-output" / "planning-artifacts").mkdir(parents=True, exist_ok=True)
    (finto / "_bmad-output" / "planning-artifacts" / "ricerca-dominio.md").write_text(
        CORPUS, encoding="utf-8")
    trovati = cl.dal_progetto(finto)
    check("la ricerca su disco viene trovata senza elencarla", len(trovati) >= 1, True)
    auto = cl.costruisci("x", trovati, [])
    check("e da sola riempie il lessico",
          {"navetta", "caparra", "reception"} <= set(auto["lessico"]), True)
    check("mentre senza corpus il lessico resta vuoto",
          cl.costruisci("x", [], [])["lessico"], [])
    vuoto_dir = _ISO / "progetto-vuoto"
    vuoto_dir.mkdir(parents=True, exist_ok=True)
    check("un progetto senza documenti non inventa niente",
          cl.dal_progetto(vuoto_dir), [])

    # --- un lessico povero si rifiuta invece di fingere ----------------------
    try:
        vuoto = cl.costruisci("x", [], [])
        check("senza corpus il lessico e' vuoto", vuoto["lessico"], [])
    except SystemExit as exc:
        check("senza corpus si dichiara invece di esplodere", "corpus" in str(exc), True)

    # --- l'estrazione contava per DOCUMENTO, non per occorrenza -------------
    # `parole()` restituisce un set: sommando set, con un corpus di un file solo
    # ogni parola usciva a 1 e il lessico restava vuoto.
    doppio = cc.elenco_parole("reception reception navetta")
    check("le occorrenze si contano davvero", doppio.count("reception"), 2)
    check("mentre l'insieme resta un insieme",
          len(cc.parole("reception reception navetta")), 2)

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
