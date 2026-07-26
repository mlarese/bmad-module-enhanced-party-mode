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

So this script answers three questions a name cannot:
  1. which hue sector does this palette actually sit in?
  2. is the structural dark a branded near-neutral, or a saturated colour
     covering half the page?
  3. is this the third job in a row in the same sector?

**What changed, and why (adversarial review 2026-07-26).** The first version
moved the guesswork from the token name to the SELECTOR name: only classes
starting with hero/section/footer/… counted as a large surface. Measured on
three pages carrying `#1A2A22` — the very green named in this docstring — it
reported "nessuna violazione" and exit 0 for all three:

  .s-hero { background: var(--abete) }        → class outside the dictionary
  .hero   { background: #1A2A22 }             → inline hex, never parsed
  [data-theme="dark"] { background: … }       → the pattern craft-rules PRESCRIBE

Worse, on a page with no custom properties (Tailwind, CSS-in-JS) the dominant
sector was decided by a 12px SVG icon, and that false value went into MEMORY as
`last_hue_sectors`, poisoning the anti-repetition of every later job.

So the rule is inverted now: **a background is a large surface unless the
selector names a small component** (button, badge, chip, icon…). Guessing which
selectors are big fails open; guessing which are small fails closed. And when
nothing can be measured honestly the script says so and exits 2 — it never
prints a dominant sector it had to invent.

Usage:
    uv run scripts/palette_guard.py --check apps/<slug>/index.html
    uv run scripts/palette_guard.py --hex '#141C18,#C96F3A,#F3F0EA'
    uv run scripts/palette_guard.py --check pagina.html --last verde,teal
    uv run scripts/palette_guard.py --check pagina.html --ledger _bmad/memory/agent-frontend-taste/hue-ledger.json
    uv run scripts/palette_guard.py --check pagina.html --format json

Exit: 0 pulito · 1 violazioni · 2 non misurabile (non dichiarare "guard pulito").
"""

from __future__ import annotations

import argparse
import colorsys
import json
import re
import sys
from datetime import datetime
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

# The one list that decides area, and it lists the SMALL things. A background
# painted by anything else is a surface until proven otherwise: an unknown
# class name is far more likely to be `.s-hero` than a chip. Matched as a word
# inside the selector, so `.btn`, `.hero-btn` and `#submit-button` all land here.
SMALL_COMPONENT_RE = re.compile(
    r"(?:^|[^a-z0-9])(?:btn|button|badge|chip|tag|pill|icon|avatar|dot|bullet|"
    r"marker|cursor|scroll|scrollbar|thumb|tooltip|popover|caret|arrow|close|"
    r"swatch|spinner|loader|toggle|switch|checkbox|radio|input|select|textarea|"
    r"field|dropdown|option|star|rating|divider|separator|rule|line)"
    r"(?:[^a-z0-9]|$)", re.I)

# Any rule block: `selector { body }`. Nested at-rules resolve naturally —
# `@media(...){ .hero{…} }` matches the inner block, because a selector cannot
# contain a brace.
BLOCK_RE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)

# Six digits are tried BEFORE three, always: with the lazy quantifier in
# BG_HEX_RE the short branch won and `#1A2A22` was parsed as `#1A2` — a green
# read as a different green, reported with two decimals of false precision.
_HEX = r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b"
HEX_RE = re.compile(_HEX)
VAR_DECL_RE = re.compile(rf"(--[\w-]+)\s*:\s*({_HEX})")
BG_PROP_RE = re.compile(r"background(?:-color|-image)?\s*:", re.I)
BG_VAR_RE = re.compile(r"background(?:-color|-image)?\s*:[^;{}]*?var\((--[\w-]+)\)", re.I)
BG_HEX_RE = re.compile(rf"background(?:-color|-image)?\s*:[^;{{}}]*?({_HEX})", re.I)
FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;{}]+)", re.I)

# Utility-class stacks (Tailwind & co.) carry the palette in a theme map and
# the usage in `bg-*` classes. Without this the whole file is unmeasurable —
# and the previous version silently reported the SVG icon's hue instead.
THEME_MAP_RE = re.compile(rf"['\"]?([A-Za-z][\w-]*)['\"]?\s*:\s*['\"]({_HEX})['\"]")
UTILITY_BG_RE = re.compile(r"\bbg-([a-z][\w-]*)\b")
UTILITY_ARBITRARY_BG_RE = re.compile(rf"\bbg-\[({_HEX})\]")
UTILITY_ANY_RE = re.compile(r"\b(?:bg|text|border|from|to|via)-[a-z][\w-]*\b")

# Hard-rejects from craft-rules § Palette + fonts, point 7. They are the most
# mechanical rules in the whole skill and nothing was checking them.
# `sans-serif` is not a serif: matching it let Inter,system-ui,sans-serif pass
# the display check, which is precisely the hard-reject being looked for.
SERIF_HINT_RE = re.compile(
    r"(?<!sans-)\bserif\b|playfair|cormorant|lora|garamond|bodoni|didot|fraunces|"
    r"libre baskerville|crimson|spectral|tiempos", re.I)
SYSTEM_FONT_RE = re.compile(r"\bInter\b|system-ui|-apple-system|BlinkMacSystemFont|"
                            r"\bSegoe UI\b|\bRoboto\b|\bHelvetica Neue\b", re.I)
HEADING_SELECTOR_RE = re.compile(
    r"(?:^|[^a-z0-9])(?:h1|h2|display|title|titolo|headline|heading|hero)"
    r"(?:[^a-z0-9]|$)", re.I)
CREAM_REF = (0xF4, 0xF1, 0xEA)


def to_hsl(hex_colour: str) -> tuple[float, float, float]:
    """(hue 0-360, saturation %, lightness %) from a #rgb or #rrggbb string."""
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    return hue * 360, sat * 100, light * 100


def to_rgb(hex_colour: str) -> tuple[int, int, int]:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


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


def is_small_component(selector: str) -> bool:
    """Whether a selector names a small component rather than a surface."""
    return bool(SMALL_COMPONENT_RE.search(selector))


def css_blocks(text: str) -> list[tuple[str, str]]:
    """(selector, body) for every rule block that paints a background."""
    out = []
    for sel, body in BLOCK_RE.findall(text):
        if BG_PROP_RE.search(body):
            out.append((" ".join(sel.split()), body))
    return out


def surface_usage(text: str) -> tuple[set[str], set[str], list[tuple[str, str]]]:
    """What paints a surface, read from the file itself.

    Returns (large_tokens, small_tokens, inline_pairs) where inline_pairs are
    ("(inline)"-style label, hex) for backgrounds written as a bare hex — the
    case `BG_HEX_RE` was compiled for and never used, which made a hero painted
    `background:#1A2A22` disappear from the analysis entirely.
    """
    large: set[str] = set()
    small: set[str] = set()
    inline: list[tuple[str, str]] = []

    for selector, body in css_blocks(text):
        minor = is_small_component(selector)
        for token in BG_VAR_RE.findall(body):
            (small if minor else large).add(token)
        for hx in BG_HEX_RE.findall(body):
            label = f"{selector.split(',')[0].strip()[:24]} (hex)"
            inline.append((label if not minor else f"{label} ·piccolo", hx))

    # Utility-class stacks: the palette lives in a theme map, the usage in
    # `bg-*`. Both are read, or a Tailwind page is measured on its SVG icons.
    theme = {name: hx for name, hx in THEME_MAP_RE.findall(text)}
    used = set(UTILITY_BG_RE.findall(text))
    for name in sorted(used):
        if name in theme:
            inline.append((f"bg-{name}", theme[name]))
    for hx in sorted(set(UTILITY_ARBITRARY_BG_RE.findall(text))):
        inline.append((f"bg-[{hx}]", hx))

    # A variable defined as another variable's background inherits the role.
    for name in list(large):
        for decl_name, decl_val in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", text):
            if f"var({name})" in decl_val:
                large.add(decl_name)
    return large, small, inline


def large_area_tokens(text: str) -> set[str]:
    """Back-compat wrapper: the tokens painted on large surfaces."""
    return surface_usage(text)[0]


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


def measured_pairs(text: str) -> tuple[list[tuple[str, str]], set[str], set[str], bool]:
    """Colours to judge, plus the roles read from usage.

    When the file declares custom properties we measure those (they are the
    palette). When it does not — utility classes, CSS-in-JS — we measure only
    what is actually painted, never every hex in the document: an icon fill is
    not a palette, and treating it as one is how `dominant_sector: blu` came
    out of a page whose hero was green.
    """
    large, small, inline = surface_usage(text)
    declared = [(name, hx) for name, hx in VAR_DECL_RE.findall(text)]
    owner_of = {}
    for name, hx in declared:
        owner_of.setdefault(hx.lower(), name)

    pairs: list[tuple[str, str]] = list(declared)
    seen = {(n, h.lower()) for n, h in declared}
    for label, hx in inline:
        minor = "·piccolo" in label
        owner = owner_of.get(hx.lower())
        if owner:
            # Same colour, already a token: promote the token's role instead of
            # adding a second row for it. `large` always wins over `small`.
            if minor:
                if owner not in large:
                    small.add(owner)
            else:
                large.add(owner)
                small.discard(owner)
            continue
        if (label, hx.lower()) in seen:
            continue
        seen.add((label, hx.lower()))
        pairs.append((label, hx))
        (small if minor else large).add(label)
    return pairs, large, small, bool(pairs)


def analyse(pairs: list[tuple[str, str]], painted: set[str] | None = None,
            small: set[str] | None = None) -> dict:
    colours = []
    for token, hx in pairs:
        hue, sat, light = to_hsl(hx)
        # Measured use wins over the name; the name is the fallback for bare
        # hex input, where there is no CSS to read. A partial match must NOT
        # disable the fallback — that is what let `--abete` slip through as a
        # non-surface just because `body` happened to be recognised.
        if painted and token in painted:
            big = True
        elif small and token in small:
            big = False
        else:
            big = is_large_area(token)
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


def is_large_area(token: str) -> bool:
    t = token.lower()
    return any(hint in t for hint in LARGE_AREA_HINTS)


def palette_colours(text: str, measured: list[dict]) -> list[dict]:
    """Every colour the page DECLARES as its palette, measured or not.

    The hard-rejects are about the palette, not about what covers area: a
    purple-indigo accent is a hard-reject even if it only ever paints a button.
    Tokens and theme maps count; a `fill` inside a third-party SVG does not.
    """
    out = list(measured)
    known = {c["hex"].lower() for c in measured}
    declared = [(n, h) for n, h in VAR_DECL_RE.findall(text)]
    declared += [(f"theme.{n}", h) for n, h in THEME_MAP_RE.findall(text)]
    for name, hx in declared:
        if hx.lower() in known:
            continue
        known.add(hx.lower())
        hue, sat, light = to_hsl(hx)
        out.append({
            "token": name, "hex": hx, "hue": round(hue), "sat": round(sat),
            "light": round(light), "chroma": round(chroma(sat, light), 1),
            "sector": sector_of(hue, sat, light), "large_area": False,
            "dark": light <= DARK_L,
        })
    return out


def hard_rejects(text: str, colours: list[dict]) -> list[str]:
    """The three named hard-rejects of craft-rules § Palette + fonts, point 7.

    Mechanical rules that were left entirely to the model's judgement while the
    script measured chroma to one decimal place.
    """
    out: list[str] = []

    ai_purple = [c for c in colours
                 if 235 <= c["hue"] <= 295 and c["sat"] >= 45 and 30 <= c["light"] <= 80]
    if ai_purple:
        names = ", ".join(f"{c['token'] or c['hex']} {c['hex']}" for c in ai_purple[:3])
        out.append(
            f"hard-reject purple-indigo AI: {names} — è il viola di default di ogni "
            "pagina generata; craft-rules lo vieta esplicitamente."
        )

    families = FONT_FAMILY_RE.findall(text)
    has_serif = any(SERIF_HINT_RE.search(f) for f in families)
    cream = [c for c in colours
             if all(abs(a - b) <= 8 for a, b in zip(to_rgb(c["hex"]), CREAM_REF))]
    terracotta = [c for c in colours
                  if 12 <= c["hue"] <= 38 and 30 <= c["sat"] <= 75 and 35 <= c["light"] <= 70]
    if cream and terracotta and has_serif:
        out.append(
            f"hard-reject cream+serif+terracotta: {cream[0]['hex']} con "
            f"{terracotta[0]['hex']} e un serif — è la landing «artigianale» "
            "che esce identica a sé stessa da anni."
        )

    for selector, body in BLOCK_RE.findall(text):
        if not HEADING_SELECTOR_RE.search(selector):
            continue
        for fam in FONT_FAMILY_RE.findall(body):
            if SYSTEM_FONT_RE.search(fam) and not SERIF_HINT_RE.search(fam):
                out.append(
                    f"hard-reject Inter/system come display: `{' '.join(selector.split())[:40]}` "
                    f"→ {fam.strip()[:60]}. Il display è una voce, non il font di sistema."
                )
                break
        if out and out[-1].startswith("hard-reject Inter"):
            break
    return out


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


# --- ledger -----------------------------------------------------------------
# `--last` has to be typed by hand from MEMORY, in an order nobody declared
# (the check assumes most-recent-first; MEMORY-template never said so), and it
# only ever covers jobs done in the same project — while the sanctum is
# per-project and an agency does one job per repo. A ledger makes the streak a
# recorded fact instead of something to remember correctly.

def ledger_load(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def ledger_sectors(entries: list[dict]) -> list[str]:
    """Dominant sectors, most recent first — the order `--last` expects."""
    return [e.get("dominant_sector", "") for e in reversed(entries)]


def ledger_record(path: Path, entries: list[dict], key: str, report: dict) -> None:
    """One record per file: a corrected page replaces its own earlier reading."""
    entries = [e for e in entries if e.get("key") != key]
    entries.append({
        "key": key,
        "when": datetime.now().isoformat(timespec="minutes"),
        "dominant_sector": report["dominant_sector"],
        "ink_family": report["ink_family"],
        "ink_hex": (report["ink"] or {}).get("hex"),
    })
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries[-50:], ensure_ascii=False, indent=1),
                    encoding="utf-8")


def render(report: dict, problems: list[str], path: str | None,
           rejects: list[str] | None = None) -> str:
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
    if rejects:
        lines.append("## Hard-reject (craft-rules § Palette + fonts)")
        lines.extend(f"- {r}" for r in rejects)
        lines.append("")
    if problems:
        lines.append("## Violazioni")
        lines.extend(f"- {p}" for p in problems)
    else:
        lines.append("Nessuna violazione: scuro entro soglia, settore non ripetuto.")
    return "\n".join(lines)


def unmeasurable_note(text: str) -> str:
    if UTILITY_ANY_RE.search(text):
        return (
            "NON MISURABILE: la pagina usa utility class (`bg-…`) ma nessuna mappa di "
            "tema con hex è leggibile da qui. Misura il file che dichiara i colori "
            "(tailwind.config, tokens.css, theme.ts) oppure passa la palette con "
            "`--hex`. **Non dichiarare «palette_guard pulito»**: qui non è stato "
            "misurato niente."
        )
    return (
        "NON MISURABILE: nessun background con colore leggibile in questo file "
        "(nessuna custom property dipinta, nessun hex su `background`). Misura il "
        "foglio di stile vero o passa la palette con `--hex`. **Non dichiarare "
        "«palette_guard pulito»**."
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Hue sectors and structural darks of a palette")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--check", metavar="FILE", help="HTML/CSS file to measure")
    src.add_argument("--hex", metavar="LIST", help="comma-separated hex colours")
    ap.add_argument("--last", default="", help="recent dominant sectors, most recent first")
    ap.add_argument("--ledger", metavar="FILE",
                    help="JSON ledger of past measurements: reads the streak and records this one")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    args = ap.parse_args()

    small: set[str] | None = None
    if args.check:
        path = Path(args.check)
        if not path.is_file():
            raise SystemExit(f"file inesistente: {path}")
        text = path.read_text(encoding="utf-8", errors="replace")
        pairs, painted, small, ok = measured_pairs(text)
        if not ok or not pairs:
            print(unmeasurable_note(text), file=sys.stderr)
            return 2
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
        text = ""
        label = None

    if not pairs:
        raise SystemExit("nessun colore trovato: il file non dichiara hex?")

    report = analyse(pairs, painted, small)
    rejects = hard_rejects(text, palette_colours(text, report["colours"])) if text else []

    last = [s for s in args.last.split(",")]
    ledger_path = Path(args.ledger) if args.ledger else None
    entries: list[dict] = []
    if ledger_path:
        entries = ledger_load(ledger_path)
        if not any(s.strip() for s in last):
            last = ledger_sectors(entries)

    problems = violations(report, last) + rejects

    if ledger_path and args.check:
        ledger_record(ledger_path, entries, str(Path(args.check).resolve()), report)

    if args.format == "json":
        print(json.dumps({**report, "violations": problems, "hard_rejects": rejects},
                         ensure_ascii=False, indent=1))
    else:
        print(render(report, violations(report, last), label, rejects))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
