# /// script
# requires-python = ">=3.11"
# ///
"""Unit tests for verify-install.py — run: uv run scripts/tests/test-verify-install.py

La regola sotto test: **l'installazione basta**, e lo si misura invece di
affermarlo. Per mesi il modulo ha insegnato il contrario, e la frase e'
sopravvissuta a due generazioni di installer perche' nessuno la rieseguiva.

Un verificatore che dice sempre «basta» sarebbe peggio della frase che
sostituisce: direbbe la cosa giusta per caso. Quindi ogni test qui e'
**differenziale** — si toglie un pezzo dall'installazione e l'esito deve
cambiare, nominando il pezzo tolto.

Le fixture riproducono la forma misurata su un'installazione vera
(`bmad-method` 6.10.0): `_bmad/config.toml` con `[agents.<code>] module = "epm"`,
e `_bmad/_config/bmad-help.csv` come catalogo consolidato.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SCRIPT = SKILL / "scripts" / "verify-install.py"

MODULE_YAML = """code: epm
name: "Enhanced Party Mode"
module_version: 9.9.9

agents:
  - code: agent-frontend-taste
    name: Vesper
    title: Direttore Craft Frontend
  - code: agent-web-animations
    name: Vera Motion
    title: Craftsperson Web Animations
  - code: agent-gdpr-counsel
    name: Jane Privacy
    title: Consigliere GDPR
"""

HELP_CSV = """module,skill,display-name,menu-code,description
Enhanced Party Mode,epm-setup,Setup,SU,setup
Enhanced Party Mode,agent-frontend-taste,Vesper,VX,craft
Enhanced Party Mode,agent-web-animations,Vera,VM,motion
"""


def load():
    spec = importlib.util.spec_from_file_location("verify_install", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["verify_install"] = mod
    spec.loader.exec_module(mod)
    return mod


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def fixture(root: Path, agenti: list[str], help_skills: list[str],
            module_di: str = "epm") -> tuple[Path, Path]:
    """Costruisce un progetto installato con esattamente questi agenti e voci."""
    (root / "_bmad" / "_config").mkdir(parents=True, exist_ok=True)
    toml = ['[core]', 'project_name = "probe"', '']
    for a in agenti:
        toml += [f"[agents.{a}]", f'module = "{module_di}"', 'team = "epm"',
                 f'name = "{a}"', ""]
    (root / "_bmad" / "config.toml").write_text("\n".join(toml), encoding="utf-8")

    righe = ["module,skill,display-name,menu-code,description"]
    righe += [f"Enhanced Party Mode,{s},x,XX,x" for s in help_skills]
    (root / "_bmad" / "_config" / "bmad-help.csv").write_text(
        "\n".join(righe) + "\n", encoding="utf-8")

    my = root / "module.yaml"
    my.write_text(MODULE_YAML, encoding="utf-8")
    hc = root / "module-help.csv"
    hc.write_text(HELP_CSV, encoding="utf-8")
    return my, hc


TUTTI = ["agent-frontend-taste", "agent-web-animations", "agent-gdpr-counsel"]
TUTTE_HELP = ["epm-setup", "agent-frontend-taste", "agent-web-animations"]


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

    # --- installazione completa: basta ---------------------------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        my, hc = fixture(root, TUTTI, TUTTE_HELP)
        d = mod.build(root, my, hc)
        check("installazione completa: basta", d["basta"])
        check("generazione riconosciuta come TOML", d["generazione"], "toml")
        check("nessun agente mancante", d["agenti_mancanti"], [])
        check("nessuna voce di aiuto mancante", d["help_mancanti"], [])
        r = run(str(root), "--module-yaml", str(my), "--help-csv", str(hc))
        check("CLI: exit 0", r.returncode, 0)
        check("CLI: lo dice", "L'installazione basta" in r.stdout)
        check("CLI: avverte di non lanciare il merge YAML",
              "cancellerebbe" in r.stdout)

    # --- differenziale 1: un agente non registrato ---------------------------
    # È il caso che la frase «installare non basta» descriveva. Se il
    # verificatore non lo distingue dal caso completo, non sta misurando niente.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        my, hc = fixture(root, TUTTI[:-1], TUTTE_HELP)
        d = mod.build(root, my, hc)
        check("un agente in meno: NON basta", d["basta"], False)
        check("e lo nomina", d["agenti_mancanti"], ["agent-gdpr-counsel"])
        r = run(str(root), "--module-yaml", str(my), "--help-csv", str(hc))
        check("CLI: exit 1 quando manca un agente", r.returncode, 1)
        check("CLI: il nome compare nel referto", "agent-gdpr-counsel" in r.stdout)

    # --- differenziale 2: agente registrato sotto un altro modulo ------------
    # Presente ma non nostro: contarlo come registrato darebbe un verde falso.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        my, hc = fixture(root, TUTTI, TUTTE_HELP, module_di="bmm")
        d = mod.build(root, my, hc)
        check("agenti sotto un altro modulo: NON basta", d["basta"], False)
        check("e il referto dice sotto quale",
              any("module='bmm'" in m for m in d["agenti_mancanti"]))

    # --- differenziale 3: catalogo di aiuto incompleto -----------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        my, hc = fixture(root, TUTTI, TUTTE_HELP[:-1])
        d = mod.build(root, my, hc)
        check("una voce di aiuto in meno: NON basta", d["basta"], False)
        check("e la nomina", d["help_mancanti"], ["agent-web-animations"])
        check("gli agenti restano a posto", d["agenti_mancanti"], [])

    # --- differenziale 4: catalogo consolidato assente -----------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        my, hc = fixture(root, TUTTI, TUTTE_HELP)
        (root / "_bmad" / "_config" / "bmad-help.csv").unlink()
        d = mod.build(root, my, hc)
        check("senza catalogo: NON basta", d["basta"], False)
        check("e dice che bmad-help non ha cosa leggere",
              any("bmad-help" in p for p in d["problemi"]))
        # Senza il file mancano TUTTE le voci, non zero: il referto stampava
        # «aiuto: 8/8» sopra la riga che diceva che il catalogo non c'era.
        check("e le conta tutte mancanti", len(d["help_mancanti"]), d["help_attese"])
        check("e nomina il colpevole probabile",
              any("cleanup-legacy" in p for p in d["problemi"]))

    # --- generazione YAML: il merge la' serviva davvero ----------------------
    # Il verificatore non deve dire «basta» su un progetto della generazione
    # vecchia: li' epm-setup faceva un lavoro vero, e negarlo romperebbe
    # un'installazione che funziona.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        my, hc = fixture(root, TUTTI, TUTTE_HELP)
        (root / "_bmad" / "config.toml").unlink()
        (root / "_bmad" / "config.yaml").write_text("epm:\n  version: 1\n", encoding="utf-8")
        d = mod.build(root, my, hc)
        check("progetto YAML: generazione riconosciuta", d["generazione"], "legacy")
        check("progetto YAML: non dichiara che basta", d["basta"], False)
        check("e dice che li' il merge serviva",
              any("YAML" in p for p in d["problemi"]))
        r = run(str(root), "--module-yaml", str(my), "--help-csv", str(hc))
        check("CLI: exit 2 (non misurabile, non un pass)", r.returncode, 2)

    # --- nessuna installazione ----------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        my, hc = fixture(root, TUTTI, TUTTE_HELP)
        (root / "_bmad" / "config.toml").unlink()
        d = mod.build(root, my, hc)
        check("nessuna config: generazione 'nessuna'", d["generazione"], "nessuna")
        check("e non basta di sicuro", d["basta"], False)

    # --- json e argomenti ----------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        my, hc = fixture(root, TUTTI, TUTTE_HELP)
        r = run(str(root), "--module-yaml", str(my), "--help-csv", str(hc),
                "--format", "json")
        check("CLI json valido", json.loads(r.stdout)["basta"], True)

    check("root inesistente rifiutata con 2", run("/nonexistent-xyz").returncode, 2)

    # --- il lettore di module.yaml regge la forma vera -----------------------
    # Se `sync-module-yaml.py` cambia forma, il parser leggero va aggiornato: e'
    # meglio saperlo qui che scoprire un 7/7 falso su un progetto vero.
    vero = SKILL / "assets" / "module.yaml"
    if vero.is_file():
        d = mod._load_yaml_light(vero.read_text(encoding="utf-8"))
        check("il module.yaml vero si legge: code", d["code"], "epm")
        check("il module.yaml vero si legge: 7 agenti", len(d["agents"]), 7)
        check("con i codici giusti",
              "agent-frontend-taste" in [a["code"] for a in d["agents"]])

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
