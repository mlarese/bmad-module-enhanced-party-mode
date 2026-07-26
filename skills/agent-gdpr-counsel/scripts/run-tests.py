#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""La suite di questo skill in un comando, più un lint che cerca il codice inerte.

Sta **dentro lo skill**, come `wake.py` e `init-sanctum.py`: quello che è di uno
skill viaggia con lui, o un'installazione del modulo si ritrova senza il modo di
verificarsi.

Perché esiste, misurato. In una sola sessione di lavoro sono successe quattro
cose, tutte della stessa famiglia:

  · un'opzione (`--prefer`) aggiunta ad argparse e **mai passata** alla funzione
    che doveva usarla: veniva letta e ignorata, e con o senza usciva lo stesso
    identico risultato;
  · un test scritto sotto `if __name__ == "__main__"` e quindi **mai chiamato**:
    la suite restava verde e il test non girava;
  · tre release consegnate sopra una suite **rossa**, perché i test si
    lanciavano a mano e quella volta non li ha lanciati nessuno;
  · una corsa di test che ha scritto 22 finte consegne nel registro di craft
    **vero**, perché il suo default sta in `$HOME`.

Nessuna di queste si vede rileggendo il diff: il codice sembra giusto e l'output
sembra giusto. Si vedono solo eseguendo, e confrontando.

Da qui le due cose che fa:

  1. **esegue** `scripts/tests/test-*.py` di questo skill, col registro isolato,
     e esce diverso da zero se una sola è rossa;
  2. **lint di cablaggio** — le due forme di codice inerte che sono
     meccanicamente rilevabili: un'opzione CLI che nessuno legge, e una funzione
     di test che nessuno chiama.

Quello che il lint **non** può sorvegliare, e resta disciplina di chi scrive:
ogni nuovo interruttore, peso o regola nasce con un **test differenziale** —
acceso contro spento devono differire, nella direzione dichiarata. È la misura
100% contro 21% che ha smascherato `--prefer`, e non si supera per caso.

Usage:
    uv run scripts/run-tests.py            # suite + lint
    uv run scripts/run-tests.py --lint     # solo il lint (veloce)
    uv run scripts/run-tests.py --tests    # solo la suite

Exit: 0 tutto verde · 1 qualcosa è rosso.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent

# --- lint --------------------------------------------------------------------

# Il lint legge l'**albero sintattico**, non il testo. Con le espressioni
# regolari una fixture dentro una stringa — `def test_x()` scritto in un test che
# verifica il lint — era indistinguibile da codice vero, e il primo file
# segnalato è stato proprio quello. Con `ast` la classe intera sparisce: una
# stringa non è una definizione.


def _dest(flag: str, kw: list[ast.keyword]) -> str:
    for k in kw:
        if k.arg == "dest" and isinstance(k.value, ast.Constant):
            return str(k.value.value)
    return flag.lstrip("-").replace("-", "_")


def lint_text(text: str, etichetta: str) -> list[str]:
    """Opzioni che nessuno legge, funzioni di test che nessuno chiama."""
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [f"{etichetta}: non si compila ({exc.msg} alla riga {exc.lineno})"]

    out: list[str] = []
    letti: set[str] = set()          # args.x letti
    passthrough = False              # vars(args) / **vars(...)
    gruppi: dict[str, str] = {}      # nome della variabile → sé stessa
    opzioni: list[tuple[str, str, str]] = []   # (ricevente, flag, dest)
    definiti: list[str] = []
    chiamati: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id == "args":
            letti.add(node.attr)
        elif isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id == "vars":
                passthrough = True
            if isinstance(f, ast.Name):
                chiamati.add(f.id)
            elif isinstance(f, ast.Attribute):
                if f.attr == "add_argument" and node.args \
                        and isinstance(node.args[0], ast.Constant) \
                        and str(node.args[0].value).startswith("--"):
                    flag = str(node.args[0].value)
                    recv = f.value.id if isinstance(f.value, ast.Name) else ""
                    if flag != "--help":
                        opzioni.append((recv, flag, _dest(flag, node.keywords)))
            if isinstance(f, ast.Name) and f.id == "getattr" and len(node.args) > 1 \
                    and isinstance(node.args[1], ast.Constant):
                letti.add(str(node.args[1].value))
        elif isinstance(node, ast.Assign):
            v = node.value
            if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) \
                    and v.func.attr == "add_mutually_exclusive_group":
                for t_ in node.targets:
                    if isinstance(t_, ast.Name):
                        gruppi[t_.id] = t_.id
        elif isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            definiti.append(node.name)

    if not passthrough:
        coperti = {g for g in gruppi
                   if any(d in letti for r, _, d in opzioni if r == g)}
        for recv, flag, dest in opzioni:
            if recv in coperti or dest in letti:
                continue
            out.append(f"{etichetta}: l'opzione `{flag}` è dichiarata ma "
                       f"`args.{dest}` non compare mai — viene letta e ignorata")

    for name in definiti:
        if name not in chiamati:
            out.append(f"{etichetta}: `{name}()` è definita ma non la chiama nessuno "
                       "— la suite resta verde e il test non gira")
    return out


def run_lint(skill: Path = SKILL) -> list[str]:
    trovati: list[str] = []
    for p in sorted((skill / "scripts").glob("**/*.py")):
        if "__pycache__" in p.parts:
            continue
        trovati += lint_text(p.read_text(encoding="utf-8", errors="replace"),
                             str(p.relative_to(skill)))
    return trovati


# --- suite -------------------------------------------------------------------

def run_suites(skill: Path = SKILL) -> tuple[int, list[str]]:
    """I test girano dalla radice dello skill, com'è scritto per fare.

    Il registro dei settori sta in `$HOME` di default: senza isolarlo, una corsa
    dei test scrive nella storia di craft vera. È già successo, 22 volte.
    """
    rossi: list[str] = []
    tot = 0
    with tempfile.TemporaryDirectory(prefix="suite-ledger-") as td:
        env = {**os.environ, "VESPER_CRAFT_LEDGER": str(Path(td) / "ledger.json")}
        for test in sorted((skill / "scripts" / "tests").glob("test-*.py")):
            tot += 1
            r = subprocess.run([sys.executable, str(test)], cwd=skill,
                               env=env, capture_output=True, text=True)
            rotto = r.returncode != 0 or re.search(r"^FAIL", r.stdout, re.M)
            print(f"  {'ROSSO' if rotto else '  ok '}  {test.name}")
            if rotto:
                rossi.append(test.name)
                for l in [x for x in r.stdout.splitlines()
                          if x.startswith(("FAIL", "  atteso", "  ottenuto"))][:6]:
                    print(f"          {l}")
                if r.stderr.strip():
                    print(f"          {r.stderr.strip().splitlines()[-1]}")
    return tot, rossi


def main() -> int:
    ap = argparse.ArgumentParser(description="Suite di questo skill + lint di cablaggio")
    ap.add_argument("--lint", action="store_true", help="solo il lint")
    ap.add_argument("--tests", action="store_true", help="solo la suite")
    args = ap.parse_args()

    rossi: list[str] = []
    if not args.lint:
        print(f"# Suite — {SKILL.name}\n")
        tot, rossi = run_suites()
        print(f"\n{tot} file · {'tutti verdi' if not rossi else f'{len(rossi)} rossi'}\n")

    trovati: list[str] = []
    if not args.tests:
        print("# Lint di cablaggio\n")
        trovati = run_lint()
        for f in trovati:
            print(f"  ! {f}")
        print(f"  {'niente codice inerte' if not trovati else f'{len(trovati)} rilievi'}\n")

    if rossi or trovati:
        print("**Non si rilascia così.** Una suite rossa o un'opzione che nessuno legge "
              "non si vedono rileggendo il diff: si vedono solo qui.")
        return 1
    print("Si rilascia.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
