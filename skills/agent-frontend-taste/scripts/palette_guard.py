#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Measure a palette the way the eye sees it: by hue sector and by area.

Why this exists — measured, not theorised. Across the delivered demos the
accent colour was different every time (rame, zafferano, corallo, limone),
yet the pages read as "all green": `--ink`, the structural dark that fills the
hero, the dark bands and the footer, was green or teal in 6 files out of 9,
with saturation up to 66%. The anti-repetition rule was checking the family
NAME (`laguna-pino`, `abete-rame`, `euganeo-zafferano` — all different) while
the hue stayed in the same place. A name is not a colour.

So this script answers two questions a name cannot:
  1. which hue sector does this palette actually sit in?
  2. is the structural dark a branded near-neutral, or a saturated colour
     covering half the page?

Usage:
    uv run scripts/palette_guard.py --check apps/<slug>/index.html
    uv run scripts/palette_guard.py --hex '#141C18,#C96F3A,#F3F0EA'
    uv run scripts/palette_guard.py --check pagina.html --last verde,teal
    uv run scripts/palette_guard.py --check pagina.html --format json
"""

from __future__ import annotations

import argparse
import colorsys
import json
import re
import sys
from pathlib import Path

# Hue sectors, in the order the eye groups them. Names match craft-rules.
SECTORS: list[tuple[str, float, float]] = [
    ("rosso", 345, 15),
    ("terra", 15, 45),
    ("giallo", 45, 70),
    ("verde", 70, 165),
    ("teal", 165, 200),
    ("blu", 200, 260),
    ("viola", 260, 300),
    ("magenta", 300, 345),
]

DARK_L = 30.0        # at or below this lightness it is a structural dark

# Two thresholds, and they must not collapse into one. Below NEUTRAL_C a colour
# has no tint left to name; between NEUTRAL_C and INK_MAX_C it is a branded
# near-neutral, legitimate on a large surface; above INK_MAX_C it is a full
# colour and it takes over the page. Calibrated on the delivered demos: true
# neutrals (#141618, #15171A, #1c1814) sit at 1.4-3.1, while #1A2A22 — the
# green that filled a hero and made the whole page read green — sits at 6.2.
NEUTRAL_C = 4.0      # at or below this chroma there is no sector to speak of
INK_MAX_C = 6.0      # perceived chroma a dark on a large surface stays under

# Saturation alone lies about dark colours: at L=4% a saturation of 17% is
# invisible, at L=27% the same number is plainly green. What the eye reads is
# the distance from grey, which collapses as a colour approaches black or
# white — so the ceiling applies to this, not to raw HSL saturation.
def chroma(sat: float, light: float) -> float:
    """Perceived colourfulness: saturation damped by distance from mid-grey."""
    return sat * (1 - abs(2 * light / 100 - 1))


# Fallback only: when there is no CSS to measure (bare --hex input), guess the
# role from the token name. Real files are measured by usage instead.
LARGE_AREA_HINTS = ("ink", "bg", "background", "paper", "surface", "fondo",
                    "base", "dark", "deep", "footer", "hero", "carta")

# Selectors that paint a large surface. A colour used as their background is a
# large area no matter what it is called — `--abete` says nothing about role.
BIG_SELECTOR_RE = re.compile(
    r"(?:^|[\s,{}])(?:body|html|main|section|header|footer|"
    r"\.(?:hero|section|footer|header|band|panel|sheet|wrap|page)[\w-]*)"
    r"[^{}]*\{[^{}]*\}", re.I | re.S)

HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")
VAR_DECL_RE = re.compile(r"(--[\w-]+)\s*:\s*(#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}))\b")
BG_VAR_RE = re.compile(r"background(?:-color|-image)?\s*:[^;{}]*?var\((--[\w-]+)\)", re.I)
BG_HEX_RE = re.compile(r"background(?:-color|-image)?\s*:[^;{}]*?(#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}))", re.I)


def to_hsl(hex_colour: str) -> tuple[float, float, float]:
    """(hue 0-360, saturation %, lightness %) from a #rgb or #rrggbb string."""
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    return hue * 360, sat * 100, light * 100


def sector_of(hue: float, sat: float, light: float = 50.0) -> str:
    """Hue sector, or 'neutro' when there is not enough colour to have one.

    Judged on chroma, like every other threshold here: a near-black at S=17%
    carries a nominal hue but no visible colour, and calling it 'blu' in the
    report told the reader something the eye cannot see.
    """
    if chroma(sat, light) <= NEUTRAL_C:
        return "neutro"
    for name, start, end in SECTORS:
        if start > end:            # the red sector wraps around 0°
            if hue >= start or hue < end:
                return name
        elif start <= hue < end:
            return name
    return "neutro"


def ink_family(hue: float, sat: float, light: float) -> str:
    """Which `ink_family` a dark belongs to, per craft-rules."""
    if chroma(sat, light) <= NEUTRAL_C:
        return "neutro"
    if 15 <= hue < 60:
        return "caldo"
    if 180 <= hue < 260:
        return "freddo"
    return "virato-accento"


def large_area_tokens(text: str) -> set[str]:
    """Tokens actually painted on big surfaces, read from the CSS itself.

    Guessing from the token name missed exactly the case that started this:
    `--abete` fills the hero of a page whose palette then reads as green, but
    no name heuristic would ever flag it.
    """
    found: set[str] = set()
    for block in BIG_SELECTOR_RE.findall(text):
        found.update(BG_VAR_RE.findall(block))
    # A variable defined as another variable's background inherits the role.
    for name in list(found):
        for decl_name, decl_val in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", text):
            if f"var({name})" in decl_val:
                found.add(decl_name)
    return found


def parse_colours(text: str) -> list[tuple[str, str]]:
    """(token, hex) pairs. Custom-property declarations first, then bare hexes.

    Declarations carry the intent (`--ink`, `--paper`), which is what lets us
    tell a large surface from a one-off border, so they are preferred; loose
    hexes are kept only when nothing declared them.
    """
    pairs = [(name, hx) for name, hx in VAR_DECL_RE.findall(text)]
    if pairs:
        return pairs
    seen: list[tuple[str, str]] = []
    for hx in HEX_RE.findall(text):
        if hx.lower() not in {h.lower() for _, h in seen}:
            seen.append(("", hx))
    return seen


def is_large_area(token: str) -> bool:
    t = token.lower()
    return any(hint in t for hint in LARGE_AREA_HINTS)


def analyse(pairs: list[tuple[str, str]], painted: set[str] | None = None) -> dict:
    colours = []
    for token, hx in pairs:
        hue, sat, light = to_hsl(hx)
        # Measured use wins over the name; the name is the fallback for bare
        # hex input, where there is no CSS to read.
        big = token in painted if painted else is_large_area(token)
        colours.append({
            "token": token,
            "hex": hx,
            "hue": round(hue),
            "sat": round(sat),
            "light": round(light),
            "chroma": round(chroma(sat, light), 1),
            "sector": sector_of(hue, sat, light),
            "large_area": big,
            "dark": light <= DARK_L,
        })

    # The dominant sector comes from the colours that cover area, not from the
    # accent: an accent is a few pixels, a background is half the page.
    weighted = [c for c in colours if c["large_area"]] or colours
    tally: dict[str, float] = {}
    for c in weighted:
        # Weighted by chroma: a near-white paper carries a nominal hue but
        # almost no colour, and counting it like a full green let a tie flip
        # the dominant sector.
        if c["sector"] != "neutro":
            tally[c["sector"]] = round(tally.get(c["sector"], 0) + c["chroma"], 1)
    dominant = max(tally, key=lambda k: tally[k]) if tally else "neutro"

    darks = [c for c in colours if c["dark"]]
    structural = [c for c in darks if c["large_area"]] or darks
    ink = min(structural, key=lambda c: c["light"]) if structural else None

    return {
        "colours": colours,
        "sector_tally": tally,
        "dominant_sector": dominant,
        "ink": ink,
        "ink_family": ink_family(ink["hue"], ink["sat"], ink["light"]) if ink else None,
    }


def violations(report: dict, last_sectors: list[str]) -> list[str]:
    out = []
    # Every large dark surface is checked, not just the darkest one: the page
    # that started this had a compliant `--ink` and a green `--abete` in the hero.
    for c in report["colours"]:
        if c["dark"] and c["large_area"] and c["chroma"] > INK_MAX_C:
            out.append(
                f"scuro strutturale colorato: {c['token'] or c['hex']} {c['hex']} "
                f"croma {c['chroma']} (max {INK_MAX_C:.0f} su superfici grandi, settore {c['sector']}). "
                "Se è una scelta dichiarata, tienila su UNA sola superficie."
            )
    ink = report["ink"]
    if ink and ink["sector"] != "neutro" and ink["sector"] == report["dominant_sector"]:
        accents = [c for c in report["colours"]
                   if not c["large_area"] and c["sector"] != "neutro"]
        if not accents or all(a["sector"] == ink["sector"] for a in accents):
            out.append(
                f"tinta unica: scuro e accento stanno entrambi nel settore "
                f"{ink['sector']} — la pagina ha un colore solo in due luminosità."
            )
    recent = [s.strip().lower() for s in last_sectors if s.strip()]
    if recent and report["dominant_sector"] != "neutro":
        streak = 0
        for s in recent:
            if s == report["dominant_sector"]:
                streak += 1
            else:
                break
        if streak >= 2:
            out.append(
                f"settore ripetuto: '{report['dominant_sector']}' arriva dopo {streak} "
                "job consecutivi nello stesso settore (max 2). Il nome della famiglia "
                "cambia, l'occhio no — cambia settore."
            )
    return out


def render(report: dict, problems: list[str], path: str | None) -> str:
    lines = [f"# Palette guard — {path or 'input'}", ""]
    lines.append(f"settore dominante (per area): **{report['dominant_sector']}**")
    if report["sector_tally"]:
        tally = " · ".join(f"{k} ×{v}" for k, v in
                           sorted(report["sector_tally"].items(), key=lambda kv: -kv[1]))
        lines.append(f"settori presenti: {tally}")
    ink = report["ink"]
    if ink:
        lines.append(
            f"scuro strutturale: `{ink['token'] or '(hex nudo)'}` {ink['hex']} — "
            f"settore {ink['sector']}, croma {ink['chroma']}, L={ink['light']}% → "
            f"`ink_family: {report['ink_family']}`"
        )
    lines.append("")
    lines.append("| token | hex | settore | H | S | L | croma | area |")
    lines.append("|---|---|---|---:|---:|---:|---:|---|")
    for c in report["colours"]:
        lines.append(
            f"| `{c['token'] or '—'}` | {c['hex']} | {c['sector']} | {c['hue']} | "
            f"{c['sat']} | {c['light']} | {c['chroma']} | {'grande' if c['large_area'] else ''} |"
        )
    lines.append("")
    if problems:
        lines.append("## Violazioni")
        lines.extend(f"- {p}" for p in problems)
    else:
        lines.append("Nessuna violazione: scuro entro soglia, settore non ripetuto.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Hue sectors and structural darks of a palette")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--check", metavar="FILE", help="HTML/CSS file to measure")
    src.add_argument("--hex", metavar="LIST", help="comma-separated hex colours")
    ap.add_argument("--last", default="", help="recent dominant sectors, most recent first")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    args = ap.parse_args()

    if args.check:
        path = Path(args.check)
        if not path.is_file():
            raise SystemExit(f"file inesistente: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        pairs = parse_colours(text)
        painted = large_area_tokens(text)
        label = str(path)
    else:
        pairs = []
        for raw in args.hex.split(","):
            raw = raw.strip()
            if not raw:
                continue
            if not raw.startswith("#"):
                raw = "#" + raw
            if not HEX_RE.fullmatch(raw):
                raise SystemExit(f"hex non valido: {raw}")
            pairs.append(("", raw))
        painted = None
        label = None

    if not pairs:
        raise SystemExit("nessun colore trovato: il file non dichiara hex?")

    report = analyse(pairs, painted)
    problems = violations(report, args.last.split(","))

    if args.format == "json":
        print(json.dumps({**report, "violations": problems}, ensure_ascii=False, indent=1))
    else:
        print(render(report, problems, label))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
