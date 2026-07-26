#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Il manifesto deve restare risolvibile, o il modulo non si installa.

Il difetto che questo test esiste per prendere e successo davvero: per mesi
`marketplace.json` ha dichiarato `./epm-setup` mentre le skill stavano in
`./skills/epm-setup`. L'installer stampava «Found 0 modules» e nessuno se n'era
accorto, perche nessuno reinstallava. Un manifesto sbagliato non da errore: da
silenzio.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "sync-module-yaml.py"
SKILLS = SCRIPT.parents[2]

fails = 0


def check(label: str, got, want=True) -> None:
    global fails
    if got == want:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}\n  atteso: {want}\n  ottenuto: {got}")
        fails += 1


def load():
    spec = importlib.util.spec_from_file_location("sync_module_yaml", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sync_module_yaml"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    mod = load()

    # --- il manifesto vero di questo repo regge ------------------------------
    check("il manifesto di questo repo e risolvibile",
          mod.guai_manifesto(SKILLS / ".claude-plugin" / "marketplace.json"), [])
    check("module.yaml descrive gli agenti veri",
          mod.atteso(mod.ASSET.read_text(encoding="utf-8"), SKILLS),
          mod.ASSET.read_text(encoding="utf-8"))
    check("e li trova tutti", len(mod.agenti(SKILLS)) >= 7, True)

    # --- e il check prende i difetti per cui e nato --------------------------
    with tempfile.TemporaryDirectory() as td:
        r = Path(td) / "skills"
        (r / ".claude-plugin").mkdir(parents=True)
        (r / "epm-setup" / "assets").mkdir(parents=True)
        (r / "agent-x").mkdir()
        mk = r / ".claude-plugin" / "marketplace.json"
        mk.write_text(json.dumps({"plugins": [{
            "name": "epm", "source": "./", "version": "9.9.9",
            "skills": ["./epm-setup", "./agent-x", "./agent-inesistente"]}]}))
        (r / "epm-setup" / "assets" / "module.yaml").write_text("code: epm\n")

        guai = mod.guai_manifesto(mk)
        check("prende la skill dichiarata e inesistente",
              any("agent-inesistente" in g for g in guai), True)
        check("prende il setup skill senza module-help.csv",
              any("module-help.csv" in g for g in guai), True)

        (r / "epm-setup" / "assets" / "module-help.csv").write_text("x\n")
        mk.write_text(json.dumps({"plugins": [{
            "name": "epm", "source": "./", "version": "9.9.9",
            "skills": ["./epm-setup", "./agent-x"]}]}))
        check("e tace quando il manifesto e a posto", mod.guai_manifesto(mk), [])

    # --- epm-setup allinea la versione da solo -------------------------------
    # La versione vive in quattro posti e uno solo si modifica. Qui si verifica
    # che `merge-config` la prenda da module.yaml invece di lasciare quella
    # vecchia — e che nel farlo NON butti via le risposte gia date, che sono
    # l'altra meta del lavoro: un aggiornamento che riporta le cartelle ai
    # default e peggio di un aggiornamento mancato.
    import subprocess
    merge = SCRIPT.parent / "merge-config.py"
    with tempfile.TemporaryDirectory() as td:
        cfg = Path(td) / "config.yaml"
        cfg.write_text("output_folder: '{project-root}/docs'\n"
                       "epm:\n  name: Enhanced Party Mode\n  version: 1.2.3\n"
                       "  epm_demos_folder: '{project-root}/le-mie-demo'\n")
        ans = Path(td) / "ans.json"
        ans.write_text(json.dumps({"module": {"epm_demos_folder": "{project-root}/le-mie-demo"}}))
        # `uv run`, non `sys.executable`: quello script dichiara le sue
        # dipendenze nell'intestazione PEP 723, e l'interprete della suite non
        # le ha. Lanciarlo con sys.executable dava exit 2 e sembrava un difetto
        # dello script — era il modo di chiamarlo.
        r = subprocess.run(["uv", "run", str(merge), "--config-path", str(cfg),
                            "--module-yaml", str(mod.ASSET), "--answers", str(ans),
                            "--user-config-path", str(Path(td) / "user.yaml")],
                           capture_output=True, text=True)
        check("merge-config gira", r.returncode, 0)
        scritto = cfg.read_text(encoding="utf-8")
        attesa = re.search(r"^module_version:\s*(\S+)",
                           mod.ASSET.read_text(encoding="utf-8"), re.M).group(1)
        check("allinea la versione da module.yaml", f"version: {attesa}" in scritto, True)
        check("e non lascia quella vecchia", "1.2.3" not in scritto, True)
        check("conservando le risposte gia date",
              "le-mie-demo" in scritto, True)
        check("e senza toccare le chiavi fuori dal modulo",
              "output_folder: '{project-root}/docs'" in scritto, True)

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
