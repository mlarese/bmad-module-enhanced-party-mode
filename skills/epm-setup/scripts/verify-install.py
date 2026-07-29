#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Dice se l'installazione di epm basta da sola — misurandolo, non affermandolo.

Perché esiste. Per mesi questo modulo ha insegnato che «installare non basta»:
l'installer copiava le skill, e i due file **consolidati** — la config di
progetto e il catalogo di `bmad-help` — li scriveva `epm-setup`, da lanciare a
mano dopo. Era vero quando i file consolidati erano YAML.

Non lo e' piu'. Misurato il 2026-07-29 su un'installazione vera
(`bmad-method` 6.10.0, `--modules bmm,epm --custom-source`):

  · `_bmad/config.toml` contiene **tutti e sette** gli agenti del consiglio,
    con `module = "epm"`, nome, titolo, icona e descrizione, presi da
    `assets/module.yaml`;
  · `_bmad/_config/bmad-help.csv` contiene **8 righe su 8** di
    `assets/module-help.csv`;
  · `resolve_config.py` — quello che `bmad-help` usa davvero — li risolve tutti;
  · `_bmad/config.yaml` e `_bmad/module-help.csv`, i file consolidati in YAML,
    **non esistono** e nessuno li legge: gli unici riferimenti in tutto il
    progetto installato stanno dentro `epm-setup` stesso.

Quindi l'installazione basta. E il merge YAML, oggi, non e' solo inutile: con
`--legacy-dir` **cancella** `_bmad/epm/config.yaml` e `_bmad/epm/module-help.csv`,
che in questa generazione dell'installer sono **suoi output**, non residui.

Questo script e' la prova che si puo' rieseguire. Confronta cio' che il modulo
dichiara con cio' che c'e' davvero nel progetto, e dice quale delle due
generazioni di installer ha lavorato.

Usage:
    uv run scripts/verify-install.py {project-root}
    uv run scripts/verify-install.py {project-root} --module-yaml ./assets/module.yaml \\
        --help-csv ./assets/module-help.csv
    uv run scripts/verify-install.py {project-root} --format json

Exit: 0 l'installazione basta, non serve altro
      1 manca qualcosa (lo dice, voce per voce)
      2 non misurabile (progetto inesistente, nessuna config)
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import tomllib
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent


def _load_yaml_light(text: str) -> dict:
    """Legge le due cose che servono da module.yaml: `code` e la lista `agents`.

    Un parser YAML vero sarebbe una dipendenza in piu' per leggere due campi da
    un file che scriviamo noi. Qui basta la forma che `sync-module-yaml.py`
    genera, e se quella cambia il test se ne accorge.
    """
    code = ""
    agents: list[dict[str, str]] = []
    in_agents = False
    cur: dict[str, str] = {}
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith((" ", "-", "\t")):
            in_agents = raw.startswith("agents:")
            if raw.startswith("code:"):
                code = raw.split(":", 1)[1].strip().strip("\"'")
            if in_agents and cur:
                agents.append(cur)
                cur = {}
            continue
        if not in_agents:
            continue
        stripped = raw.strip()
        if stripped.startswith("- "):
            if cur:
                agents.append(cur)
            cur = {}
            stripped = stripped[2:]
        if ":" in stripped:
            k, v = stripped.split(":", 1)
            cur[k.strip()] = v.strip().strip("\"'")
    if cur:
        agents.append(cur)
    return {"code": code, "agents": [a for a in agents if a.get("code")]}


def _config_paths(root: Path) -> list[Path]:
    """I file che `resolve_config.py` fonde, nell'ordine in cui li fonde."""
    return [
        root / "_bmad" / "config.toml",
        root / "_bmad" / "custom" / "config.toml",
    ]


def build(root: Path, module_yaml: Path, help_csv: Path) -> dict:
    dichiarato = _load_yaml_light(module_yaml.read_text(encoding="utf-8"))
    code = dichiarato["code"] or "epm"

    presenti = [p for p in _config_paths(root) if p.is_file()]
    legacy_yaml = root / "_bmad" / "config.yaml"

    out: dict = {
        "project_root": str(root),
        "module_code": code,
        "generazione": None,
        "config_letta": [str(p) for p in presenti],
        "agenti_attesi": [a["code"] for a in dichiarato["agents"]],
        "agenti_mancanti": [],
        "help_attese": 0,
        "help_mancanti": [],
        "catalogo": None,
        "problemi": [],
        "basta": False,
    }

    if not presenti:
        out["generazione"] = "legacy" if legacy_yaml.is_file() else "nessuna"
        out["problemi"].append(
            "nessun `_bmad/config.toml`: qui non ha lavorato l'installer TOML. "
            + (
                "C'e' `_bmad/config.yaml`, quindi questo progetto viene dalla "
                "generazione YAML: la' il merge di epm-setup serviva davvero."
                if legacy_yaml.is_file()
                else "Non risulta nemmeno un'installazione: lancia l'installer."
            )
        )
        return out

    out["generazione"] = "toml"

    agenti: dict[str, dict] = {}
    for p in presenti:
        try:
            d = tomllib.loads(p.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            out["problemi"].append(f"`{p}` illeggibile: {exc}")
            continue
        for nome, voce in (d.get("agents") or {}).items():
            if isinstance(voce, dict):
                agenti[nome] = voce

    for atteso in dichiarato["agents"]:
        voce = agenti.get(atteso["code"])
        if voce is None:
            out["agenti_mancanti"].append(atteso["code"])
        elif voce.get("module") != code:
            out["agenti_mancanti"].append(
                f"{atteso['code']} (registrato sotto module='{voce.get('module')}', non '{code}')"
            )

    catalogo = root / "_bmad" / "_config" / "bmad-help.csv"
    out["catalogo"] = str(catalogo)
    attese = list(csv.DictReader(help_csv.read_text(encoding="utf-8").splitlines()))
    out["help_attese"] = len(attese)
    if not catalogo.is_file():
        # Senza il file non ne manca «nessuna»: mancano **tutte**. Lasciarle a
        # zero faceva stampare «aiuto: 8/8» sopra la riga che dice che il
        # catalogo non c'e' — due affermazioni opposte nello stesso referto.
        # Trovato usandolo su un progetto dove `cleanup-legacy.py` aveva appena
        # cancellato `_bmad/_config/`.
        out["help_mancanti"] = [r.get("skill") or "?" for r in attese]
        out["problemi"].append(
            f"`{catalogo}` non esiste: bmad-help non ha un catalogo da leggere. "
            "Se qui e' passato `cleanup-legacy.py --also-remove _config`, ha "
            "cancellato il catalogo di **tutti** i moduli: reinstalla."
        )
    else:
        righe = list(csv.DictReader(catalogo.read_text(encoding="utf-8").splitlines()))
        viste = {(r.get("module"), r.get("skill")) for r in righe}
        for r in attese:
            if (r.get("module"), r.get("skill")) not in viste:
                out["help_mancanti"].append(r.get("skill") or "?")

    if out["agenti_mancanti"]:
        out["problemi"].append(
            "agenti dichiarati e non registrati: " + ", ".join(out["agenti_mancanti"])
        )
    if out["help_mancanti"]:
        out["problemi"].append(
            "voci di aiuto non consolidate: " + ", ".join(out["help_mancanti"])
        )

    out["basta"] = not out["problemi"]
    return out


def referto(d: dict) -> str:
    righe = [f"# Installazione di `{d['module_code']}` — {d['project_root']}", ""]
    if d["generazione"] == "toml":
        righe.append("Generazione installer: **TOML** (`_bmad/config.toml`).")
    elif d["generazione"] == "legacy":
        righe.append("Generazione installer: **YAML** (`_bmad/config.yaml`).")
    else:
        righe.append("Nessuna installazione trovata.")
    righe.append("")
    attesi = len(d["agenti_attesi"])
    righe.append(f"- agenti: {attesi - len(d['agenti_mancanti'])}/{attesi} registrati")
    if d["help_attese"]:
        ok = d["help_attese"] - len(d["help_mancanti"])
        righe.append(f"- aiuto:  {ok}/{d['help_attese']} righe nel catalogo consolidato")
    righe.append("")
    if d["basta"]:
        righe += [
            "**L'installazione basta.** Non serve lanciare nient'altro: gli agenti",
            "del consiglio sono in config e bmad-help li conosce.",
            "",
            "Non eseguire il merge YAML su questo progetto: `--legacy-dir`",
            "cancellerebbe `_bmad/<code>/config.yaml` e `_bmad/<code>/module-help.csv`,",
            "che qui sono output dell'installer, non residui.",
        ]
    else:
        righe.append("**Manca qualcosa:**")
        righe += [f"- {p}" for p in d["problemi"]]
    return "\n".join(righe)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verifica che l'installazione di epm basti da sola"
    )
    ap.add_argument("root", help="{project-root}")
    ap.add_argument(
        "--module-yaml",
        default=str(SKILL / "assets" / "module.yaml"),
        help="il module.yaml che dichiara gli agenti (default: quello di questo skill)",
    )
    ap.add_argument(
        "--help-csv",
        default=str(SKILL / "assets" / "module-help.csv"),
        help="il module-help.csv del modulo (default: quello di questo skill)",
    )
    ap.add_argument("--format", choices=("text", "json"), default="text")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"project-root inesistente: {root}", file=sys.stderr)
        return 2

    my = Path(args.module_yaml)
    hc = Path(args.help_csv)
    for p in (my, hc):
        if not p.is_file():
            print(f"non trovo `{p}`", file=sys.stderr)
            return 2

    d = build(root, my, hc)
    print(json.dumps(d, indent=2, ensure_ascii=False) if args.format == "json" else referto(d))

    # `1` vuol dire «installazione TOML incompleta, ecco cosa manca». Su un
    # progetto della generazione YAML — o senza installazione — non c'e' niente
    # di incompleto da correggere: questo metro non si applica, ed e' `2`. Il
    # test l'ha preso: usciva `1`, che avrebbe mandato a cercare agenti mancanti
    # in un progetto dove il merge di epm-setup e' invece la cosa giusta.
    if d["generazione"] != "toml":
        return 2
    return 0 if d["basta"] else 1


if __name__ == "__main__":
    sys.exit(main())
