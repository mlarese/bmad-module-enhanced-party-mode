#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
First Breath — Deterministic sanctum scaffolding.

This script runs BEFORE the conversational awakening. It creates the sanctum
folder structure, copies template files with config values substituted,
copies all capability files and their supporting references into the sanctum,
and auto-generates CAPABILITIES.md from capability prompt frontmatter.

After this script runs, the sanctum is fully self-contained — the agent does
not depend on the skill bundle location for normal operation.

This initializes the agent's runtime sanctum memory, not build-time config. It
reads config.yaml and config.user.yaml strictly to substitute values into the
sanctum templates, and it never writes or authors any config file. Build-time
customization is owned by customize.toml, a separate surface this script never
touches.

Usage:
    uv run init-sanctum.py <project-root> <skill-path>

    project-root: The root of the project (where _bmad/ lives)
    skill-path:   Path to the skill directory (where SKILL.md, references/, assets/ live)
"""

import sys
import re
import shutil
from datetime import date
from pathlib import Path

# --- Agent-specific configuration (set by builder) ---

SKILL_NAME = "agent-frontend-taste"
SANCTUM_DIR = SKILL_NAME

# Files that stay in the skill bundle (only used during First Breath)
SKILL_ONLY_FILES = {"first-breath.md"}

TEMPLATE_FILES = [
    "INDEX-template.md",
    "PERSONA-template.md",
    "CREED-template.md",
    "BOND-template.md",
    "MEMORY-template.md",
]

# Whether the owner can teach this agent new capabilities
EVOLVABLE = True

# --- End agent-specific configuration ---

def parse_yaml_config(config_path: Path) -> dict:
    """Simple YAML key-value parser. Handles top-level scalar values only."""
    config = {}
    if not config_path.exists():
        return config
    with open(config_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                value = value.strip().strip("'\"")
                if value:
                    config[key.strip()] = value
    return config

def parse_frontmatter(file_path: Path) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    meta = {}
    with open(file_path) as f:
        content = f.read()

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return meta

    for line in match.group(1).strip().split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip("'\"")
    return meta

def copy_references(source_dir: Path, dest_dir: Path) -> list[str]:
    """Copy all reference files (except skill-only files) into the sanctum."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []

    for source_file in sorted(source_dir.iterdir()):
        if source_file.name in SKILL_ONLY_FILES:
            continue
        if source_file.is_file():
            shutil.copy2(source_file, dest_dir / source_file.name)
            copied.append(source_file.name)

    return copied

def copy_scripts(source_dir: Path, dest_dir: Path) -> list[str]:
    """Copy any scripts the capabilities might use into the sanctum."""
    if not source_dir.exists():
        return []
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []

    for source_file in sorted(source_dir.iterdir()):
        if source_file.is_file() and source_file.name != "init-sanctum.py":
            shutil.copy2(source_file, dest_dir / source_file.name)
            copied.append(source_file.name)

    return copied

def discover_capabilities(references_dir: Path, sanctum_refs_path: str) -> list[dict]:
    """Scan references/ for capability prompt files with frontmatter."""
    capabilities = []

    for md_file in sorted(references_dir.glob("*.md")):
        if md_file.name in SKILL_ONLY_FILES:
            continue
        meta = parse_frontmatter(md_file)
        if meta.get("name") and meta.get("code"):
            capabilities.append({
                "name": meta["name"],
                "description": meta.get("description", ""),
                "code": meta["code"],
                "source": f"{sanctum_refs_path}/{md_file.name}",
            })
    return capabilities

def generate_capabilities_md(capabilities: list[dict], evolvable: bool) -> str:
    """Generate CAPABILITIES.md content from discovered capabilities."""
    lines = [
        "# Capabilities",
        "",
        "## Built-in",
        "",
        "| Code | Name | Description | Source |",
        "|------|------|-------------|--------|",
    ]
    for cap in capabilities:
        lines.append(
            f"| [{cap['code']}] | {cap['name']} | {cap['description']} | `{cap['source']}` |"
        )

    lines.extend([
        "",
        "Load the Source file before answering when the owner invokes a code or clear intent.",
    ])

    if evolvable:
        lines.extend([
            "",
            "## Learned",
            "",
            "_Capabilities added by the owner over time. Prompts live in `capabilities/`._",
            "",
            "| Code | Name | Description | Source | Added |",
            "|------|------|-------------|--------|-------|",
            "",
            "## How to Add a Capability",
            "",
            'Tell me "I want you to be able to do X" and we\'ll create it together.',
            "I'll write the prompt, save it to `capabilities/`, and register it here.",
            "Next session, I'll know how.",
            "Load `references/capability-authoring.md` for mechanics. At author time hold "
            "`references/prompt-quality-canon.md` per CREED.",
        ])

    lines.extend([
        "",
        "## Tools",
        "",
        "Prefer crafting your own tools over depending on external ones. A script you wrote "
        "and saved is more reliable than an external API. Use the file system creatively.",
        "",
        "### User-Provided Tools",
        "",
        "_MCP servers, APIs, or services the owner has made available. Document them here._",
    ])

    return "\n".join(lines) + "\n"

def substitute_vars(content: str, variables: dict) -> str:
    """Replace {var_name} placeholders with values from the variables dict."""
    for key, value in variables.items():
        content = content.replace(f"{{{key}}}", value)
    return content

def assert_is_this_skill(skill_path: Path) -> None:
    """Refuse to build or refresh a sanctum from the wrong source.

    Both paths write the materials the agent loads at runtime. Pointed at
    another skill (or a half-empty directory) they would fill this agent's
    sanctum with someone else's rules, and the damage only surfaces next
    session, as instructions that make no sense.
    """
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists() or not (skill_path / "references").is_dir():
        print(f"Rifiuto: {skill_path} non è una skill (manca SKILL.md o references/).")
        sys.exit(1)
    if f"name: {SKILL_NAME}" not in skill_md.read_text(encoding="utf-8", errors="replace")[:400]:
        print(f"Rifiuto: {skill_md} non è {SKILL_NAME} — il sanctum finirebbe con i materiali di un'altra skill.")
        sys.exit(1)


def copy_assets(source_dir: Path, dest_dir: Path) -> list[str]:
    """Sync runtime assets (catalogs, generated galleries, media) into the sanctum.

    Birth templates are skipped: they build the identity files once and have no
    runtime role. Media directories are mirrored because the hero gallery reads
    real photos from them.
    """
    if not source_dir.exists():
        return []
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for source in sorted(source_dir.iterdir()):
        if source.name.endswith("-template.md"):
            continue
        if source.is_file():
            shutil.copy2(source, dest_dir / source.name)
            copied.append(source.name)
        elif source.is_dir():
            shutil.copytree(source, dest_dir / source.name, dirs_exist_ok=True)
            copied.append(source.name + "/")
    return copied


def refresh_sanctum(sanctum_path: Path, skill_path: Path) -> int:
    """Re-sync the MATERIALS an existing sanctum carries, never its identity.

    First Breath copies references and scripts into the sanctum, and
    CAPABILITIES.md points at those copies — so the agent loads from the
    sanctum, not from the skill. Without a refresh the two drift silently:
    rules edited in the skill keep having no effect, and files added after
    the birth (a new surface, a new script) never arrive at all.

    PERSONA / CREED / BOND / MEMORY / INDEX / capabilities/ / sessions/ are the
    agent's self and are never touched here. CAPABILITIES.md is left alone too
    (it may carry learned capabilities); new or removed built-ins are reported
    so the owner can decide.
    """
    references_dir = skill_path / "references"
    scripts_dir = skill_path / "scripts"
    sanctum_refs = sanctum_path / "references"
    sanctum_scripts = sanctum_path / "scripts"

    assert_is_this_skill(skill_path)

    before_refs = {p.name for p in sanctum_refs.iterdir() if p.is_file()} if sanctum_refs.is_dir() else set()
    before_scripts = {p.name for p in sanctum_scripts.iterdir() if p.is_file()} if sanctum_scripts.is_dir() else set()

    copied_refs = copy_references(references_dir, sanctum_refs)
    copied_scripts = copy_scripts(scripts_dir, sanctum_scripts)
    copied_assets = copy_assets(skill_path / "assets", sanctum_path / "assets")

    new_refs = sorted(set(copied_refs) - before_refs)
    new_scripts = sorted(set(copied_scripts) - before_scripts)
    # Files still in the sanctum that the skill no longer has: reported, never
    # deleted — removing something the owner may have hand-written is worse
    # than leaving a stale copy that nothing points to.
    orphan_refs = sorted(before_refs - set(copied_refs))
    orphan_scripts = sorted(before_scripts - set(copied_scripts))

    print(f"Refreshed sanctum materials at {sanctum_path}")
    print(f"  references: {len(copied_refs)} synced" + (f", {len(new_refs)} new" if new_refs else ""))
    for n in new_refs:
        print(f"    + {n}")
    print(f"  scripts:    {len(copied_scripts)} synced" + (f", {len(new_scripts)} new" if new_scripts else ""))
    for n in new_scripts:
        print(f"    + {n}")
    print(f"  assets:     {len(copied_assets)} synced (template di nascita esclusi)")
    for label, orphans in (("reference", orphan_refs), ("script", orphan_scripts)):
        for n in orphans:
            print(f"  ! {label} nel sanctum ma non più nello skill: {n} (non rimosso)")
    if orphan_refs or orphan_scripts:
        # Leaving the file is right (it might be hand-written); leaving the RULE
        # in force is not. A reference the skill has dropped keeps being
        # loadable from the sanctum, and an abrogated rule that still applies is
        # worse than a missing one.
        print("    → un file orfano resta sul disco ma NON è più una regola: "
              "non caricarlo, e se serviva davvero rimettilo nello skill.")

    # Built-in capabilities are discovered from frontmatter; a mismatch means
    # CAPABILITIES.md is stale, but rewriting it could drop learned entries.
    discovered = {c["code"] for c in discover_capabilities(references_dir, "references")}
    cap_file = sanctum_path / "CAPABILITIES.md"
    if cap_file.exists():
        listed = set(re.findall(r"^\|\s*\[([A-Z]{2})\]", cap_file.read_text(encoding="utf-8"), re.M))
        missing, extra = sorted(discovered - listed), sorted(listed - discovered)
        if missing or extra:
            print("  ! CAPABILITIES.md non allineata (non riscritta: può contenere capability apprese)")
            if missing:
                print(f"    da aggiungere: {', '.join(missing)}")
            if extra:
                print(f"    non più nello skill: {', '.join(extra)}")

    print()
    print("Identità intatta: PERSONA · CREED · BOND · MEMORY · INDEX · capabilities/ · sessions/ non toccati.")
    return 0


def main():
    if len(sys.argv) < 3:
        print("Usage: uv run init-sanctum.py <project-root> <skill-path> [--refresh]")
        sys.exit(1)

    project_root = Path(sys.argv[1]).resolve()
    skill_path = Path(sys.argv[2]).resolve()
    do_refresh = "--refresh" in sys.argv[3:]

    # `assert_is_this_skill` refuses the wrong skill; nothing refused the wrong
    # PROJECT. With `mkdir(parents=True)` downstream, a typo silently built a
    # whole sanctum inside a directory that did not exist a second earlier —
    # a second birth, with a blank MEMORY, while the real sanctum sat untouched
    # elsewhere. Creating the project root is never this script's job.
    if not project_root.is_dir():
        print(f"Rifiuto: project-root inesistente: {project_root}")
        print("Un sanctum si scrive in un progetto che esiste — questo è un path sbagliato.")
        sys.exit(1)

    # Paths
    bmad_dir = project_root / "_bmad"
    memory_dir = bmad_dir / "memory"
    sanctum_path = memory_dir / SANCTUM_DIR
    assets_dir = skill_path / "assets"
    references_dir = skill_path / "references"
    scripts_dir = skill_path / "scripts"

    # Sanctum subdirectories
    sanctum_refs = sanctum_path / "references"
    sanctum_scripts = sanctum_path / "scripts"

    # Relative path for CAPABILITIES.md references (agent loads from within sanctum)
    sanctum_refs_path = "references"

    assert_is_this_skill(skill_path)

    # Check if sanctum already exists
    if sanctum_path.exists():
        if do_refresh:
            sys.exit(refresh_sanctum(sanctum_path, skill_path))
        print(f"Sanctum already exists at {sanctum_path}")
        print("This agent has already been born. Skipping First Breath scaffolding.")
        print("Per ri-sincronizzare references/ e scripts/ (identità intatta): --refresh")
        sys.exit(0)
    if do_refresh:
        print(f"Nessun sanctum da aggiornare a {sanctum_path} — serve prima First Breath.")
        sys.exit(1)

    # Load config
    config = {}
    for config_file in ["config.yaml", "config.user.yaml"]:
        config.update(parse_yaml_config(bmad_dir / config_file))

    # Build variable substitution map
    today = date.today().isoformat()
    variables = {
        "user_name": config.get("user_name", "friend"),
        "communication_language": config.get("communication_language", "English"),
        "birth_date": today,
        "project_root": str(project_root),
        "sanctum_path": str(sanctum_path),
    }

    # Create sanctum structure
    sanctum_path.mkdir(parents=True, exist_ok=True)
    (sanctum_path / "capabilities").mkdir(exist_ok=True)
    (sanctum_path / "sessions").mkdir(exist_ok=True)
    print(f"Created sanctum at {sanctum_path}")

    # Copy reference files (capabilities + techniques + guidance) into sanctum
    copied_refs = copy_references(references_dir, sanctum_refs)
    print(f"  Copied {len(copied_refs)} reference files to sanctum/references/")
    for name in copied_refs:
        print(f"    - {name}")

    # Copy any supporting scripts into sanctum
    copied_scripts = copy_scripts(scripts_dir, sanctum_scripts)
    if copied_scripts:
        print(f"  Copied {len(copied_scripts)} scripts to sanctum/scripts/")
        for name in copied_scripts:
            print(f"    - {name}")

    # Copy and substitute template files
    for template_name in TEMPLATE_FILES:
        template_path = assets_dir / template_name
        if not template_path.exists():
            print(f"  Warning: template {template_name} not found, skipping")
            continue

        # Remove "-template" from the output filename and uppercase it
        output_name = template_name.replace("-template", "").upper()
        # Fix extension casing: .MD -> .md
        output_name = output_name[:-3] + ".md"

        content = template_path.read_text()
        content = substitute_vars(content, variables)

        output_path = sanctum_path / output_name
        output_path.write_text(content)
        print(f"  Created {output_name}")

    # Auto-generate CAPABILITIES.md from references/ frontmatter
    capabilities = discover_capabilities(references_dir, sanctum_refs_path)
    capabilities_content = generate_capabilities_md(capabilities, evolvable=EVOLVABLE)
    (sanctum_path / "CAPABILITIES.md").write_text(capabilities_content)
    print(f"  Created CAPABILITIES.md ({len(capabilities)} built-in capabilities discovered)")

    print()
    print("First Breath scaffolding complete.")
    print("The conversational awakening can now begin.")
    print(f"Sanctum: {sanctum_path}")

if __name__ == "__main__":
    main()
