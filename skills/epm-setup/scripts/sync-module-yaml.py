#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Tiene `module.yaml` allineato agli agenti veri, e verifica che il manifesto
del plugin sia risolvibile — cioè che il modulo si installi.

Perché esiste, misurato il 2026-07-27: **il modulo non si installava più**.
L'installer stampava «Found 0 modules» e la diagnosi è stata questa —

    marketplace.json letto, 1 plugin («epm»)     ✓
    discoverModules → 1 modulo                   ✓
    PluginResolver.resolve → 0 moduli            ✗

`PluginResolver` supporta esattamente il nostro schema (una skill `-setup` con
`assets/module.yaml` + `assets/module-help.csv`), ma risolve i percorsi
dell'array `skills[]` **relativi alla radice del plugin**. Il manifesto
dichiarava `./epm-setup` mentre le skill stanno in `./skills/epm-setup`: un
livello di differenza, e il resolver non trovava niente da risolvere. Era così
dal primo rilascio, e nessuno se n'era accorto perché nessuno reinstallava.

Il file era anche **stantio**: `module_version: 1.4.0` mentre il marketplace
diceva 1.17.0, e la descrizione di Vesper era ferma a due nomi fa. Un manifesto
che nessuno rigenera racconta il modulo di un anno prima.

Due cose, quindi:

  1. **rigenera** `module_version` e il blocco `agents:` di `assets/module.yaml`
     dalle fonti vere — `.claude-plugin/marketplace.json` per la versione,
     `skills/<agente>/customize.toml` per nome, titolo, icona e descrizione;
  2. **verifica il manifesto**: ogni percorso di `skills[]` esiste davvero, e la
     skill `-setup` porta i due file che il resolver pretende.

Un solo manifesto: la copia alla radice **non serve** (provato — il resolver
trova l'asset del setup skill) e sarebbe solo un secondo posto da cui divergere.

`--check` non scrive: dice se è tutto allineato ed esce 1 se no. È quello che
usa il test, perché un manifesto si allontana dal codice in silenzio.

Usage:
    uv run scripts/sync-module-yaml.py {skills-root}
    uv run scripts/sync-module-yaml.py {skills-root} --check
    uv run scripts/sync-module-yaml.py {skills-root} --marketplace {file}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent / "assets" / "module.yaml"

AGENT_BLOCK_RE = re.compile(r"^agents:\n(?:[ \t]+.*\n|\n)*", re.M)
VERSION_RE = re.compile(r"^module_version:\s*.*$", re.M)


def agenti(skills_root: Path) -> list[dict]:
    """Gli agenti sono quelli installati, non quelli ricordati."""
    out = []
    for d in sorted(skills_root.glob("agent-*")):
        toml = d / "customize.toml"
        if not toml.is_file():
            continue
        a = tomllib.load(toml.open("rb")).get("agent", {})
        if not a.get("code"):
            continue
        out.append({k: a.get(k, "") for k in ("code", "name", "title", "icon", "description")})
    return out


def versione_di(mk: Path) -> str | None:
    if not mk.is_file():
        return None
    plugins = json.loads(mk.read_text(encoding="utf-8")).get("plugins") or []
    return plugins[0].get("version") if plugins else None


def versione(skills_root: Path) -> str | None:
    """La sorgente di verità della versione: il manifesto dentro `skills/`."""
    return versione_di(skills_root / ".claude-plugin" / "marketplace.json")


def guai_versione(skills_root: Path, mk: Path) -> list[str]:
    """I due manifesti devono dire la **stessa versione**.

    Perché esiste. I due `marketplace.json` sono legittimamente diversi — i
    percorsi di `skills[]` si risolvono dalla radice del plugin, che qui è
    `skills/` e nel repo di distribuzione è il repo — e da lì la regola: «non
    copiare uno sull'altro, si propaga solo la **versione**».

    Quella regola viveva solo in prosa. `--check --marketplace <distribuzione>`
    verificava i percorsi e diceva «allineato» con la sorgente a 1.30.0 e la
    distribuzione ferma a 1.29.0 — cioè taceva esattamente sull'unica cosa che
    quel comando doveva propagare. È la stessa famiglia di difetto di
    `./epm-setup` contro `./skills/epm-setup`: una regola scritta, nessuno che
    la esegua, e il disallineamento che non dà errore.

    Non morde quando `--marketplace` non è passato: lì il manifesto è già la
    sorgente, e confrontarlo con sé stesso non misura niente.
    """
    sorgente_mk = (skills_root / ".claude-plugin" / "marketplace.json").resolve()
    if mk.resolve() == sorgente_mk:
        return []
    qui, la = versione_di(sorgente_mk), versione_di(mk)
    if qui is None or la is None:
        return []
    if qui != la:
        return [f"versione disallineata: la sorgente dice {qui}, "
                f"`{mk}` dice {la}. Si propaga **solo** la versione — "
                "i percorsi dei due manifesti restano diversi ed è giusto"]
    return []


def blocco(agents: list[dict]) -> str:
    righe = ["agents:"]
    for a in agents:
        righe += [f"  - code: {a['code']}",
                  f"    name: {a['name']}",
                  f"    title: {a['title']}",
                  f'    icon: "{a["icon"]}"',
                  f'    description: "{a["description"]}"']
    return "\n".join(righe) + "\n\n"


def atteso(testo: str, skills_root: Path) -> str:
    fuori = agenti(skills_root)
    if not fuori:
        raise SystemExit(f"nessun agente trovato in {skills_root}: "
                         "senza agenti il manifesto non descrive niente")
    nuovo = AGENT_BLOCK_RE.sub(blocco(fuori), testo, count=1)
    v = versione(skills_root)
    if v:
        nuovo = VERSION_RE.sub(f"module_version: {v}", nuovo, count=1)
    return nuovo


def guai_manifesto(mk: Path) -> list[str]:
    """I percorsi di `skills[]` devono esistere, o il resolver torna a mani vuote.

    Si risolvono dalla **radice del plugin**, cioè la cartella che contiene
    `.claude-plugin/` — che in questo repo è `skills/` e nel repo di
    distribuzione è la radice. Per questo i due manifesti dicono percorsi
    diversi, ed è giusto: copiarne uno sull'altro rimette il difetto.
    """
    if not mk.is_file():
        return [f"manca {mk}"]
    radice = mk.parent.parent
    plugins = json.loads(mk.read_text(encoding="utf-8")).get("plugins") or []
    if not plugins:
        return [f"{mk.name}: nessun plugin dichiarato"]
    out = []
    for p in plugins:
        rels = p.get("skills") or []
        if not rels:
            out.append(f"{mk.name}: il plugin `{p.get('name')}` non elenca skill")
        for rel in rels:
            d = (radice / rel.lstrip("./")).resolve()
            if not d.is_dir():
                out.append(f"{mk.name}: `{rel}` non esiste sotto {radice} — "
                           "il resolver non trova la skill e il modulo NON si installa")
            elif d.name.endswith("-setup"):
                for f in ("module.yaml", "module-help.csv"):
                    if not (d / "assets" / f).is_file():
                        out.append(f"{d.name}: manca `assets/{f}`, che il resolver pretende")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Allinea module.yaml agli agenti veri")
    ap.add_argument("skills_root", help="la cartella `skills/` che contiene gli agenti")
    ap.add_argument("--check", action="store_true", help="non scrive: dice se è allineato")
    ap.add_argument("--marketplace", help="marketplace.json da verificare "
                    "(default: quello dentro skills-root)")
    args = ap.parse_args()

    skills_root = Path(args.skills_root).resolve()
    if not skills_root.is_dir():
        raise SystemExit(f"skills-root inesistente: {skills_root}")
    if not ASSET.is_file():
        raise SystemExit(f"manca {ASSET}")

    mk = (Path(args.marketplace).resolve() if args.marketplace
          else skills_root / ".claude-plugin" / "marketplace.json")

    testo = ASSET.read_text(encoding="utf-8")
    voluto = atteso(testo, skills_root)
    if args.check:
        guai = []
        if voluto != testo:
            guai.append(f"`{ASSET.name}` non descrive gli agenti veri: rigeneralo")
        guai += guai_manifesto(mk)
        guai += guai_versione(skills_root, mk)
        for g in guai:
            print(f"  ! {g}")
        print("  allineato" if not guai else f"  {len(guai)} rilievi")
        return 1 if guai else 0

    if voluto != testo:
        ASSET.write_text(voluto, encoding="utf-8")
        print(f"aggiornato {ASSET}")
    for g in guai_manifesto(mk) + guai_versione(skills_root, mk):
        print(f"  ! {g}")
    v = versione(skills_root)
    print(f"agenti: {len(agenti(skills_root))} · versione: {v or 'non dichiarata'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
