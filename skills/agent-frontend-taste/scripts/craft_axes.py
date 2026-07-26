#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Pick composition / surface / type axes from seed — deterministic 'random'.

Biases to kill: centered 1200px container + everything text-left; flat tint
sections after a crafted hero; display+body pair with no scale law.

The script proposes; DX/UE/AF must still justify the pick against activity and
the AW batch (see references/craft-rules.md). It never emits hex.

Usage:
  uv run scripts/craft_axes.py
  uv run scripts/craft_axes.py --seed 2026072517 --activity restaurant
  uv run scripts/craft_axes.py --last-grid fine --last-texture rule-lines
  uv run scripts/craft_axes.py --sections 7 --surface dashboard
"""

from __future__ import annotations

import argparse
import random
from collections import Counter
from datetime import datetime

GRID_SYSTEMS: dict[str, str] = {
    "fine": "repeat(28, 1fr) — placement esplicito (grid-column: 6/16); off-center come misura",
    "asym-rail": "traccia fissa 16vw + 1fr — rail metadati/label, asimmetria cablata su ogni sezione",
    "12-col": "repeat(12, 1fr) + span — solo product/dashboard, da motivare",
}

# activity keyword -> grid systems allowed, in preference order
GRID_BY_ACTIVITY: list[tuple[tuple[str, ...], list[str]]] = [
    (("dashboard", "admin", "saas", "product", "crm", "app"), ["12-col", "asym-rail"]),
    (
        ("restaurant", "ristorante", "hotel", "hospitality", "spa", "food", "wine"),
        ["fine", "asym-rail"],
    ),
    (
        ("studio", "portfolio", "atelier", "sartoria", "brand", "agency", "editorial", "film"),
        ["fine", "asym-rail"],
    ),
]

BLEED_RHYTHMS: dict[str, str] = {
    "contained": "rail rigoroso su tutta la pagina; full-bleed riservato ai media",
    "alternating": "fasce 100vw alternate a blocchi in colonna",
}

SURFACE_TEXTURES: dict[str, str] = {
    "rule-lines": "hairline 1px solid come sistema (token --rule) su sezioni, card, tabelle",
    "rule-lines-dashed": "hairline 1px dashed come grafica di casa — non stato disabled",
    "svg-pattern": "data-URI ripetuto, background-size agganciato al modulo di griglia (1rem / 18px / 4rem)",
    "baseline-rule": "background-size: 100% <line-height>px + repeat-y — carta rigata sul passo della riga",
    "grain": "feTurbulence/noise come texture vera, non velo al 3% su tutto",
}

THIRD_VOICES: dict[str, str] = {
    "mono": "label, metriche, eyebrow, nav — voce primaria, non 'font del codice'",
    "italic": "italic dedicato (anche di altra famiglia) per citazioni e didascalie",
    "serif-accent": "serif d'accento su statement e numeri di sezione",
}

# Tonal keys for the surface rhythm, with house weights: paper is the ground,
# accent-band is the rare gesture. Caps keep the loud keys from taking over.
TONAL_WEIGHTS: dict[str, int] = {
    "paper": 4,
    "dark": 3,
    "light-warm": 2,
    "media-bleed": 2,
    "accent-band": 1,
}
TONAL_CAPS: dict[str, int] = {"media-bleed": 2, "accent-band": 2}

# Per-section alignment registers. center appears at most twice by construction.
ALIGNMENTS: list[str] = ["left", "rail-right", "split", "full-bleed", "center", "right-meta"]


def _rng(seed: int, axis: int | str) -> random.Random:
    """One independent stream per axis — the dashboard/mobile recipe law.

    The previous Knuth multiplicative hash correlated every axis through the
    same +K step on sequential hourly seeds: measured over a full year of
    hourly seeds, the joint output collapsed to 112 distinct recipes out of a
    32k nominal space (0.3%), with type_scale covering 5 of its 27 combos and
    every axis stepping 0/+1 per hour in lockstep. Per-axis streams were
    already the fix in dashboard_recipe.py; this backports it.
    """
    return random.Random(f"{seed}|{axis}")


def _pick(
    pool: list[str],
    seed: int,
    salt: int | str,
    exclude: list[str] | None = None,
    weights: dict[str, float] | None = None,
) -> str:
    excluded = {e.strip() for e in (exclude or []) if e.strip()}
    candidates = [p for p in pool if p not in excluded] or list(pool)
    if weights:
        return _rng(seed, salt).choices(
            candidates, weights=[weights.get(c, 1.0) for c in candidates]
        )[0]
    return _rng(seed, salt).choice(candidates)


# The third voice tunes to the house texture: a hairline system reads as
# technical (mono labels), ruled paper and grain read as material (serif,
# italic). Bias, never a removal — svg-pattern stays neutral.
TEXTURE_VOICE_AFFINITY: dict[str, dict[str, float]] = {
    "rule-lines": {"mono": 3},
    "rule-lines-dashed": {"mono": 2},
    "baseline-rule": {"serif-accent": 2, "italic": 2},
    "grain": {"italic": 2, "serif-accent": 2},
}


def grid_pool(activity: str | None, surface: str) -> list[str]:
    hay = (activity or "").lower()
    if surface == "dashboard":
        return ["12-col", "asym-rail"]
    for keys, pool in GRID_BY_ACTIVITY:
        if any(k in hay for k in keys):
            return pool
    return ["fine", "asym-rail"]


def type_scale(seed: int) -> tuple[float, float, float]:
    """Display ratio ~1.5, body ratio 1.2–1.25, step ratio for the ladder.

    Three independent streams: with the old shared hash these moved in
    lockstep and only 5 of the 27 combinations ever occurred.
    """
    display = _rng(seed, "scale-display").choice([1.45, 1.5, 1.55])
    body = _rng(seed, "scale-body").choice([1.2, 1.22, 1.25])
    step = _rng(seed, "scale-step").choice([1.2, 1.25, 1.333])
    return display, body, step


def alignment_map(seed: int, sections: int) -> list[str]:
    """One register per section: never mono-alignment, center at most twice.

    Generative under constraints, not a rotation: the old cyclic construction
    admitted exactly 5 possible maps in the whole seed space, with `center`
    always in the same two slots. Now the non-center registers are drawn with
    no immediate repeat, and the mid-page statement position jitters — the
    invariants stay (≤2 center, never adjacent, closing ≥ statement+2).
    """
    rng = _rng(seed, "alignment")
    base = [a for a in ALIGNMENTS if a != "center"]
    out: list[str] = []
    prev: str | None = None
    for _ in range(sections):
        pick = rng.choice([a for a in base if a != prev])
        out.append(pick)
        prev = pick
    if sections >= 4:
        # Statement somewhere mid-page (seeded jitter), closing CTA centered
        # most of the time — never adjacent to the statement.
        lo, hi = 2, max(2, sections - 3)
        statement = rng.randint(lo, hi)
        out[statement] = "center"
        closing = sections - 1
        if closing >= statement + 2 and rng.random() < 0.6:
            out[closing] = "center"
    return out


def surface_rhythm(seed: int, sections: int) -> list[str]:
    """Weighted seeded chain: never two identical keys in a row, loud keys capped.

    The old version rotated one of 4 fixed cycles — 4 possible rhythms, ever.
    Now each section draws from the tonal keys minus the previous one, with
    house weights (paper is the ground, accent-band the rare gesture) and hard
    caps on media-bleed and accent-band so a long page cannot become a fair.
    """
    rng = _rng(seed, "rhythm")
    used: Counter[str] = Counter()
    out: list[str] = []
    prev: str | None = None
    for _ in range(sections):
        cands = [
            k for k in TONAL_WEIGHTS
            if k != prev and used[k] < TONAL_CAPS.get(k, sections)
        ]
        pick = rng.choices(cands, weights=[TONAL_WEIGHTS[k] for k in cands])[0]
        out.append(pick)
        used[pick] += 1
        prev = pick
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Composition / surface / type axes from seed")
    ap.add_argument(
        "--seed",
        type=int,
        default=int(datetime.now().strftime("%Y%m%d%H")),
        help="YYYYMMDDHH (default: now — same clock as motion and hero_copy)",
    )
    ap.add_argument("--activity", help="es. ristorante, sartoria, saas, hotel — biases grid pool")
    ap.add_argument(
        "--surface",
        choices=["marketing", "dashboard"],
        default="marketing",
        help="dashboard restricts the grid pool",
    )
    ap.add_argument("--sections", type=int, default=7, help="How many sections the page has (1-40)")
    ap.add_argument("--last-grid", action="append", default=[], help="last_grid_systems from MEMORY")
    ap.add_argument(
        "--last-texture", action="append", default=[], help="last_surface_textures from MEMORY"
    )
    ap.add_argument("--last-voice", action="append", default=[], help="last_type_voices from MEMORY")
    args = ap.parse_args()

    # Was `max(3, args.sections)`: safe but mute — asking for 0 quietly returned 3,
    # and 999 produced two thousand lines nobody reads. Say what is out of range.
    if not 1 <= args.sections <= 40:
        raise SystemExit(
            f"--sections {args.sections}: fuori intervallo (1-40). "
            "Una pagina con meno di 3 sezioni non ha un ritmo di superficie da dichiarare."
        )
    sections = max(3, args.sections)
    pool = grid_pool(args.activity, args.surface)
    grid = _pick(pool, args.seed, 1, args.last_grid)
    bleed = _pick(list(BLEED_RHYTHMS), args.seed, 2)
    texture = _pick(list(SURFACE_TEXTURES), args.seed, 3, args.last_texture)
    voice = _pick(list(THIRD_VOICES), args.seed, 4, args.last_voice,
                  weights=TEXTURE_VOICE_AFFINITY.get(texture))
    d_ratio, b_ratio, step = type_scale(args.seed)

    print(f"seed: {args.seed}")
    print()
    print("# Composizione")
    print(f"grid_system: {grid} — {GRID_SYSTEMS[grid]}")
    print(f"bleed_rhythm: {bleed} — {BLEED_RHYTHMS[bleed]}")
    print("alignment_map:")
    for i, a in enumerate(alignment_map(args.seed, sections), 1):
        print(f"  {i}. {a}")
    print("measure: headline 10–20ch · body 55–68ch")
    print("obbligo: ≥2 blocchi con grid-column <start>/<end> esplicito (start≠1 o end≠-1)")
    print()
    print("# Superfici")
    print(f"surface_texture: {texture} — {SURFACE_TEXTURES[texture]}")
    print("surface_rhythm:")
    for i, k in enumerate(surface_rhythm(args.seed, sections), 1):
        print(f"  {i}. {k}")
    print("luce: radial-gradient(circle at X Y, <accento>, transparent 8–15rem) oppure blur(20–30px) dietro")
    print("token: --bg-paper · --bg-dirty-white · --bg-inv + 1–2 fasce color-blocking dalla palette")
    print()
    print("# Tipografia")
    tuned = " (in affinità con la texture)" if TEXTURE_VOICE_AFFINITY.get(texture) else ""
    print(f"type_voices: display · body · {voice} — {THIRD_VOICES[voice]}{tuned}")
    print(f"type_scale: base 1200px · step ×{step} · display max = min ×{d_ratio} · body max = min ×{b_ratio}")
    print("tracking: display -0.03em → -0.06em · eyebrow +0.10em → +0.18em uppercase")
    print("leading: display 0.80–0.95 · body 1.35–1.50")
    print("numerali: tabular-nums su ogni cifra in colonna · text-wrap balance/pretty")
    print()
    excluded = args.last_grid + args.last_texture + args.last_voice
    if excluded:
        print(f"excluded: {', '.join(excluded)}")
    print("Nota: proposta da seed — tienila o alterala tu contro activity + batch ≥30, poi dichiarala. Non si sottopone all'owner.")


if __name__ == "__main__":
    main()
