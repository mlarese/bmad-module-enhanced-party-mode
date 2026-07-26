#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Sanctum health — deterministic metrics for Pulse / birthday cleanup.

Usage:
    uv run sanctum-health.py <project-root> [--placeholders] [--json]

Emits compact JSON (or human text) with: MEMORY token estimate, session
inventory (age_days, over_14d), INDEX↔disk drift, optional leftover `{...}`
placeholders. Judgment (what to prune) stays with the agent.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

SKILL_NAME = "agent-world-cpa"
IDENTITY = [
    "INDEX.md",
    "PERSONA.md",
    "CREED.md",
    "BOND.md",
    "MEMORY.md",
    "CAPABILITIES.md",
    "PULSE.md",
    "SCADENZE.md",
]


def approx_tokens(text: str) -> int:
    # Rough guardrail metric (~4 chars/token); identical input → identical count.
    return max(0, (len(text) + 3) // 4)


def parse_index_paths(index_text: str) -> set[str]:
    found: set[str] = set()
    for m in re.finditer(r"`([^`]+)`", index_text):
        name = m.group(1).strip()
        if name and not name.endswith("/"):
            found.add(name.split("/")[-1] if "/" in name else name)
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="Sanctum health metrics for agent-world-cpa")
    ap.add_argument("project_root", type=Path)
    ap.add_argument("--placeholders", action="store_true", help="Scan sanctum .md for leftover {...}")
    ap.add_argument("--json", action="store_true", help="Emit JSON only (default)")
    ap.add_argument("--text", action="store_true", help="Emit human-readable text")
    args = ap.parse_args()

    sanctum = args.project_root.resolve() / "_bmad" / "memory" / SKILL_NAME
    report: dict = {"sanctum": str(sanctum), "ok": sanctum.is_dir()}

    if not sanctum.is_dir():
        report["error"] = "sanctum missing"
        print(json.dumps(report, indent=2))
        return 1

    missing = [n for n in IDENTITY if not (sanctum / n).is_file()]
    report["structure_missing"] = missing

    mem = sanctum / "MEMORY.md"
    if mem.is_file():
        text = mem.read_text(encoding="utf-8")
        report["memory_chars"] = len(text)
        report["memory_approx_tokens"] = approx_tokens(text)
        report["memory_over_1500"] = report["memory_approx_tokens"] > 1500

    today = date.today()
    sessions_dir = sanctum / "sessions"
    sessions = []
    if sessions_dir.is_dir():
        for p in sorted(sessions_dir.glob("*.md")):
            try:
                d = datetime.strptime(p.stem[:10], "%Y-%m-%d").date()
                age = (today - d).days
            except ValueError:
                age = None
            sessions.append(
                {
                    "path": f"sessions/{p.name}",
                    "age_days": age,
                    "over_14d": age is not None and age > 14,
                    "approx_tokens": approx_tokens(p.read_text(encoding="utf-8")),
                }
            )
    report["sessions"] = sessions
    report["prune_candidates"] = [s["path"] for s in sessions if s.get("over_14d")]

    index_path = sanctum / "INDEX.md"
    listed: set[str] = set()
    if index_path.is_file():
        listed = parse_index_paths(index_path.read_text(encoding="utf-8"))
    on_disk = {p.name for p in sanctum.iterdir() if p.is_file() and p.suffix == ".md"}
    # ignore standard identity already in INDEX Standard Files section loosely
    organic_disk = on_disk - set(IDENTITY) - {"INDEX.md"}
    report["index_unlisted_on_disk"] = sorted(organic_disk - listed)
    report["index_listed_missing"] = sorted(
        n for n in listed if n.endswith(".md") and n not in on_disk and not n.startswith("sessions")
    )

    if args.placeholders:
        hits = []
        for p in sorted(sanctum.rglob("*.md")):
            if "sessions" in p.parts:
                continue
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if re.search(r"\{[a-zA-Z_][^}]*\}", line) or "{awaiting" in line or "{Shaped" in line or "{Start" in line or "{Discovered" in line or "{Explicit" in line or "{Develops" in line:
                    hits.append({"file": str(p.relative_to(sanctum)), "line": i, "text": line.strip()[:120]})
        report["placeholders"] = hits

    if args.text and not args.json:
        print(f"Sanctum: {sanctum}")
        print(f"Missing identity: {missing or 'none'}")
        if "memory_approx_tokens" in report:
            print(f"MEMORY ≈ {report['memory_approx_tokens']} tokens (over_1500={report['memory_over_1500']})")
        print(f"Sessions: {len(sessions)}; prune_candidates: {report['prune_candidates']}")
        print(f"Unlisted on disk: {report['index_unlisted_on_disk']}")
        print(f"Listed missing: {report['index_listed_missing']}")
        if args.placeholders:
            print(f"Placeholders: {len(report.get('placeholders', []))}")
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
