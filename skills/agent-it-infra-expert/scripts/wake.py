#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Waking — load the agent's sanctum in one pass, or route to First Breath.

Run on activation. Determines the mode from the filesystem and, when the
sanctum exists, prints the full identity in a single read (INDEX, PERSONA,
CREED, BOND, MEMORY, CAPABILITIES). When no sanctum exists, prints a directive
to run First Breath.

This agent is memory-only (no Pulse Mode). This loads runtime memory only; it
never reads or writes config or customize.toml.

Usage:
    uv run wake.py <project-root>

    project-root: The root of the project (where _bmad/ lives)
"""

import sys
from pathlib import Path

SKILL_NAME = "agent-it-infra-expert"

IDENTITY_FILES = [
    "INDEX.md",
    "PERSONA.md",
    "CREED.md",
    "BOND.md",
    "MEMORY.md",
    "CAPABILITIES.md",
]


def emit(path: Path) -> bool:
    print(f"\n===== {path.name} =====")
    try:
        print(path.read_text(encoding="utf-8").rstrip())
        return True
    except FileNotFoundError:
        print(f"(missing: {path.name})")
        return False


def main() -> int:
    args = sys.argv[1:]
    pulse = "--pulse" in args
    positional = [a for a in args if not a.startswith("--")]
    if not positional:
        print("Usage: wake.py <project-root>", file=sys.stderr)
        return 2

    if pulse:
        print("NOTE: --pulse ignored (this agent has no Pulse Mode).", file=sys.stderr)

    project_root = Path(positional[0]).resolve()
    sanctum = project_root / "_bmad" / "memory" / SKILL_NAME

    core_ok = (
        sanctum.is_dir()
        and (sanctum / "CREED.md").is_file()
        and (sanctum / "MEMORY.md").is_file()
    )
    if not core_ok:
        print("MODE: FIRST_BREATH")
        print(f"NO SANCTUM at {sanctum}")
        print("This is your one birth. Load references/first-breath.md and follow it.")
        return 0

    print("MODE: WAKING")
    print(f"Sanctum: {sanctum}")
    missing = [name for name in IDENTITY_FILES if not emit(sanctum / name)]
    if missing:
        print(f"PARTIAL_SANCTUM: missing {', '.join(missing)}")
        print(
            "Recover: re-run init-sanctum only if safe/idempotent, or rebuild missing "
            "files from assets templates — do not continue half-born silently."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
