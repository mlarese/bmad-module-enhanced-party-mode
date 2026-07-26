#!/usr/bin/env python3
"""Pick hero copy layout (placement × panel) from seed — deterministic 'random'.

Bias to kill: always text-right + solid plate.
Pool mixes right/left/center × solid/transparent.

Usage:
  uv run scripts/hero_copy.py
  uv run scripts/hero_copy.py --seed 2026072517
  uv run scripts/hero_copy.py --seed 2026072517 --exclude right-solid --exclude plate-locale-right
  uv run scripts/hero_copy.py --last right-solid center-transparent
"""

from __future__ import annotations

import argparse
import random
from datetime import datetime

# Equal-weight hypotheses. Label = placement-panel.
POOL: list[str] = [
    "right-solid",
    "right-transparent",
    "left-solid",
    "left-transparent",
    "center-solid",
    "center-transparent",
]

# How each label maps to craft tokens (for DX/AF declare).
META: dict[str, dict[str, str]] = {
    "right-solid": {
        "placement": "right",
        "panel": "solid",
        "hint": "testo a destra su plate/pannello tinta piena (≤40% area); foto intatta a sinistra",
    },
    "right-transparent": {
        "placement": "right",
        "panel": "transparent",
        "hint": "testo a destra senza plate; leggibilità via negative-space / knockout / velo chiaro locale",
    },
    "left-solid": {
        "placement": "left",
        "panel": "solid",
        "hint": "testo a sinistra su plate/pannello pieno; foto a destra intatta",
    },
    "left-transparent": {
        "placement": "left",
        "panel": "transparent",
        "hint": "testo a sinistra, fondo trasparente; crop/negative-space o blend",
    },
    "center-solid": {
        "placement": "center",
        "panel": "solid",
        "hint": "blocco testo centrato su plate opaco (non full-bleed); foto intorno intatta",
    },
    "center-transparent": {
        "placement": "center",
        "panel": "transparent",
        "hint": "titolo centrato in hero senza plate; niente velo scuro full-bleed — usa luce del crop",
    },
}


def pick(seed: int, exclude: list[str] | None = None) -> str:
    exclude_set = {e.strip() for e in (exclude or []) if e.strip()}
    # Also accept short aliases from MEMORY last_hero_treatments that imply a copy layout
    aliases = {
        "plate locale": "right-solid",  # historical bias → treat as right-solid for exclusion
        "plate-locale": "right-solid",
        "plate-locale-right": "right-solid",
        "editorial": None,  # different axis — don't map
    }
    mapped_exclude: set[str] = set()
    for e in exclude_set:
        if e in POOL:
            mapped_exclude.add(e)
        elif e in aliases and aliases[e]:
            mapped_exclude.add(aliases[e])  # type: ignore[arg-type]

    candidates = [p for p in POOL if p not in mapped_exclude]
    if not candidates:
        candidates = list(POOL)

    # Seeded stream, not the multiplicative hash: on sequential hourly seeds
    # the hash walked the pool in a rigid +3/+1 cycle (measured over 24h),
    # so the "variety" was a fixed rotation, not a draw.
    return random.Random(f"{seed}|hero-copy").choice(candidates)


def main() -> None:
    ap = argparse.ArgumentParser(description="Hero copy layout from seed")
    ap.add_argument(
        "--seed",
        type=int,
        default=int(datetime.now().strftime("%Y%m%d%H")),
        help="YYYYMMDDHH (default: now)",
    )
    ap.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Labels to skip (repeatable); usually last_hero_copy from MEMORY",
    )
    ap.add_argument(
        "--last",
        nargs="*",
        default=[],
        help="Shortcut: last N hero_copy labels from MEMORY (same as --exclude)",
    )
    args = ap.parse_args()
    exclude = list(args.exclude) + list(args.last)
    choice = pick(args.seed, exclude)
    meta = META[choice]
    print(f"hero_copy: {choice}")
    print(f"hero_copy_placement: {meta['placement']}")
    print(f"hero_copy_panel: {meta['panel']}")
    print(f"seed: {args.seed}")
    print(f"hint: {meta['hint']}")
    if exclude:
        print(f"excluded: {', '.join(exclude)}")


if __name__ == "__main__":
    main()
