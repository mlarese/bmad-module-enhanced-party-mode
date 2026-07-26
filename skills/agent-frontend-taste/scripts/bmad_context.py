#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Discover the BMAD documents that BIND the implementation phase.

Before Vesper builds a page, this script answers one question: is there a PRD,
an architecture document, a UX/page spec, a project context? If yes, they are
not inspiration — they are constraints. The architecture's tech stack is
mandatory; the PRD bounds the scope; a page spec drives the structure and the
seeded axes only fill what it leaves open. If no document exists, the verdict
says so, and the autonomous path (domain+marketing research, edge cases,
adversarial review) must be declared in the accompanying spec, never inside the artifact.

Paths come from `_bmad/config.toml` when present (planning_artifacts,
implementation_artifacts), with the standard BMAD layout as fallback — the
script reads the project's own config instead of hardcoding a guess.

Usage:
    uv run scripts/bmad_context.py {project-root}
    uv run scripts/bmad_context.py . --format json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# Default BMAD layout, used only when _bmad/config.toml does not say otherwise.
DEFAULT_PLANNING = "_bmad-output/planning-artifacts"
DEFAULT_IMPLEMENTATION = "_bmad-output/implementation-artifacts"

PRD_PAT = re.compile(r"prd", re.I)
ARCH_PAT = re.compile(r"architect|architett", re.I)
UX_PAT = re.compile(r"ux|wireframe|page-?spec", re.I)

# Headings inside the architecture doc that carry the binding stack.
STACK_HEADING = re.compile(r"stack|tecnolog|tech\b|framework", re.I)
RULES_HEADING = re.compile(r"regol|rule|principi|constraint|convenzion|standard", re.I)

# Project-context files, most binding first.
CONTEXT_CANDIDATES = (
    "project-context.md",
    "docs/project-context.md",
    "CLAUDE.md",
    "AGENTS.md",
)

# Where clarifying documents live when the project has no formal architecture.
# The short path (kernel + slices) deliberately skips writing an architecture
# doc, so the stack and the conventions end up in CLAUDE.md / AGENTS.md or in
# loose notes under docs/. Those notes are not decoration: if nothing else
# states the stack, they are the only place that does.
DOC_DIRS = ("docs", "doc", "documentation")
DOC_PRIORITY = re.compile(
    r"varian|decision|adr|stack|tech|architett|architect|setup|install|convenzion|convention|"
    r"standard|contributing|readme|struttur|structure|deploy|env", re.I)
MAX_CLARIFYING = 12

# Repo files whose presence is a stack signal even without an architecture doc.
REPO_SIGNALS = (
    ("package.json", "node"),
    ("composer.json", "php/composer"),
    ("requirements.txt", "python"),
    ("pyproject.toml", "python"),
    ("Gemfile", "ruby"),
    ("go.mod", "go"),
    ("wp-content", "wordpress"),
    ("next.config.js", "next"),
    ("next.config.mjs", "next"),
    ("astro.config.mjs", "astro"),
    ("vite.config.js", "vite"),
    ("vite.config.ts", "vite"),
    ("tailwind.config.js", "tailwind"),
)


def clarifying_docs(root: Path, already: list[Path]) -> list[Path]:
    """Loose documentation that can answer what no formal document states.

    On the short path there is no architecture document by design, so the
    stack and the conventions live in CLAUDE.md / AGENTS.md — or, when nobody
    wrote them there, in whatever sits under docs/. Reading those beats
    guessing the stack from file extensions.

    Ranked, not dumped: names that promise stack, setup or conventions first,
    then the rest, capped — a docs/ folder can hold hundreds of files and a
    wall of paths is as useless as no paths at all.
    """
    seen = {p.resolve() for p in already}
    found: list[Path] = []
    readme = root / "README.md"
    if readme.is_file() and readme.resolve() not in seen:
        found.append(readme)
    for name in DOC_DIRS:
        folder = root / name
        if not folder.is_dir():
            continue
        for f in sorted(folder.rglob("*.md")):
            if f.is_file() and f.resolve() not in seen and f not in found:
                found.append(f)
    found.sort(key=lambda f: (0 if DOC_PRIORITY.search(f.name) else 1, str(f)))
    return found[:MAX_CLARIFYING]


def read_config_paths(root: Path) -> tuple[Path, Path]:
    """Planning/implementation artifact dirs from the project's own config."""
    planning, implementation = DEFAULT_PLANNING, DEFAULT_IMPLEMENTATION
    cfg = root / "_bmad" / "config.toml"
    if cfg.exists():
        try:
            text = cfg.read_text(encoding="utf-8")
        except OSError:
            text = ""
        for key, current in (("planning_artifacts", "p"), ("implementation_artifacts", "i")):
            m = re.search(rf'^{key}\s*=\s*"([^"]+)"', text, re.M)
            if m:
                raw = m.group(1)
                if "{project-root}" in raw:
                    value = raw.replace("{project-root}", "").lstrip("/")
                elif raw.startswith("/"):
                    # An absolute path with no {project-root} placeholder is
                    # meant as-is: stripping the slash would silently re-root
                    # it under the project.
                    value = raw
                else:
                    value = raw
                if current == "p":
                    planning = value
                else:
                    implementation = value
    # Path("/root") / "/abs" resolves to "/abs": absolute values win by design.
    return root / planning, root / implementation


def front_title(path: Path) -> str:
    """Title from YAML frontmatter or first heading; fall back to the filename."""
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:2000]
    except OSError:
        return path.name
    m = re.search(r"^title:\s*['\"]?(.+?)['\"]?\s*$", head, re.M)
    if m:
        return m.group(1)
    m = re.search(r"^#\s+(.+)$", head, re.M)
    return m.group(1) if m else path.name


def md_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.rglob("*.md") if p.is_file())


def extract_section(text: str, heading_pat: re.Pattern, max_lines: int = 25) -> str | None:
    """Body of the first matching heading, down to the next heading of the
    SAME level or shallower.

    Cutting at any heading was wrong: a stack section organised as
    `## Tech stack / ### Frontend / ### Backend` returned just the bare
    heading line — it read as extracted while carrying nothing. Subsections
    belong to their section.
    """
    lines = text.splitlines()
    start = level = None
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,4})\s", line)
        if m and heading_pat.search(line):
            start, level = i, len(m.group(1))
            break
    if start is None or level is None:
        return None
    out = [lines[start]]
    for line in lines[start + 1:]:
        m = re.match(r"^(#{1,4})\s", line)
        if m and len(m.group(1)) <= level:
            break
        out.append(line)
        if len(out) >= max_lines:
            out.append("… (sezione più lunga: leggila per intero)")
            break
    body = "\n".join(out).strip()
    # The heading alone is not an extraction.
    return body if body and body != lines[start].strip() else None


def repo_stack_signals(root: Path) -> list[str]:
    found: list[str] = []
    for name, label in REPO_SIGNALS:
        if (root / name).exists() and label not in found:
            found.append(label)
    pkg = root / "package.json"
    if pkg.exists():
        try:
            deps = json.loads(pkg.read_text(encoding="utf-8"))
            names = sorted(
                set(deps.get("dependencies", {})) | set(deps.get("devDependencies", {}))
            )
            for marker in ("react", "vue", "svelte", "next", "astro", "tailwindcss", "jquery"):
                if any(marker in n for n in names) and marker not in found:
                    found.append(marker)
        except (json.JSONDecodeError, OSError):
            pass
    return found


def discover(root: Path) -> dict:
    planning_dir, implementation_dir = read_config_paths(root)
    planning = md_files(planning_dir)
    implementation = md_files(implementation_dir)

    def rel(p: Path) -> str:
        # Classify on the path relative to the planning dir, not the basename:
        # BMAD v6 shards documents into folders (prd/epic-1.md,
        # architecture/tech-stack.md) whose file names carry no keyword — on
        # basename matching a sharded PRD produced the "no binding documents"
        # verdict, the exact opposite of the truth.
        try:
            return str(p.relative_to(planning_dir))
        except ValueError:
            return p.name

    prd = [p for p in planning if PRD_PAT.search(rel(p))]
    arch = [p for p in planning if ARCH_PAT.search(rel(p)) and p not in prd]
    ux = [p for p in planning if UX_PAT.search(rel(p)) and p not in prd and p not in arch]
    others = [p for p in planning if p not in prd and p not in arch and p not in ux]

    context = [root / c for c in CONTEXT_CANDIDATES if (root / c).exists()]
    clarifying = clarifying_docs(root, context)

    stack_section = rules_section = None
    for a in arch:
        try:
            text = a.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        stack_section = stack_section or extract_section(text, STACK_HEADING)
        rules_section = rules_section or extract_section(text, RULES_HEADING)

    def entry(p: Path) -> dict:
        return {"path": str(p.relative_to(root)), "title": front_title(p)}

    return {
        "root": str(root),
        "planning_dir": str(planning_dir.relative_to(root)) if planning_dir.is_relative_to(root) else str(planning_dir),
        "implementation_dir": str(implementation_dir.relative_to(root)) if implementation_dir.is_relative_to(root) else str(implementation_dir),
        "prd": [entry(p) for p in prd],
        "architecture": [entry(p) for p in arch],
        "ux_specs": [entry(p) for p in ux],
        "planning_other": [entry(p) for p in others],
        "implementation_specs": [entry(p) for p in implementation],
        "project_context": [entry(p) for p in context],
        "clarifying_docs": [entry(p) for p in clarifying],
        "stack_section": stack_section,
        "rules_section": rules_section,
        "repo_stack_signals": repo_stack_signals(root),
        "binding": bool(prd or arch or ux),
    }


def render_md(d: dict) -> str:
    lines = ["# Contesto BMAD per la fase implementativa", ""]
    lines.append(f"planning: `{d['planning_dir']}` · implementation: `{d['implementation_dir']}`")
    lines.append("")

    def block(label: str, items: list[dict], binding: str) -> None:
        if items:
            lines.append(f"## {label} — {binding}")
            for it in items:
                lines.append(f"- **{it['title']}** — `{it['path']}`")
            lines.append("")

    block("PRD", d["prd"], "VINCOLANTE: perimetro e requisiti")
    block("Architettura", d["architecture"], "VINCOLANTE: stack e regole obbligatori")
    block("UX / page spec", d["ux_specs"], "VINCOLANTE: struttura della pagina")
    block("Altri planning artifacts", d["planning_other"], "da leggere")
    block("Spec di implementazione già consegnati", d["implementation_specs"],
          "coerenza: non contraddirli")
    block("Contesto progetto", d["project_context"], "sempre applicato")

    if d["architecture"]:
        if d["stack_section"]:
            lines.append("## Stack dichiarato nell'architettura (obbligatorio)")
            lines.append("")
            lines.append("```")
            lines.append(d["stack_section"])
            lines.append("```")
            lines.append("")
        else:
            lines.append(
                "> architettura trovata ma **nessuna sezione stack riconosciuta** "
                "dalle euristiche: leggi il documento per intero prima di scrivere "
                "una riga di codice — il vincolo esiste anche se qui non è estratto."
            )
            lines.append("")
        if d["rules_section"]:
            lines.append("## Regole di architettura (obbligatorie)")
            lines.append("")
            lines.append("```")
            lines.append(d["rules_section"])
            lines.append("```")
            lines.append("")

    if d["clarifying_docs"]:
        lines.append("## Documenti chiarificatori (`docs/`, README)")
        lines.append("")
        lines.append(
            "Non vincolano come l'architettura, ma **vanno letti prima di dedurre "
            "lo stack dai file**: se qualcuno ha scritto qui come si costruisce "
            "questo progetto, quella è la risposta."
        )
        lines.append("")
        for e in d["clarifying_docs"]:
            lines.append(f"- **{e['title']}** — `{e['path']}`")
        lines.append("")

    if d["repo_stack_signals"]:
        lines.append(
            "segnali di stack dal repo: " + " · ".join(f"`{s}`" for s in d["repo_stack_signals"])
        )
        lines.append("")

    lines.append("## Verdetto")
    lines.append("")
    if d["binding"]:
        lines.append(
            "**VINCOLI ATTIVI.** Il deliverable si costruisce DENTRO questi documenti: "
            "stack e regole dall'architettura, perimetro dal PRD, struttura dalle page "
            "spec. Gli assi da seed (`craft_axes`, ricette, hero) riempiono solo ciò "
            "che i documenti lasciano aperto — mai il contrario. Da questi documenti "
            "non ci si scosta: se uno è impraticabile davvero, decide G1 il percorso "
            "praticabile più vicino, lo dichiara e lo scrive come varianza."
        )
        missing = [
            label
            for label, found in (
                ("architettura (stack e regole)", d["architecture"]),
                ("PRD (perimetro)", d["prd"]),
                ("UX / page spec (struttura)", d["ux_specs"]),
            )
            if not found
        ]
        if missing:
            lines.append("")
            lines.append(
                "**AVVISA SU CIÒ CHE MANCA.** Copertura parziale: manca "
                + ", ".join(missing)
                + ". Su questi fronti si decide in autonomia, quindi vanno "
                "annunciati all'owner *prima* di partire (una battuta, non "
                "bloccante) e dichiarati nello spec di accompagnamento."
            )
    else:
        lines.append(
            "**NESSUN DOCUMENTO VINCOLANTE.** Analisi autonoma obbligatoria: "
            "(1) ricerca di dominio e marketing (batch `hero_sample.py`, corpora, "
            "scout) — **da cui si derivano anche i testi**, se non forniti: "
            "headline, CTA con verbi del dominio, copy di sezione, FAQ, microcopy, "
            "`alt` e meta; mai lorem ipsum né gergo da landing generica. Il "
            "deliverable è **finito**: nessun `TODO`, nessun «da sostituire», "
            "nessun elenco di dati fittizi nel file — prezzi, orari e contatti si "
            "scrivono verosimili e si segnala **all'owner in chat** che non sono "
            "veri — (2) elenco esplicito dei casi limite della pagina, "
            "(3) review avversaria del risultato prima della consegna. "
            "Il project context, se esiste, resta applicato."
        )
        lines.append("")
        lines.append(
            "**PRIMA DI DEDURRE, LEGGI.** Le indicazioni di progetto (stack, "
            "convenzioni, vincoli) stanno in `CLAUDE.md` / `AGENTS.md`: è lì che "
            "vanno messe e lì che si cercano per prime. Se non le dicono, leggi i "
            "**documenti chiarificatori** elencati sopra (`docs/`, README) prima "
            "di dedurre lo stack dai soli file del repo. Se restano ambigui, "
            "**decide G1** (consiglio non interattivo) sullo stack che il repo rende "
            "più praticabile: si dichiara nel kernel con una riga di motivo e si "
            "lascia una varianza. Nessuna domanda all'owner."
        )
        lines.append("")
        lines.append(
            "**AVVISA PRIMA DI PARTIRE.** L'analisi autonoma non parte in silenzio: "
            "una battuta all'owner *prima* del lavoro — «nessun documento vincolante "
            "qui: procedo in autonomia (ricerca di dominio e marketing, casi limite, "
            "review avversaria); perimetro, stack e testi li scelgo io — il copy "
            "dal dominio, e contatti/prezzi/orari saranno verosimili ma non veri, "
            "te lo dico qui perché nella pagina non ci sarà scritto». È una "
            "dichiarazione, non una domanda: detto, si procede nella stessa "
            "risposta — niente «fermami se…», niente attesa. "
            "Non sostituisce la dichiarazione nello spec (o in chat se non c'è spec): "
            "l'artefatto consegnato resta pulito."
        )

    if not d["architecture"] and not d["project_context"]:
        lines.append("")
        lines.append(
            "**CANONE DI SVILUPPO OBBLIGATORIO.** Nessuna architettura e nessun "
            "project context: il progetto non detta regole, quindi valgono queste, "
            "come i craft-rules — **SOLID** (una responsabilità per componente, la "
            "presentazione non fa fetch), **SoC** (struttura/stile/comportamento/dati "
            "separati, token invece di valori hardcoded), **KISS** (la soluzione più "
            "semplice che regge i casi limite; niente framework non necessario), "
            "**DRY** (token e componenti in un posto solo, ma regola del tre: non "
            "batte KISS), **OWASP** (escaping di ogni dato non fidato, mai `innerHTML` "
            "su input o contenuti remoti, zero segreti nel bundle, "
            "`rel=\"noopener noreferrer\"`, validazione client ≠ sicurezza; ciò che "
            "spetta al backend si scrive come requisito), **vertical slices** (codice "
            "per feature end-to-end, non per strato tecnico). Il canone entra "
            "nell'avviso all'owner e le scelte non ovvie si dichiarano nello spec."
        )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="BMAD context for the implementation phase")
    ap.add_argument("root", nargs="?", default=".", help="Project root (default: cwd)")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"root inesistente: {root}")

    d = discover(root)
    if args.format == "json":
        print(json.dumps(d, ensure_ascii=False, indent=1))
    else:
        print(render_md(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
