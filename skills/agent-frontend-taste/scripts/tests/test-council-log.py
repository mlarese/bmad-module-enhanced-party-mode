# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for council_log.py — run: uv run scripts/tests/test-council-log.py

La regola sotto test: il registro dice **chi c'era**, e in ciclo rapido
(`references/ciclo-rapido.md`) deve dire che non c'era nessuno.

Il difetto che questi test intercettano è quello di sempre in questo skill: un
interruttore aggiunto e mai cablato. `--goal rapido` *sembrava* funzionare anche
senza toccare `GOALS` — argparse lo accetta, la riga si scrive, l'output è
plausibile — solo che nel registro finiva la parola nuda «rapido», che si legge
come il nome di una seduta veloce invece che come la sua assenza. Acceso contro
spento si vede solo confrontando le due righe, non rileggendo il diff.

E il secondo test chiude l'anello vero: `close_check` non fa consegnare senza
registro, quindi se la riga del ciclo rapido non passasse il suo controllo, il
ciclo rapido non potrebbe consegnare **niente** — e lo si scoprirebbe alla prima
consegna vera, non qui.
"""
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
SCRIPT = SCRIPTS / "council_log.py"
CLOSE = SCRIPTS / "close_check.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def main() -> int:
    fails = 0
    mod = load(SCRIPT, "council_log")
    close = load(CLOSE, "close_check")

    def check(label, got, want=True):
        nonlocal fails
        if got == want:
            print(f"PASS: {label}")
        else:
            print(f"FAIL: {label}\n  atteso: {want}\n  ottenuto: {got}")
            fails += 1

    # --- differenziale: rapido contro seduta vera ----------------------------
    # Acceso contro spento devono **differire**, nella direzione dichiarata: la
    # riga del ciclo rapido deve dire che seduta non ce n'è stata, non essere una
    # seduta con un nome diverso.
    rapido = mod.normalise_goal("rapido")
    g1 = mod.normalise_goal("G1")
    check("rapido e G1 non scrivono la stessa cosa", rapido != g1)
    check("rapido dice che non si è seduto nessuno",
          "nessuna seduta" in rapido)
    check("rapido non resta la parola nuda", rapido != "rapido")
    check("G1 resta quello che era", g1, "G1 lettura")
    check("un obiettivo sconosciuto passa come testo libero",
          mod.normalise_goal("mezzogiro"), "mezzogiro")

    # --- l'anello vero: la riga del ciclo rapido regge close_check -----------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        registro = root / "docs" / "consiglio" / "trattoria.md"

        # spento: nessun registro → non si consegna
        ok, _ = close.check_council(registro)
        check("senza registro close_check non fa consegnare", ok, False)

        r = run(str(root), "--project", "trattoria", "--goal", "rapido",
                "--agents", "Vesper",
                "--outcome", "ciclo rapido scelto dall'owner: brief in 6 righe, nessuna seduta")
        check("CLI: la riga del ciclo rapido si scrive", r.returncode, 0)

        # acceso: la riga esiste → si consegna
        ok, problemi = close.check_council(registro)
        check("con la riga del ciclo rapido close_check fa consegnare", ok, problemi == [] and ok)

        testo = registro.read_text(encoding="utf-8")
        # L'**etichetta** — fra `- **` e `**` — è l'unico pezzo che dipende da
        # GOALS. Cercare «ciclo rapido» in tutto il file passerebbe anche a
        # interruttore spento, perché quelle parole stanno già nell'--outcome
        # che scrive il chiamante: sarebbe un test che misura la propria fixture.
        etichetta = [l.split("**")[1] for l in testo.splitlines() if l.startswith("- **")][-1]
        check("l'etichetta della riga nomina il ciclo rapido", "ciclo rapido" in etichetta)
        check("e dice che non c'è stata seduta", "nessuna seduta" in etichetta)
        check("e la riga dice chi ha deciso", "Vesper" in testo)

        # `--check` legge lo stesso registro
        check("--check trova la seduta registrata",
              run(str(root), "--project", "trattoria", "--check").returncode, 0)

    # --- resta un indice, non un verbale -------------------------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r = run(str(root), "--project", "x", "--goal", "rapido", "--agents", "Vesper",
                "--outcome", "a" * (mod.OUTCOME_MAX + 1))
        check("un outcome lungo è rifiutato anche in ciclo rapido", r.returncode, 2)
        check("e dice dove va scritto", "varianza" in r.stdout)

    # --- lo slug resta un nome, non un percorso ------------------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r = run(str(root), "--project", "../../fuori", "--goal", "rapido",
                "--agents", "Vesper", "--outcome", "x")
        check("uno slug che esce dal progetto è rifiutato", r.returncode != 0)

    # --- una seduta senza nessuno che parla non è una seduta -----------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r = run(str(root), "--project", "x", "--goal", "rapido", "--agents", " ",
                "--outcome", "x")
        check("--agents vuoto è rifiutato", r.returncode != 0)

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
