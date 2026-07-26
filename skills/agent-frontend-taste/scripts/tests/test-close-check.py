# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for close_check.py — run: uv run scripts/tests/test-close-check.py

Il check di chiusura esiste perché tre pagine su cinque, negli eval, uscivano
con `palette_guard` a 1: la regola c'era, il comando no. Questi test tengono
fermo il comportamento che rende il comando difficile da saltare — e i falsi
positivi lontani, perché un controllo che grida al lupo viene spento.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "close_check.py"

CLEAN = """<!doctype html><meta name="viewport" content="width=device-width, initial-scale=1">
<style>:root{--paper:#F5F3EF;--ink:#15171A;--brass:#B8895A;}
body{background:var(--paper)}.hero{background:var(--ink)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,18rem),1fr))}
@media(max-width:820px){.grid{grid-template-columns:1fr}}</style>
<section class="hero"><h1>Osteria</h1></section>
"""


def load():
    spec = importlib.util.spec_from_file_location("close_check", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["close_check"] = mod
    spec.loader.exec_module(mod)
    return mod


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def page(td: Path, name: str, body: str) -> Path:
    p = td / name
    p.write_text(body, encoding="utf-8")
    return p


def main() -> int:
    fails = 0
    mod = load()

    def check(label, got, want=True):
        nonlocal fails
        if got == want:
            print(f"PASS: {label}")
        else:
            print(f"FAIL: {label}\n  atteso: {want}\n  ottenuto: {got}")
            fails += 1

    # --- pagina pulita: si consegna ----------------------------------------
    with tempfile.TemporaryDirectory() as td:
        p = page(Path(td), "ok.html", CLEAN)
        r = run(str(p))
        check("pagina pulita → exit 0", r.returncode, 0)
        check("pagina pulita → lo dice", "**OK**" in r.stdout)
        check("suggerisce la traccia da mettere nel DESIGN", "hue_sector:" in r.stdout)

    # --- il difetto che ha fatto nascere il comando -------------------------
    with tempfile.TemporaryDirectory() as td:
        p = page(Path(td), "teal.html", CLEAN.replace("--ink:#15171A", "--ink:#1d5b62"))
        r = run(str(p))
        check("scuro saturo su superficie grande → exit 1", r.returncode, 1)
        check("nomina il colore e la croma", "croma" in r.stdout and "#1d5b62" in r.stdout)
        check("dice che così non si consegna", "Non si consegna" in r.stdout)

    # --- responsive ---------------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        p = page(Path(td), "noviewport.html", CLEAN.replace(
            '<meta name="viewport" content="width=device-width, initial-scale=1">', ""))
        r = run(str(p))
        check("viewport mancante → exit 1", r.returncode, 1)
        check("spiega cosa succede sul telefono", "rimpicciolita" in r.stdout)

        p2 = page(Path(td), "fissa.html", CLEAN.replace(
            ".grid{display:grid", ".wrap{width:1280px}.grid{display:grid"))
        check("larghezza fissa oltre 1000px segnalata",
              "larghezza fissa" in run(str(p2)).stdout)

    # --- segnaposto ---------------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        p = page(Path(td), "todo.html", CLEAN.replace("<h1>Osteria</h1>", "<h1>TODO: nome</h1>"))
        r = run(str(p))
        check("TODO nel consegnato → exit 1", r.returncode, 1)
        check("nomina il segnaposto trovato", "segnaposto" in r.stdout)

        # La trappola già vista due volte: «Metodo» contiene «todo».
        p2 = page(Path(td), "metodo.html", CLEAN.replace("<h1>Osteria</h1>",
                                                         "<h1>Il nostro metodo</h1>"))
        check("«metodo» non è un segnaposto", run(str(p2)).returncode, 0)

    # --- traccia: serve solo se la pagina espone dati inventabili -----------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        con = page(root, "contatti.html", CLEAN.replace(
            "</style>", "</style><footer>+39 0421 55 22 10 · info@osteria.it</footer>"))
        r = run(str(con))
        check("contatti senza DESIGN.md → exit 1", r.returncode, 1)
        check("dice perché la traccia serve", "la chat sparisce" in r.stdout)

        design = root / "DESIGN.md"
        design.write_text("# Design\n\ndati_verosimili:\n  - campo: telefono\n", encoding="utf-8")
        check("con `dati_verosimili` nel DESIGN → exit 0",
              run(str(con), "--design", str(design)).returncode, 0)

        design.write_text("# Design\n\n## Brand\ntesto\n", encoding="utf-8")
        check("DESIGN senza la voce → ancora 1",
              run(str(con), "--design", str(design)).returncode, 1)

        # `@media` non è un indirizzo email: il controllo non deve gridare al lupo.
        check("una pagina senza contatti non chiede la traccia", run(str(page(
            root, "nodata.html", CLEAN))).returncode, 0)

    # --- non misurabile: 2, e non è un pass ---------------------------------
    with tempfile.TemporaryDirectory() as td:
        p = page(Path(td), "utility.html",
                 '<!doctype html><meta name="viewport" content="width=device-width">'
                 '<div class="bg-slate-900 text-white">x</div>')
        r = run(str(p))
        check("palette non leggibile → exit 2", r.returncode, 2)
        check("dice che non è un pass", "non si dichiara «pulita»" in r.stdout)

    # --- più pagine insieme: vince la peggiore ------------------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        a = page(root, "a.html", CLEAN)
        b = page(root, "b.html", CLEAN.replace("<h1>Osteria</h1>", "<h1>lorem ipsum</h1>"))
        r = run(str(a), str(b))
        check("due pagine, una rotta → exit 1", r.returncode, 1)
        check("entrambe compaiono nel report", "a.html" in r.stdout and "b.html" in r.stdout)

    # --- json + ledger ------------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        p = page(root, "ok.html", CLEAN)
        led = root / "hue-ledger.json"
        r = run(str(p), "--ledger", str(led), "--format", "json")
        check("json valido", json.loads(r.stdout)["state"], 0)
        check("il ledger registra la misura", led.is_file() and
              json.loads(led.read_text(encoding="utf-8"))[0]["dominant_sector"] is not None)

    check("file inesistente rifiutato", run("/tmp/non-esiste-xyz.html").returncode != 0)

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
