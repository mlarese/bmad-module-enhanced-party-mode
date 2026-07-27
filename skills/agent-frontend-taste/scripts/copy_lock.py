#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Il lessico del dominio, raccolto **prima** di scrivere una riga di copy.

Stessa forma del craft-lock, altro materiale: là le decisioni di design, qui le
parole che il mestiere usa davvero. La ragione e' la diagnosi del consiglio del
2026-07-27 — il traduzionese non e' un difetto di lingua ma di **provenienza**.
Il copy fisso del catalogo hero tiene perche' chi l'ha scritto guardava un
archivio vero; il copy generato dal nulla ripiega sul vocabolario
internazionale della landing, che in italiano non parla nessuno.

Il corpus e' quello che si e' gia' letto per il lavoro: il sito del cliente, la
ricerca di dominio, il PRD, i materiali che l'owner ha dato. Da li' si estraggono
i sostantivi e i verbi del mestiere — `mezza pensione`, `caparra`, `navetta`,
`sala lettura` — e alla consegna `copy_check` verifica che i titoli li usino.

Non e' un vincolo sul come si scrive: **almeno una parola del dominio per
titolo**. Chi scrive resta libero di metterla in una frase che il mestiere non
avrebbe scritto — «Cento anni di carte, una stanza» contiene `carte` e `stanza`,
e non e' una frase da archivista.

Usage:
    uv run scripts/copy_lock.py --project hotel-mare --corpus ricerca.md sito.txt \\
        --out apps/hotel-mare/copy-lock.json
    uv run scripts/copy_lock.py --project … --termini "mezza pensione,caparra,navetta" \\
        --out apps/…/copy-lock.json
    uv run scripts/copy_lock.py --show apps/hotel-mare/copy-lock.json

Exit: 0 scritto · 1 corpus illeggibile o lessico troppo povero · 2 argomenti mancanti.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MINIMO = 8  # sotto questa soglia non e' un lessico, e' una manciata di parole


def _bmad_context():
    spec = importlib.util.spec_from_file_location("bmad_context", HERE / "bmad_context.py")
    if not spec or not spec.loader:
        return None
    m = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("bmad_context", m)
    spec.loader.exec_module(m)
    return m


def dal_progetto(root: Path) -> list[Path]:
    """Il corpus si trova da solo: la ricerca e' gia' su disco.

    Il consiglio scrive ricerca di dominio e ricerca di marketing in
    `planning-artifacts/` — «una ricerca usata e persa» e' la ragione per cui ci
    finiscono. Chiedere a chi esegue di **elencare a mano** quei file era la
    fragilita' dei cataloghi che nessuno lanciava: se dipende dal ricordarsi,
    prima o poi non succede, e il lessico resta vuoto senza che nessuno lo noti.

    Si legge la config del progetto per `planning_artifacts`, come fa il
    pre-flight, invece di indovinare il percorso.
    """
    root = Path(root)
    cartelle: list[Path] = []
    bc = _bmad_context()
    if bc is not None:
        try:
            pian, impl = bc.read_config_paths(root)
            cartelle += [pian, impl]
        except Exception:
            pass
    cartelle += [root / "docs", root / "planning-artifacts",
                 root / "_bmad-output" / "planning-artifacts"]

    visti, out = set(), []
    for c in cartelle:
        if not c or not Path(c).is_dir():
            continue
        for f in sorted(Path(c).rglob("*.md")):
            r = f.resolve()
            if f.is_file() and r not in visti:
                visti.add(r)
                out.append(f)
    for nome in ("project-context.md", "CLAUDE.md", "AGENTS.md", "README.md"):
        f = root / nome
        if f.is_file() and f.resolve() not in visti:
            visti.add(f.resolve())
            out.append(f)
    return out


def _cc():
    spec = importlib.util.spec_from_file_location("copy_check", HERE / "copy_check.py")
    if not spec or not spec.loader:
        raise SystemExit("copy_check.py non trovato accanto a copy_lock.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("copy_check", m)
    spec.loader.exec_module(m)
    return m


def da_corpus(testi: list[str], quante: int = 200) -> list[str]:
    """Tutte le parole piene del corpus, le piu' frequenti per prime.

    Niente analisi grammaticale: la frequenza basta e non ha dipendenze.

    **Il lessico e' generoso di proposito.** La prima versione teneva solo le
    parole ripetute, per togliere il rumore, e su una scheda di ricerca di dieci
    righe buttava via `navetta` — che nel corpus c'era una volta sola — cosi' il
    titolo «Navetta dalla stazione» finiva accusato di non parlare del dominio.
    Un falso positivo su un titolo giusto, cioe' il difetto che si era detto di
    non rifare. Il mordente non viene dalla ristrettezza dell'elenco: viene dal
    fatto che una headline tradotta non contiene **nessuna** parola del
    mestiere, per quanto lungo sia l'elenco.
    """
    cc = _cc()
    conta: Counter[str] = Counter()
    for t in testi:
        conta.update(cc.elenco_parole(cc.testo_visibile(t)))
    return [p for p, _ in conta.most_common(quante)]


def costruisci(slug: str, corpus: list[Path], termini: list[str]) -> dict:
    testi = []
    for f in corpus:
        if not f.is_file():
            raise SystemExit(f"{f} non esiste")
        try:
            testi.append(f.read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            raise SystemExit(f"{f} illeggibile: {exc}")

    a_mano = [t.strip().lower() for t in termini if t.strip()]
    estratte = da_corpus(testi) if testi else []
    # I termini dichiarati a mano vengono prima: sono la parola dell'owner.
    lessico, visti = [], set()
    for p in a_mano + estratte:
        for pezzo in re.split(r"[\s,;]+", p):
            pezzo = pezzo.strip().lower()
            if len(pezzo) >= 3 and pezzo not in visti:
                visti.add(pezzo)
                lessico.append(pezzo)
    return {"project": slug, "fonti": [str(f) for f in corpus],
            "documenti_letti": len(corpus),
            "dichiarati": a_mano, "lessico": lessico}


def main() -> int:
    ap = argparse.ArgumentParser(description="Il lessico del dominio, raccolto prima")
    ap.add_argument("--project", help="slug del progetto")
    ap.add_argument("--corpus", nargs="*", default=[],
                    help="i file gia' letti per il lavoro: ricerca, sito del cliente, PRD")
    ap.add_argument("--da-progetto", metavar="ROOT",
                    help="raccoglie da solo ricerca, PRD e documenti da "
                         "planning-artifacts/ — la ricerca del consiglio e' gia' li'")
    ap.add_argument("--termini", default="",
                    help="parole del mestiere, separate da virgola — vengono prima")
    ap.add_argument("--out", help="apps/<slug>/copy-lock.json")
    ap.add_argument("--show", metavar="FILE", help="stampa un lessico esistente")
    args = ap.parse_args()

    if args.show:
        p = Path(args.show)
        if not p.is_file():
            print(f"nessun lessico in {p}", file=sys.stderr)
            return 1
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            print(f"{p} non e' leggibile come lessico: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(d, ensure_ascii=False, indent=1))
        return 0

    if not args.project or not args.out:
        print("servono --project e --out (o --show)", file=sys.stderr)
        return 2

    corpus = [Path(c) for c in args.corpus]
    if args.da_progetto:
        trovati = dal_progetto(Path(args.da_progetto))
        if not trovati:
            print(f"! in {args.da_progetto} non c'e' nessun documento da leggere: "
                  "la ricerca del consiglio si scrive in planning-artifacts/",
                  file=sys.stderr)
        corpus += [f for f in trovati if f not in corpus]
    lock = costruisci(args.project, corpus, args.termini.split(","))
    if len(lock["lessico"]) < MINIMO:
        print(f"lessico troppo povero ({len(lock['lessico'])} parole): dai un corpus "
              "vero — la ricerca di dominio, il sito del cliente — o elenca i termini "
              "con --termini. Un lessico vuoto non vincola niente.", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(lock, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{out}")
    print(f"  {len(lock['lessico'])} parole del mestiere"
          + (f", {len(lock['dichiarati'])} dichiarate a mano" if lock["dichiarati"] else ""))
    print("  " + ", ".join(lock["lessico"][:14]) + ("…" if len(lock["lessico"]) > 14 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
