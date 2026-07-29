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


def manifesto_di_questo_albero() -> Path | None:
    """Gli alberi in cui questo file può trovarsi sono **tre**, e solo due hanno
    un manifesto.

    - **sorgente** (`base-bmad`): `.claude-plugin/` sta dentro `skills/`, che è
      la radice del plugin;
    - **distribuzione**: sta alla radice del repo, perché lì la radice del
      plugin è il repo;
    - **progetto installato**: la skill vive in `.claude/skills/epm-setup/` e di
      manifesto **non ce n'è nessuno** — l'installer copia le skill, non il
      manifesto. È il layout giusto, non un difetto.

    Il test guardava solo il primo, e arrivava **rosso** negli altri due.
    Misurato due volte, e la seconda ha corretto la prima: la correzione che
    copriva la distribuzione lasciava rosso il progetto installato, e la riga
    «che non ce ne sia nessuno resta un difetto» era falsa. Si vede solo
    installando davvero e lanciando la suite da lì.

    Conta perché il runner vive dentro lo skill proprio per far sì che
    un'installazione possa verificarsi da sola. Una suite rossa all'arrivo è
    come non averla, e peggio: insegna a ignorarla.
    """
    for candidato in (SKILLS / ".claude-plugin" / "marketplace.json",
                      SKILLS.parent / ".claude-plugin" / "marketplace.json"):
        if candidato.is_file():
            return candidato
    return None

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

    # --- il manifesto vero di questo albero regge ----------------------------
    # Sorgente o distribuzione: si prende quello che c'e', e in entrambi i casi
    # deve essere risolvibile. Se non c'e' nessuno dei due, quello si' e' un
    # difetto — non un layout diverso.
    manifesto = manifesto_di_questo_albero()
    if manifesto is None:
        print("SKIP: nessun manifesto in questo albero (progetto installato) — "
              "il manifesto si verifica dove vive, cioe' nel repo del modulo")
    else:
        check(f"il manifesto ({manifesto.parent.parent.name}/) e risolvibile",
              mod.guai_manifesto(manifesto), [])
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

    # --- le due versioni devono coincidere -----------------------------------
    # La regola «si propaga solo la versione» viveva solo in prosa: `--check
    # --marketplace <distribuzione>` verificava i percorsi e diceva «allineato»
    # con la sorgente a 1.30.0 e la distribuzione a 1.29.0. Differenziale:
    # stessa versione tace, versione diversa parla e le nomina entrambe.
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        src = base / "skills"
        (src / ".claude-plugin").mkdir(parents=True)
        dist = base / "distribuzione" / ".claude-plugin"
        dist.mkdir(parents=True)

        def scrivi(p: Path, v: str, skills: list[str]) -> None:
            p.write_text(json.dumps({"plugins": [{
                "name": "epm", "source": "./", "version": v, "skills": skills}]}))

        src_mk = src / ".claude-plugin" / "marketplace.json"
        dist_mk = dist / "marketplace.json"

        scrivi(src_mk, "1.30.0", ["./epm-setup"])
        scrivi(dist_mk, "1.30.0", ["./skills/epm-setup"])
        check("versioni uguali: tace", mod.guai_versione(src, dist_mk), [])

        scrivi(dist_mk, "1.29.0", ["./skills/epm-setup"])
        guai = mod.guai_versione(src, dist_mk)
        check("versione indietro nella distribuzione: parla", len(guai), 1)
        check("e nomina quella della sorgente", "1.30.0" in guai[0])
        check("e nomina quella della distribuzione", "1.29.0" in guai[0])
        check("e ricorda che i percorsi restano diversi", "percorsi" in guai[0])

        # Senza --marketplace il confronto sarebbe con se stesso: non misura
        # niente, e fingere di misurarlo sarebbe un verde comprato.
        check("manifesto sorgente contro se stesso: niente da confrontare",
              mod.guai_versione(src, src_mk), [])

        # Un manifesto illeggibile o senza versione non e' un disallineamento:
        # lo prende `guai_manifesto`, e raddoppiare il rilievo confonde.
        scrivi(dist_mk, "1.30.0", ["./skills/epm-setup"])
        (dist / "vuoto.json").write_text(json.dumps({"plugins": []}))
        check("manifesto senza plugin: nessun rilievo di versione",
              mod.guai_versione(src, dist / "vuoto.json"), [])

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
