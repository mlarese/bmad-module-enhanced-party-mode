#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Il lint deve prendere i due bug per cui è nato — o dice sempre «tutto bene».

Un controllo che non fallisce mai è indistinguibile da un controllo assente, e
questo in particolare nasce per sorvegliare il codice inerte: sarebbe una beffa
se diventasse lui il primo pezzo inerte del repo.

Perciò qui non si verifica che il lint «funzioni»: si riproducono i **due difetti
storici** e si pretende che li nomini, e si verifica che sull'albero vero non
inventi allarmi.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "run-tests.py"
SKILL = SCRIPT.parent.parent

fails = 0


def check(label: str, got, want=True) -> None:
    global fails
    if got == want:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}\n  atteso: {want}\n  ottenuto: {got}")
        fails += 1


def load():
    spec = importlib.util.spec_from_file_location("run_tests", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_tests"] = mod
    spec.loader.exec_module(mod)
    return mod


# Il difetto numero uno: l'opzione dichiarata e mai passata a valle.
OPZIONE_MORTA = '''
import argparse
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed")
    p.add_argument("--prefer", help="la lista dei preferiti")
    args = p.parse_args()
    print(args.seed)
'''

# Il difetto numero due: il test definito e mai chiamato.
TEST_MORTO = '''
def main():
    print("PASS: qualcosa")
    return 0
def test_preferiti():
    assert False
if __name__ == "__main__":
    raise SystemExit(main())
'''

# Il falso allarme del primo giro: gruppo mutuamente esclusivo, il codice si
# dirama sul fratello e l'altro è il ramo `else`.
GRUPPO_ESCLUSIVO = '''
import argparse
def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--build", action="store_true")
    g.add_argument("--stats", action="store_true")
    args = p.parse_args()
    if args.stats:
        return 0
    return 1
'''

# Il namespace passato intero a valle: `args.x` non compare per forza.
PASSTHROUGH = '''
import argparse
def build(**kw): pass
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target")
    args = p.parse_args()
    build(**vars(args))
'''


def main() -> int:
    mod = load()

    trovato = mod.lint_text(OPZIONE_MORTA, "finto.py")
    check("prende l'opzione dichiarata e mai letta", len(trovato), 1)
    check("e la nomina", "--prefer" in (trovato[0] if trovato else ""))

    trovato = mod.lint_text(TEST_MORTO, "test-finto.py")
    check("prende il test definito e mai chiamato", len(trovato), 1)
    check("e lo nomina", "test_preferiti" in (trovato[0] if trovato else ""))

    check("non inventa allarmi sui gruppi esclusivi",
          mod.lint_text(GRUPPO_ESCLUSIVO, "finto.py"), [])
    check("né quando il namespace passa intero a valle",
          mod.lint_text(PASSTHROUGH, "finto.py"), [])

    # Sull'albero vero: zero rilievi, o il lint sta gridando al lupo.
    check("nessun codice inerte in questo skill", mod.run_lint(SKILL), [])

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
