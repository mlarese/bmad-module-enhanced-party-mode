#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Who sits on the council — derived from what is installed, not remembered.

The law says «convoca tutto il consiglio, non tre voci»: every agent skill
installed in this project takes part in the decisions, because the value is the
friction, and a table picked by hand contains only the objections you expected.

But «tutto il consiglio» was written down as a LIST, by hand, in three places —
`_bmad/custom/bmad-party-mode.toml`, `autonomia.md`, `implementation-handoff.md`
— and the three had already drifted: the party carried 13 members while the
references named 11, leaving the PM and the dev out of every roster Vesper
actually read. A roster held in prose is a roster that goes stale the day
someone adds an agent, and nobody notices, because a missing voice does not
raise an error: it just never speaks.

So the roster is computed here:
  - every `agent-*` skill installed in the project is a member **by right**;
  - the party group is checked against them and the gaps are named;
  - anyone missing from the group is still convened, by name — a
    misconfiguration must not silently shrink the table.

Usage:
    uv run scripts/council_roster.py {project-root}
    uv run scripts/council_roster.py . --format json

Exit: 0 roster completo · 1 qualcuno è installato ma fuori dal gruppo.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Where agent skills live: the source tree first, then the installed copies.
SKILL_DIRS = ("skills", ".claude/skills", ".agents/skills")
PARTY_TOML = "_bmad/custom/bmad-party-mode.toml"
PARTY_TOML_FALLBACKS = ("_bmad/custom/bmad-party-mode.user.toml",)
GROUP_ID = "super-esperti"

# BMAD role skills that carry a person in this project's council. Their names
# are what the references cite, so a drift between the two is visible here.
BMAD_ROLES: dict[str, tuple[str, str]] = {
    "bmad-agent-pm": ("John", "product manager — perimetro e requisiti"),
    "bmad-agent-ux-designer": ("Sally", "UX — flussi, stati, page spec"),
    "bmad-agent-architect": ("Winston", "architettura — coerenza tecnica"),
    "bmad-agent-analyst": ("Mary", "analista — evidenza e ricerca"),
    "bmad-agent-dev": ("Amelia", "sviluppo — fattibilità implementativa"),
    "bmad-tea": ("Murat", "test architect — ciò che nessuno ha verificato"),
}

NAME_RE = re.compile(r"^description:\s*>?\s*\n?\s*(.+)$", re.M)


def agent_display_name(skill_md: Path) -> str:
    """The person's name from the skill description: «Jane Privacy (GDPR…)»."""
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")[:1200]
    except OSError:
        return skill_md.parent.name
    m = re.search(r"^description:\s*(?:>-?\s*\n\s*)?(.+)$", text, re.M)
    if not m:
        return skill_md.parent.name
    head = m.group(1).strip()
    # Cut at the first separator: «Vesper — craft FE», «Jane Privacy (GDPR…)».
    head = re.split(r"\s+[—–-]\s+|\s*\(|\.\s|,\s", head)[0].strip()
    return head or skill_md.parent.name


def installed_agents(root: Path) -> list[dict]:
    """Every agent-* skill installed here, deduplicated by directory name."""
    found: dict[str, dict] = {}
    for rel in SKILL_DIRS:
        base = root / rel
        if not base.is_dir():
            continue
        for d in sorted(base.glob("agent-*")):
            skill_md = d / "SKILL.md"
            if not (d.is_dir() and skill_md.is_file()):
                continue
            found.setdefault(d.name, {
                "skill": d.name,
                "name": agent_display_name(skill_md),
                "where": str(d.relative_to(root)),
            })
    return list(found.values())


def _load_toml(path: Path) -> dict:
    try:
        import tomllib
    except ModuleNotFoundError:                      # py3.10
        return _load_toml_regex(path)
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except (OSError, ValueError):
        return {}


def _load_toml_regex(path: Path) -> dict:
    """Enough of the party file to read members and the group, without tomllib."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    members = [{"code": c, "name": n} for c, n in zip(
        re.findall(r'^code\s*=\s*"([^"]+)"', text, re.M),
        re.findall(r'^name\s*=\s*"([^"]+)"', text, re.M))]
    groups = []
    for gid, body in re.findall(
            r'id\s*=\s*"([^"]+)"(.*?)(?=\n\[\[|\Z)', text, re.S):
        m = re.search(r"members\s*=\s*\[(.*?)\]", body, re.S)
        ids = re.findall(r'"([^"]+)"', m.group(1)) if m else []
        groups.append({"id": gid, "members": ids})
    return {"workflow": {"party_members": members, "party_groups": groups}}


def party(root: Path) -> tuple[list[dict], list[str], str | None]:
    """(declared members, ids of the council group, path read)."""
    for rel in (PARTY_TOML, *PARTY_TOML_FALLBACKS):
        path = root / rel
        if not path.is_file():
            continue
        data = _load_toml(path).get("workflow", {})
        members = data.get("party_members", []) or []
        group: list[str] = []
        for g in data.get("party_groups", []) or []:
            if g.get("id") == GROUP_ID:
                group = list(g.get("members", []) or [])
        return members, group, str(path.relative_to(root))
    return [], [], None


def seated(agent: dict, members: list[dict], group: list[str]) -> str | None:
    """The party code that seats this agent, or None when nobody does.

    Two ways a group can name an agent, and both are legitimate:
      1. by the installed agent's own code — `agent-frontend-taste`. This is
         what `--emit-party` writes, and what a project gets when nobody
         hand-wrote personas.
      2. by a custom member's code — `vesper` — declared in `party_members`
         with its own persona, which overrides the installed agent.
    Only the second was checked, so a group generated by this very script came
    back as "nobody is seated": found by installing it in a real project.
    """
    if agent["skill"] in group:
        return agent["skill"]
    key = agent["name"].split()[0].lower() if agent["name"] else ""
    for m in members:
        code, name = str(m.get("code", "")), str(m.get("name", ""))
        if code not in group:
            continue
        if key and (key in name.lower() or key in code.lower()):
            return code
    return None


def build(root: Path) -> dict:
    agents = installed_agents(root)
    members, group, path = party(root)
    configured = bool(group)

    council, missing = [], []
    for a in agents:
        code = seated(a, members, group) if configured else None
        entry = {**a, "party_code": code, "seated": bool(code) or not configured}
        council.append(entry)
        if configured and not code:
            missing.append(entry)

    roles = []
    for skill, (person, role) in BMAD_ROLES.items():
        present = skill in group if configured else True
        roles.append({"skill": skill, "name": person, "role": role, "seated": present})

    return {
        "party_file": path,
        "group": GROUP_ID,
        "group_configured": configured,
        "group_size": len(group),
        # How to convene without opening a menu: an unknown `--party <id>` makes
        # bmad-party-mode list the names and ASK, and a question is a stop.
        "convocazione": (f"bmad-party-mode --non-interactive --party {GROUP_ID}"
                         if configured else "bmad-party-mode --non-interactive"),
        "agents": council,
        "bmad_roles": roles,
        "missing_from_group": missing,
        "complete": not missing,
    }


def emit_party(root: Path) -> str:
    """A ready `super-esperti` group for a project where the module is installed.

    Configuring the group is optional — without it party-mode already convenes
    the whole collective — but it is what carries the scene and the personas.
    """
    agents = installed_agents(root)
    lines = [
        "# Gruppo del consiglio, generato da council_roster.py --emit-party.",
        "# Incollalo in {project-root}/_bmad/custom/bmad-party-mode.toml",
        "",
        "[workflow]",
        "",
        "[[workflow.party_groups]]",
        f'id = "{GROUP_ID}"',
        'name = "Super Esperti"',
        "memory = true",
        "members = [",
    ]
    codes = [a["skill"] for a in agents] + list(BMAD_ROLES)
    for c in codes:
        lines.append(f'  "{c}",')
    lines.append("]")
    lines.append('scene = """Il consiglio che decide e approva. Non parlano tutti: '
                 "parla chi ha giurisdizione sul punto in discussione. Chi ha "
                 "giurisdizione ha però il dovere di parlare. Il craft non si "
                 'vota."""')
    return "\n".join(lines)


def render(d: dict) -> str:
    out = ["# Consiglio — chi si siede", ""]
    if d["group_configured"]:
        out.append(f"gruppo `{d['group']}` da `{d['party_file']}` "
                   f"· {d['group_size']} membri dichiarati")
    else:
        out.append(
            "**nessun gruppo `super-esperti` configurato in questo progetto — e non "
            "è un problema:** senza `default_party`, `bmad-party-mode` convoca già "
            "*tutto il collettivo installato*, che è esattamente la legge del roster "
            "completo. Il gruppo serve solo a dare scena e persone su misura."
        )
    out.append("")
    out.append(f"**Come si convoca qui:** `{d['convocazione']}`")
    out.append("")
    if not d["group_configured"]:
        out.append(
            "> Non passare `--party super-esperti` dove il gruppo non esiste: a un id "
            "sconosciuto party-mode risponde elencando i nomi e **chiedendo quale "
            "usare** — e una domanda è una fermata, cioè la legge violata da una riga "
            "di configurazione mancante. Per configurarlo: `--emit-party`."
        )
        out.append("")
    out.append("## Agenti installati — membri **di diritto**")
    out.append("")
    out.append("| agente | nome | dove | al tavolo |")
    out.append("|---|---|---|---|")
    for a in d["agents"]:
        if a["party_code"]:
            how = f"sì (`{a['party_code']}`)"
        elif a["seated"]:
            how = "sì (collettivo)"
        else:
            how = "**NO**"
        out.append(f"| `{a['skill']}` | {a['name']} | `{a['where']}` | {how} |")
    out.append("")
    out.append("## Ruoli BMAD nel consiglio")
    out.append("")
    for r in d["bmad_roles"]:
        out.append(f"- {'✓' if r['seated'] else '✗'} **{r['name']}** — {r['role']} "
                   f"(`{r['skill']}`)")
    out.append("")
    if d["missing_from_group"]:
        names = ", ".join(f"{a['name']} (`{a['skill']}`)" for a in d["missing_from_group"])
        out.append("## Roster incompleto")
        out.append("")
        out.append(
            f"**Installati ma fuori dal gruppo: {names}.** Non è un permesso a "
            "decidere senza di loro: si convocano **per nome** in questa seduta, e "
            "il gruppo si corregge nel file di party. Un consiglio che si restringe "
            "per una riga mancante in un TOML contiene solo le obiezioni che ti "
            "aspettavi — che è esattamente ciò che la legge del roster completo "
            "vuole impedire."
        )
    else:
        out.append("Roster completo: ogni agente installato ha un posto al tavolo.")
        if not d["group_configured"]:
            out.append("")
            out.append(
                "Il modulo appena installato sta così: gli agenti ci sono, il gruppo "
                "no, e il consiglio è comunque tutto il collettivo. `--emit-party` "
                "genera il blocco da mettere in `_bmad/custom/bmad-party-mode.toml` "
                "se vuoi anche scena e persone."
            )
    out.append("")
    out.append("Parla chi ha giurisdizione; chi tace su una cosa di sua competenza ha "
               "fallito, e il consiglio con lui. Il craft non si vota.")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Roster del consiglio, derivato dall'installato")
    ap.add_argument("root", nargs="?", default=".", help="Project root (default: cwd)")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    ap.add_argument("--emit-party", action="store_true",
                    help="stampa il blocco TOML del gruppo per un progetto che ha installato il modulo")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"root inesistente: {root}")

    if args.emit_party:
        print(emit_party(root))
        return 0

    d = build(root)
    print(json.dumps(d, ensure_ascii=False, indent=1) if args.format == "json" else render(d))
    return 0 if d["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
