#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Effects catalogue — visual chooser page + text lookup from assets/effects-catalog.json.

The sibling of hero_gallery.py in agent-frontend-taste: same idea, other axis.
Where that one asks "which hero", this one asks "which movement" — and it answers by
*moving*. Every tile runs its animation on a little stage (a block, a line of text, a
card, a cursor, an SVG path...), so the owner picks by watching instead of by reading
a table. Numbering follows `references/catalog.md` (1-117).

Local only: no network, no webfonts, no libraries. Effects that genuinely need one
(WebGL, canvas, Lottie, Rive) are rendered as a declared approximation and say so on
the card — a catalogue that fakes its samples is worse than a table.

Usage:
    uv run scripts/effects_gallery.py                          # markdown list
    uv run scripts/effects_gallery.py --filter cat=scroll      # filtered list
    uv run scripts/effects_gallery.py --filter cost=free
    uv run scripts/effects_gallery.py --show scrub
    uv run scripts/effects_gallery.py --kit vetrina
    uv run scripts/effects_gallery.py --suggest 4 --seed 2026072522 --last parallax-bg
    uv run scripts/effects_gallery.py --build                  # write assets/effects-gallery.html
    uv run scripts/effects_gallery.py --check                  # page in sync with catalogue?
    uv run scripts/effects_gallery.py --format json
"""

from __future__ import annotations

import argparse
import html
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CATALOG = ASSETS / "effects-catalog.json"
PAGE = ASSETS / "effects-gallery.html"

FIELDS = ("n", "id", "name", "cat", "tech", "cost", "stage", "fx", "desc", "use", "watch")

STAGES = {
    "block", "blocks", "line", "words", "chars", "photo", "btn", "link", "card",
    "nav", "list", "path", "dots", "bar", "panel", "cursor", "num", "blob",
    "scene", "page", "scrollbox",
}

# Stages whose markup carries several subjects — used by the stagger-style effects.
MULTI = {"blocks", "words", "chars", "dots", "list", "nav"}


# ------------------------------------------------------------------ catalog


def load(path: Path = CATALOG) -> dict:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    validate(catalog)
    return catalog


def validate(catalog: dict) -> None:
    """Fail loud on a catalogue the page could only render wrong."""
    axes = catalog["axes"]
    seen_id: set[str] = set()
    seen_n: set[int] = set()
    for e in catalog["effects"]:
        where = e.get("id", "<senza id>")
        missing = [f for f in FIELDS if e.get(f) in (None, "", [])]
        if missing:
            raise SystemExit(f"{where}: campi mancanti {missing}")
        if e["id"] in seen_id:
            raise SystemExit(f"id duplicato: {e['id']}")
        if e["n"] in seen_n:
            raise SystemExit(f"numero duplicato: {e['n']}")
        seen_id.add(e["id"])
        seen_n.add(e["n"])
        if e["cat"] not in axes["cat"]:
            raise SystemExit(f"{where}: categoria '{e['cat']}' non è negli assi")
        if e["cost"] not in axes["cost"]:
            raise SystemExit(f"{where}: costo '{e['cost']}' non è negli assi")
        for t in e["tech"]:
            if t not in axes["tech"]:
                raise SystemExit(f"{where}: tecnica '{t}' non è negli assi")
        if e["stage"] not in STAGES:
            raise SystemExit(f"{where}: stage '{e['stage']}' sconosciuto")
        if not isinstance(e["approx"], bool):
            raise SystemExit(f"{where}: 'approx' deve essere booleano")
    known = {e["n"] for e in catalog["effects"]}
    for kit in catalog["kits"]:
        missing = [n for n in kit["effects"] if n not in known]
        if missing:
            raise SystemExit(f"kit '{kit['id']}': effetti inesistenti {missing}")


def by_n(catalog: dict) -> dict[int, dict]:
    return {e["n"]: e for e in catalog["effects"]}


def match_filters(entry: dict, filters: list[tuple[str, str]]) -> bool:
    for key, value in filters:
        got = entry.get(key, "")
        if isinstance(got, list):
            if value not in got:
                return False
        elif str(got) != value:
            return False
    return True


def parse_filters(raw: list[str], catalog: dict | None = None) -> list[tuple[str, str]]:
    """Parse `key=value` filters, refusing keys and values the catalog does not have.

    Without the check a typo reads exactly like an honest empty result: both
    `--filter ct=scroll` and `--filter cat=nonesiste` printed zero rows in
    silence, so you conclude "no effect matches" instead of "you typed it wrong".
    """
    out: list[tuple[str, str]] = []
    fields: dict[str, set[str]] = {}
    if catalog:
        for e in catalog["effects"]:
            for k, v in e.items():
                if isinstance(v, str):
                    fields.setdefault(k, set()).add(v)
                elif isinstance(v, list) and all(isinstance(x, str) for x in v):
                    fields.setdefault(k, set()).update(v)
        fields = {k: v for k, v in fields.items() if len(v) <= 20}

    for item in raw:
        if "=" not in item:
            raise SystemExit(f"filtro non valido: {item} (usa chiave=valore, es. cat=scroll)")
        key, _, value = item.partition("=")
        key, value = key.strip(), value.strip()
        if fields:
            if key not in fields:
                raise SystemExit(
                    f"filtro: chiave sconosciuta `{key}`. Disponibili: {', '.join(sorted(fields))}"
                )
            if value not in fields[key]:
                raise SystemExit(
                    f"filtro: `{key}` non ha il valore `{value}`. "
                    f"Valori reali: {', '.join(sorted(fields[key]))}"
                )
        out.append((key, value))
    return out


def suggest(effects: list[dict], n: int, seed: str, last: list[str]) -> list[dict]:
    """Deterministic shortlist per seed: diverse on family, MEMORY-aware, cheap first.

    Mirrors hero_gallery.suggest so the two skills feel like one hand.
    """
    dropped = {v.strip() for v in last if v.strip()}
    pool = [e for e in effects if not dropped & {e["id"], e["cat"], str(e["n"])}]
    if not pool:
        pool = list(effects)
    rng = random.Random(f"{seed}|effects-gallery")
    rng.shuffle(pool)
    picked: list[dict] = []
    seen_cat: set[str] = set()
    # First pass: one per family and nothing heavy — the sane default kit.
    for strict in (True, False):
        for e in pool:
            if len(picked) >= n:
                break
            if e in picked:
                continue
            if strict and (e["cat"] in seen_cat or e["cost"] == "heavy"):
                continue
            picked.append(e)
            seen_cat.add(e["cat"])
    return picked[:n]


# ------------------------------------------------------------------ text out


def render_list(catalog: dict, entries: list[dict]) -> str:
    axes = catalog["axes"]
    lines = [
        "# Effetti",
        "",
        f"Catalogo: `assets/effects-catalog.json` · pagina: `assets/effects-gallery.html` "
        f"({len(catalog['effects'])} effetti, {len(entries)} elencati)",
        "",
        "| # | id | Nome | Famiglia | Tecnica | Costo |",
        "|---|---|---|---|---|---|",
    ]
    for e in entries:
        lines.append(
            f"| {e['n']} | `{e['id']}` | {e['name']}{' *' if e['approx'] else ''} | "
            f"{axes['cat'][e['cat']]['label']} | {' · '.join(e['tech'])} | "
            f"{axes['cost'][e['cost']]['label']} |"
        )
    lines += [
        "",
        "`*` = nella pagina la miniatura è un'approssimazione dichiarata (serve una libreria vera).",
        "",
        "Guardali muovere: `open assets/effects-gallery.html` (o il path stampato da `--build`).",
    ]
    return "\n".join(lines)


def render_show(catalog: dict, entry: dict) -> str:
    axes = catalog["axes"]
    techs = "\n".join(f"  - `{t}` — {axes['tech'][t]['note']}" for t in entry["tech"])
    kits = [k["label"] for k in catalog["kits"] if entry["n"] in k["effects"]]
    return "\n".join(
        [
            f"# {entry['n']}. {entry['name']}  (`{entry['id']}`)",
            "",
            entry["desc"],
            "",
            f"- **Famiglia:** {axes['cat'][entry['cat']]['label']} (`{entry['cat']}`)",
            "- **Tecnica:**",
            techs,
            f"- **Costo:** {axes['cost'][entry['cost']]['label']} — {axes['cost'][entry['cost']]['note']}",
            f"- **Quando:** {entry['use']}",
            f"- **Attenzione:** {entry['watch']}",
            f"- **Nei kit:** {', '.join(kits) if kits else '—'}",
            "",
            (
                "> La miniatura in pagina è un'approssimazione: l'effetto vero richiede la "
                "libreria indicata sopra."
                if entry["approx"]
                else "La miniatura in pagina esegue l'effetto per davvero, in CSS."
            ),
        ]
    )


def render_kit(catalog: dict, kit: dict) -> str:
    index = by_n(catalog)
    lines = [f"# Kit — {kit['label']}", "", kit["note"], ""]
    for n in kit["effects"]:
        e = index[n]
        lines.append(f"- **{n}. {e['name']}** (`{e['id']}`) — {e['desc']}")
    return "\n".join(lines)


# ------------------------------------------------------------------ stages


def _stage_html(stage: str, uid: str = "x") -> str:
    """The little mock each effect animates. `.subj` marks what moves.

    `uid` keeps SVG ids unique: 117 cards share this markup on one page.
    """
    if stage == "block":
        return '<i class="subj s-block"></i>'
    if stage == "blocks":
        return '<span class="s-grid">' + "".join('<i class="subj"></i>' for _ in range(6)) + "</span>"
    if stage == "line":
        return '<span class="s-line"><i class="subj">Movimento giusto</i></span>'
    if stage == "words":
        return '<span class="s-line s-words">' + "".join(
            f'<i class="subj">{w}</i>' for w in ("Movimento", "che", "significa")
        ) + "</span>"
    if stage == "chars":
        return '<span class="s-line s-chars">' + "".join(
            f'<i class="subj">{c}</i>' for c in "MOVIMENTO"
        ) + "</span>"
    if stage == "photo":
        return '<span class="s-photo"><i class="subj"></i></span>'
    if stage == "btn":
        return '<span class="s-btn subj"><em>Prenota ora</em></span>'
    if stage == "link":
        return '<span class="s-link subj">Scopri il progetto</span>'
    if stage == "card":
        return (
            '<span class="s-card subj"><i class="s-card__ph"></i>'
            '<b>Rifugio 2.140</b><em>Quattro camere, cucina di montagna.</em>'
            '<u>Prenota</u></span>'
        )
    if stage == "nav":
        return (
            '<span class="s-nav"><b>Logo</b>'
            + "".join(f'<i class="subj">{v}</i>' for v in ("Stanze", "Cucina", "Contatti"))
            + '<u class="s-nav__ind"></u></span>'
        )
    if stage == "list":
        return '<span class="s-list">' + "".join('<i class="subj"></i>' for _ in range(3)) + "</span>"
    if stage == "path":
        ring = f"ring-{uid}"
        return (
            '<span class="s-path"><svg viewBox="0 0 100 100" aria-hidden="true">'
            f'<defs><path id="{ring}" d="M 12,50 A 38,38 0 1 1 88,50 A 38,38 0 1 1 12,50"/></defs>'
            '<circle class="subj" cx="50" cy="50" r="34" pathLength="100"/>'
            '<path class="subj subj--tick" d="M34 51 L46 63 L68 39" pathLength="100"/>'
            f'<text class="s-path__ring"><textPath href="#{ring}" startOffset="0%">'
            "SCORRI PER SCOPRIRE ·</textPath></text>"
            "</svg></span>"
        )
    if stage == "dots":
        return '<span class="s-dots">' + "".join('<i class="subj"></i>' for _ in range(14)) + "</span>"
    if stage == "bar":
        return '<span class="s-bar"><i class="subj"></i></span>'
    if stage == "panel":
        return '<span class="s-panel subj"><b></b><em></em></span>'
    if stage == "cursor":
        return '<span class="s-cursor"><b>Portfolio</b><i class="subj"></i></span>'
    if stage == "num":
        return '<span class="s-num"><i class="subj">128</i></span>'
    if stage == "blob":
        return '<span class="s-blob"><i class="subj"></i></span>'
    if stage == "scene":
        return (
            '<span class="s-scene"><i class="subj">'
            + "".join(f'<b class="f{k}"></b>' for k in range(1, 5))
            + "</i></span>"
        )
    if stage == "page":
        return '<span class="s-page"><i class="subj p-a"></i><i class="subj p-b"></i></span>'
    if stage == "scrollbox":
        return (
            '<span class="s-scrollbox"><i class="subj">'
            + "".join("<b></b>" for _ in range(4))
            + "</i></span>"
        )
    raise SystemExit(f"stage sconosciuto: {stage}")


def render_card(entry: dict, catalog: dict) -> str:
    e = html.escape
    axes = catalog["axes"]
    techs = "".join(f"<li><code>{e(t)}</code></li>" for t in entry["tech"])
    haystack = " ".join(
        [
            str(entry["n"]), entry["id"], entry["name"], entry["desc"], entry["use"],
            entry["watch"], axes["cat"][entry["cat"]]["label"], " ".join(entry["tech"]),
            axes["cost"][entry["cost"]]["label"],
        ]
    ).lower()
    approx = (
        '<span class="flag" title="L\'effetto vero richiede una libreria: qui è una resa '
        'approssimata, dichiarata.">resa approssimata</span>'
        if entry["approx"]
        else ""
    )
    return f"""      <article class="card" tabindex="0" role="button" aria-pressed="false"
        data-id="{e(entry['id'])}" data-n="{entry['n']}" data-cat="{e(entry['cat'])}"
        data-cost="{e(entry['cost'])}" data-tech="{e(' '.join(entry['tech']))}"
        data-search="{e(haystack)}">
        <span class="stage fx--{e(entry['fx'])}" aria-hidden="true">{_stage_html(entry['stage'], entry['id'])}</span>
        <div class="body">
          <p class="eyebrow"><b>{entry['n']}</b> <code>{e(entry['id'])}</code></p>
          <h3>{e(entry['name'])}{approx}</h3>
        </div>
      </article>
"""


def _chip_group(name: str, label: str, values: dict[str, dict], used: set[str]) -> str:
    chips = "".join(
        f'<button type="button" class="chip" data-group="{name}" data-value="{html.escape(k)}" '
        f'title="{html.escape(v["note"])}" aria-pressed="false">{html.escape(v["label"])}</button>'
        for k, v in values.items()
        if k in used
    )
    return (
        f'<div class="chips" role="group" aria-label="{label}">'
        f'<span class="chips__label">{label}</span>{chips}</div>'
    )


def _kits_html(catalog: dict) -> str:
    index = by_n(catalog)
    blocks = []
    for kit in catalog["kits"]:
        items = " · ".join(
            f'<code>{html.escape(index[n]["id"])}</code>' for n in kit["effects"]
        )
        nums = ",".join(str(n) for n in kit["effects"])
        blocks.append(
            f'<div class="kit"><h3>{html.escape(kit["label"])}</h3>'
            f'<p>{html.escape(kit["note"])}</p><p class="kit__ids">{items}</p>'
            f'<button type="button" class="btn" data-kit="{nums}">Seleziona questo kit</button></div>'
        )
    return (
        '<section class="kits"><h2>Kit di partenza</h2>'
        "<p class=\"lede\">Combinazioni che reggono insieme. Sono un punto di partenza da "
        "tagliare, non una lista da applicare tutta.</p>"
        f'<div class="kits__cols">{"".join(blocks)}</div></section>'
    )


def _legend(catalog: dict) -> str:
    axes = catalog["axes"]
    blocks = []
    for name, title in (("cat", "Famiglie"), ("tech", "Tecniche"), ("cost", "Costo")):
        items = "".join(
            f"<dt><code>{html.escape(k)}</code> {html.escape(v['label'])}</dt>"
            f"<dd>{html.escape(v['note'])}</dd>"
            for k, v in axes[name].items()
        )
        blocks.append(f"<div><h3>{title}</h3><dl>{items}</dl></div>")
    return (
        '<section class="legend"><h2>Come è organizzato</h2>'
        f'<div class="legend__cols">{"".join(blocks)}</div></section>'
    )


def render_html(catalog: dict) -> str:
    axes = catalog["axes"]
    effects = catalog["effects"]
    cards = "".join(render_card(e, catalog) for e in effects)
    used_tech = {t for e in effects for t in e["tech"]}
    filters = _chip_group("cat", "Famiglia", axes["cat"], {e["cat"] for e in effects})
    return f"""<!DOCTYPE html>
<html lang="it" data-generated-by="effects_gallery.py">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Effetti — scelta a vista</title>
<style>
{_css()}
</style>
</head>
<body>
<header class="masthead">
  <h1>Movimento — {len(effects)} esempi</h1>
</header>

<div class="toolbar">
  {filters}
  <label class="search"><span class="sr">Cerca</span>
    <input type="search" id="q" placeholder="Cerca"></label>
  <button type="button" class="btn" id="motion">Metti in pausa</button>
  <button type="button" class="btn" id="reset">Azzera</button>
  <span class="count" id="count"></span>
</div>

<main>
  <div class="grid" id="grid">
{cards}  </div>
  <p class="empty" id="empty" hidden>Nessun effetto con questi filtri.</p>
  <footer class="credits"><p>Miniature in CSS puro. In produzione ogni effetto va sotto
  <code>prefers-reduced-motion</code>.</p></footer>
</main>

<div class="tray" id="tray" hidden>
  <p id="picked"></p>
  <button type="button" class="btn" id="copy">Copia</button>
  <button type="button" class="btn" id="clear">Svuota</button>
</div>

<script>
{_js()}
</script>
</body>
</html>
"""


# ------------------------------------------------------------------ assets


def _css() -> str:
    return (_css_shell() + _css_stages() + _css_effects()).strip()


def _css_shell() -> str:
    return """
:root {
  --paper: #f4f1ec;
  --paper-2: #e8e3da;
  --ink: #16151a;
  --ink-2: #4c4954;
  --rule: #c8c2b8;
  --accent: #2f5d50;
  --hot: #b1442a;
  --r: 3px;
  --mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--paper); color: var(--ink);
  font-family: var(--sans); line-height: 1.5;
}
code { font-family: var(--mono); font-size: .82em; }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }

header.masthead { padding: clamp(1.5rem, 4vw, 3.5rem) clamp(1rem, 4vw, 3rem) 1.25rem; border-bottom: 1px solid var(--rule); }
.kicker { font-family: var(--mono); font-size: .7rem; letter-spacing: .16em; text-transform: uppercase; color: var(--ink-2); margin: 0 0 .75rem; }
h1 { font-family: var(--serif); font-weight: 500; font-size: clamp(2rem, 5.5vw, 3.4rem); line-height: .95; letter-spacing: -.035em; margin: 0 0 .6rem; max-width: 22ch; text-wrap: balance; }
.lede { margin: 0; max-width: 68ch; color: var(--ink-2); text-wrap: pretty; }
.lede + .lede { margin-top: .5rem; }

.toolbar { position: sticky; top: 0; z-index: 5; background: color-mix(in srgb, var(--paper) 92%, transparent); backdrop-filter: blur(6px); border-bottom: 1px solid var(--rule); padding: .75rem clamp(1rem, 4vw, 3rem); display: flex; flex-wrap: wrap; gap: .75rem 1.5rem; align-items: center; }
.chips { display: flex; flex-wrap: wrap; gap: .3rem; align-items: center; }
.chips__label { font-family: var(--mono); font-size: .66rem; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-2); margin-right: .3rem; }
.chip, .btn { font: inherit; font-size: .8rem; padding: .3rem .6rem; border: 1px solid var(--rule); border-radius: var(--r); background: transparent; color: var(--ink-2); cursor: pointer; min-height: 34px; }
.chip[aria-pressed="true"] { background: var(--ink); border-color: var(--ink); color: var(--paper); }
.chip:focus-visible, .btn:focus-visible, .card:focus-visible, input:focus-visible { outline: 2px solid var(--hot); outline-offset: 2px; }
.search { flex: 1 1 12rem; min-width: 9rem; }
.search input { width: 100%; font: inherit; font-size: .85rem; padding: .4rem .6rem; border: 1px solid var(--rule); border-radius: var(--r); background: var(--paper); color: var(--ink); min-height: 34px; }
.count { font-family: var(--mono); font-size: .72rem; color: var(--ink-2); white-space: nowrap; }

main { padding: 1.5rem clamp(1rem, 4vw, 3rem) 6rem; }
.grid { display: grid; gap: 1px; grid-template-columns: repeat(auto-fill, minmax(min(100%, 11.5rem), 1fr)); background: var(--rule); border: 1px solid var(--rule); }
.card { background: var(--paper); padding: .6rem; display: flex; flex-direction: column; gap: .45rem; cursor: pointer; }
.card[aria-pressed="true"] { background: var(--paper-2); box-shadow: inset 3px 0 0 var(--hot); }
.card .eyebrow { margin: 0; font-family: var(--mono); font-size: .6rem; letter-spacing: .06em; color: var(--ink-2); display: flex; gap: .5rem; align-items: baseline; }
.card .eyebrow b { color: var(--hot); font-weight: 600; }
.card h3 { font-family: var(--serif); font-weight: 500; font-size: .95rem; line-height: 1.15; letter-spacing: -.02em; margin: 0; }
.card .desc { margin: 0; font-size: .87rem; color: var(--ink-2); max-width: 52ch; text-wrap: pretty; }
.flag { display: inline-block; margin-left: .4rem; font-family: var(--mono); font-size: .58rem; letter-spacing: .1em; text-transform: uppercase; color: var(--hot); border: 1px dashed currentColor; border-radius: 999px; padding: .1rem .45rem; vertical-align: middle; }
.flag--inline { margin: 0; }
.tokens { list-style: none; display: flex; flex-wrap: wrap; gap: .25rem; margin: 0; padding: 0; }
.tokens li { font-family: var(--mono); font-size: .63rem; letter-spacing: .04em; text-transform: uppercase; padding: .15rem .38rem; border: 1px dashed var(--rule); color: var(--ink-2); }
.cost--free { color: var(--accent); border-color: currentColor; }
.cost--heavy { color: var(--hot); border-color: currentColor; }
.notes { margin: 0; display: grid; grid-template-columns: max-content 1fr; gap: .15rem .6rem; font-size: .79rem; }
.notes dt { font-family: var(--mono); font-size: .6rem; letter-spacing: .12em; text-transform: uppercase; color: var(--accent); padding-top: .12rem; }
.notes dd { margin: 0; color: var(--ink-2); }
.card[hidden] { display: none; }

.kits { margin-top: 3rem; border-top: 1px solid var(--rule); padding-top: 1.5rem; }
.kits h2, .legend h2 { font-family: var(--serif); font-weight: 500; font-size: 1.5rem; letter-spacing: -.025em; margin: 0 0 .5rem; }
.kits__cols { display: grid; gap: 1px; grid-template-columns: repeat(auto-fit, minmax(min(100%, 15rem), 1fr)); background: var(--rule); border: 1px solid var(--rule); margin-top: 1rem; }
.kit { background: var(--paper); padding: .9rem; display: flex; flex-direction: column; gap: .5rem; align-items: start; }
.kit h3 { font-family: var(--serif); font-weight: 500; font-size: 1.05rem; margin: 0; }
.kit p { margin: 0; font-size: .82rem; color: var(--ink-2); }
.kit__ids { font-family: var(--mono); font-size: .66rem; line-height: 1.7; }
.legend { margin-top: 2.5rem; border-top: 1px solid var(--rule); padding-top: 1.5rem; }
.legend__cols { display: grid; gap: 1.5rem 2.5rem; grid-template-columns: repeat(auto-fit, minmax(min(100%, 17rem), 1fr)); }
.legend h3 { font-family: var(--mono); font-size: .68rem; letter-spacing: .14em; text-transform: uppercase; color: var(--accent); margin: 0 0 .5rem; }
.legend dl { margin: 0; }
.legend dt { font-size: .82rem; }
.legend dt code { color: var(--ink-2); }
.legend dd { margin: 0 0 .6rem; font-size: .8rem; color: var(--ink-2); max-width: 46ch; }
.credits { margin-top: 2rem; border-top: 1px solid var(--rule); padding-top: 1rem; }
.credits p { margin: 0; font-family: var(--mono); font-size: .7rem; line-height: 1.6; color: var(--ink-2); max-width: 80ch; }

.tray { position: fixed; left: 0; right: 0; bottom: 0; z-index: 10; display: flex; flex-wrap: wrap; gap: .5rem 1rem; align-items: center; padding: .7rem clamp(1rem, 4vw, 3rem); background: var(--ink); color: var(--paper); }
.tray[hidden] { display: none; }
.tray p { margin: 0; font-family: var(--mono); font-size: .74rem; flex: 1 1 14rem; word-break: break-word; }
.tray .btn { border-color: rgb(255 255 255 / .45); color: var(--paper); }
.empty { font-family: var(--mono); font-size: .8rem; color: var(--ink-2); padding: 2rem 0; }
.empty[hidden] { display: none; }

@media (max-width: 720px) { .toolbar { position: static; } .notes { grid-template-columns: 1fr; } }
"""


def _css_stages() -> str:
    """The mocks: neutral, quiet, identical across cards so the movement is the only variable."""
    return """
/* ------------------------------------------------------------------ palchi */
.stage { position: relative; display: grid; place-items: center; aspect-ratio: 16 / 9; overflow: hidden;
  background: var(--paper-2); border: 1px solid var(--rule); container-type: inline-size; }
.stage > * { position: relative; }
.s-block { width: 34%; height: 34%; background: var(--ink); }
.s-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4cqw; width: 74%; }
.s-grid i { aspect-ratio: 1; background: var(--ink); opacity: .82; }
.s-line { font-family: var(--serif); font-size: 8.5cqw; line-height: 1; letter-spacing: -.02em; color: var(--ink); white-space: nowrap; }
.s-words i, .s-chars i { display: inline-block; font-style: normal; }
.s-words i + i { margin-left: .22em; }
.s-chars { font-family: var(--sans); font-weight: 800; font-size: 9cqw; letter-spacing: -.03em; }
.s-photo { width: 72%; aspect-ratio: 16 / 10; overflow: hidden; background: var(--ink); }
.s-photo i { position: absolute; inset: 0; background:
  linear-gradient(165deg, #3f5c68 0%, #6d8a86 42%, #c2a878 72%, #8a5a3c 100%); }
.s-btn { display: inline-flex; align-items: center; justify-content: center; padding: 2.6cqw 5cqw; overflow: hidden;
  border: 1px solid var(--ink); color: var(--ink); font-family: var(--mono); font-size: 3.4cqw; letter-spacing: .1em; text-transform: uppercase; }
.s-btn em { font-style: normal; display: block; }
.s-link { font-family: var(--serif); font-size: 6.5cqw; color: var(--ink); padding-bottom: .12em; }
.s-card { display: flex; flex-direction: column; gap: 1.4cqw; width: 52%; padding: 3cqw; background: var(--paper);
  box-shadow: 0 .4cqw 1.4cqw rgb(0 0 0 / .16); }
.s-card__ph { display: block; aspect-ratio: 16 / 9; background: linear-gradient(150deg, #3f5c68, #c2a878); }
.s-card b { font-family: var(--serif); font-weight: 500; font-size: 4.4cqw; }
.s-card em { font-style: normal; font-size: 3cqw; color: var(--ink-2); }
.s-card u { text-decoration: none; font-family: var(--mono); font-size: 2.8cqw; letter-spacing: .1em; text-transform: uppercase; color: var(--accent); }
.s-nav { position: absolute; top: 0; left: 0; right: 0; display: flex; align-items: center; gap: 4cqw; padding: 3.4cqw 4cqw;
  background: var(--paper); border-bottom: 1px solid var(--rule); }
.s-nav b { font-family: var(--serif); font-size: 4cqw; margin-right: auto; }
.s-nav i { font-style: normal; font-family: var(--mono); font-size: 2.9cqw; letter-spacing: .08em; text-transform: uppercase; color: var(--ink-2); }
.s-nav__ind { position: absolute; left: 46%; bottom: 0; width: 12cqw; height: 2px; background: var(--hot); }
.s-list { display: flex; flex-direction: column; gap: 2.4cqw; width: 70%; }
.s-list i { height: 6cqw; background: var(--ink); opacity: .16; }
.s-path { width: 46%; }
.s-path svg { display: block; width: 100%; overflow: visible; }
.s-path circle, .s-path path { fill: none; stroke: var(--ink); stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }
.s-path .subj--tick { stroke: var(--accent); }
.s-path__ring { display: none; font-family: var(--mono); font-size: 8px; letter-spacing: .22em; fill: var(--ink); stroke: none; }
.s-dots { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4cqw; width: 62%; }
.s-dots i { aspect-ratio: 1; border-radius: 50%; background: var(--ink); opacity: .5; }
.s-bar { width: 66%; height: 3cqw; background: rgb(22 21 26 / .14); overflow: hidden; }
.s-bar i { display: block; width: 40%; height: 100%; background: var(--accent); }
.s-panel { display: flex; flex-direction: column; gap: 2cqw; width: 54%; padding: 3.4cqw; background: var(--paper);
  box-shadow: 0 .6cqw 2cqw rgb(0 0 0 / .2); }
.s-panel b { display: block; height: 3.4cqw; width: 60%; background: var(--ink); opacity: .8; }
.s-panel em { display: block; height: 2.4cqw; width: 90%; background: var(--ink); opacity: .2; }
.s-cursor { position: absolute; inset: 0; display: grid; place-items: center; }
.s-cursor b { font-family: var(--serif); font-size: 7cqw; color: var(--ink); }
.s-cursor i { position: absolute; left: 50%; top: 50%; width: 5cqw; height: 5cqw; margin: -2.5cqw 0 0 -2.5cqw;
  border: 1px solid var(--hot); border-radius: 50%; }
.s-num { font-family: var(--mono); font-size: 14cqw; font-variant-numeric: tabular-nums; letter-spacing: -.04em; color: var(--ink); }
.s-num i { font-style: normal; }
.s-blob { width: 44%; aspect-ratio: 1; }
.s-blob i { position: absolute; inset: 0; background: radial-gradient(circle at 34% 32%, #6d8a86, #3f5c68);
  border-radius: 46% 54% 40% 60% / 52% 44% 56% 48%; filter: blur(.4cqw); }
.s-scene { width: 34%; aspect-ratio: 1; perspective: 60cqw; }
.s-scene .subj { position: absolute; inset: 0; transform-style: preserve-3d; }
.s-scene b { position: absolute; inset: 0; border: 1px solid var(--ink); background: rgb(63 92 104 / .3); }
.s-scene .f1 { transform: translateZ(6cqw); }
.s-scene .f2 { transform: rotateY(90deg) translateZ(6cqw); }
.s-scene .f3 { transform: rotateY(180deg) translateZ(6cqw); }
.s-scene .f4 { transform: rotateY(270deg) translateZ(6cqw); }
.s-page { position: absolute; inset: 0; }
.s-page i { position: absolute; inset: 0; display: block; }
.s-page .p-a { background: linear-gradient(150deg, #3f5c68, #6d8a86); }
.s-page .p-b { background: linear-gradient(150deg, #8a5a3c, #c2a878); }
.s-scrollbox { position: absolute; inset: 8% 20%; overflow: hidden; background: var(--paper); }
.s-scrollbox .subj { position: absolute; left: 0; right: 0; top: 0; display: flex; flex-direction: column; gap: 3cqw; padding: 3cqw; }
.s-scrollbox b { display: block; height: 10cqw; background: var(--ink); opacity: .16; }

/* pausa globale + rispetto delle preferenze di sistema */
body.is-paused .stage *, body.is-paused .stage { animation-play-state: paused !important; }
@media (prefers-reduced-motion: reduce) {
  .stage *, .stage { animation: none !important; transition: none !important; }
  .stage::after { content: "movimento disattivato dal sistema"; position: absolute; left: 0; right: 0; bottom: 0;
    font-family: var(--mono); font-size: .6rem; letter-spacing: .08em; text-transform: uppercase;
    text-align: center; padding: .3rem; background: var(--ink); color: var(--paper); }
}
"""


def _css_effects() -> str:
    """One block per effect. The tile loops so the movement is visible without interaction."""
    return """
/* ------------------------------------------------------------------ effetti */
/* 1-11 reveal */
@keyframes k-fade { 0%,12% { opacity: 0 } 45%,88% { opacity: 1 } 100% { opacity: 0 } }
.fx--fade-in .subj { animation: k-fade 3.4s ease-in-out infinite; }
@keyframes k-fade-up { 0%,12% { opacity: 0; transform: translateY(28%) } 45%,88% { opacity: 1; transform: none } 100% { opacity: 0; transform: translateY(28%) } }
.fx--fade-up .subj { animation: k-fade-up 3.4s cubic-bezier(.2,.7,.3,1) infinite; }
@keyframes k-zoom { 0%,12% { opacity: 0; transform: scale(.82) } 45%,88% { opacity: 1; transform: none } 100% { opacity: 0; transform: scale(.82) } }
.fx--zoom-in .subj { animation: k-zoom 3.4s cubic-bezier(.2,.7,.3,1) infinite; }
@keyframes k-blur { 0%,12% { opacity: 0; filter: blur(1.6cqw) } 45%,88% { opacity: 1; filter: blur(0) } 100% { opacity: 0; filter: blur(1.6cqw) } }
.fx--blur-in .subj { animation: k-blur 3.6s ease-in-out infinite; }
@keyframes k-clip { 0%,10% { clip-path: inset(0 100% 0 0) } 45%,88% { clip-path: inset(0 0 0 0) } 100% { clip-path: inset(0 0 0 100%) } }
.fx--clip-wipe .subj { animation: k-clip 3.6s cubic-bezier(.7,0,.2,1) infinite; }
@keyframes k-maskrev { 0%,8% { clip-path: inset(0 0 100% 0); transform: scale(1.12) } 46%,88% { clip-path: inset(0 0 0 0); transform: none } 100% { clip-path: inset(100% 0 0 0); transform: none } }
.fx--mask-reveal .subj { animation: k-maskrev 3.8s cubic-bezier(.66,0,.24,1) infinite; }
@keyframes k-flip { 0%,12% { opacity: .2; transform: perspective(60cqw) rotateY(-84deg) } 46%,88% { opacity: 1; transform: perspective(60cqw) rotateY(0) } 100% { opacity: .2; transform: perspective(60cqw) rotateY(84deg) } }
.fx--flip-3d .subj { animation: k-flip 3.6s cubic-bezier(.3,.7,.3,1) infinite; }
@keyframes k-rot { 0%,12% { opacity: 0; transform: rotate(-7deg) translateY(14%) } 46%,88% { opacity: 1; transform: none } 100% { opacity: 0; transform: rotate(7deg) } }
.fx--rotate-in .subj { animation: k-rot 3.4s cubic-bezier(.2,.8,.3,1) infinite; }
.fx--stagger-grid .subj { animation: k-fade-up 3.2s cubic-bezier(.2,.7,.3,1) infinite; }
.fx--stagger-grid .subj:nth-child(2) { animation-delay: .09s }
.fx--stagger-grid .subj:nth-child(3) { animation-delay: .18s }
.fx--stagger-grid .subj:nth-child(4) { animation-delay: .27s }
.fx--stagger-grid .subj:nth-child(5) { animation-delay: .36s }
.fx--stagger-grid .subj:nth-child(6) { animation-delay: .45s }
.fx--seq-section .subj > * { animation: k-fade-up 3.6s cubic-bezier(.2,.7,.3,1) infinite; }
.fx--seq-section .subj > *:nth-child(2) { animation-delay: .12s }
.fx--seq-section .subj > *:nth-child(3) { animation-delay: .24s }
.fx--seq-section .subj > *:nth-child(4) { animation-delay: .4s }
@keyframes k-curtain { 0%,10% { clip-path: inset(0 50% 0 50%) } 46%,88% { clip-path: inset(0 0 0 0) } 100% { clip-path: inset(0 50% 0 50%) } }
.fx--curtain .subj { animation: k-curtain 3.6s cubic-bezier(.7,0,.2,1) infinite; }

/* 12-23 testo */
@keyframes k-char { 0%,10% { opacity: 0; transform: translateY(45%) } 42%,86% { opacity: 1; transform: none } 100% { opacity: 0; transform: translateY(-30%) } }
.fx--split-chars .subj { animation: k-char 3.4s cubic-bezier(.2,.8,.3,1) infinite; }
.fx--split-chars .subj:nth-child(2) { animation-delay: .05s } .fx--split-chars .subj:nth-child(3) { animation-delay: .1s }
.fx--split-chars .subj:nth-child(4) { animation-delay: .15s } .fx--split-chars .subj:nth-child(5) { animation-delay: .2s }
.fx--split-chars .subj:nth-child(6) { animation-delay: .25s } .fx--split-chars .subj:nth-child(7) { animation-delay: .3s }
.fx--split-chars .subj:nth-child(8) { animation-delay: .35s } .fx--split-chars .subj:nth-child(9) { animation-delay: .4s }
.fx--split-words .subj { animation: k-char 3.4s cubic-bezier(.2,.8,.3,1) infinite; }
.fx--split-words .subj:nth-child(2) { animation-delay: .12s } .fx--split-words .subj:nth-child(3) { animation-delay: .24s }
.fx--split-lines .s-line { overflow: hidden; display: inline-block; }
@keyframes k-lines { 0%,10% { transform: translateY(105%) } 44%,86% { transform: none } 100% { transform: translateY(-105%) } }
.fx--split-lines .subj { animation: k-lines 3.6s cubic-bezier(.5,0,.15,1) infinite; }
.fx--split-lines .subj:nth-child(2) { animation-delay: .1s } .fx--split-lines .subj:nth-child(3) { animation-delay: .2s }
@keyframes k-type { 0% { width: 0 } 55%,80% { width: 100% } 100% { width: 0 } }
@keyframes k-caret { 50% { border-color: transparent } }
.fx--typewriter .subj { display: inline-block; overflow: hidden; white-space: nowrap; vertical-align: bottom;
  border-right: .1em solid var(--hot); animation: k-type 4s steps(18) infinite, k-caret .7s step-end infinite; }
@keyframes k-scramble { 0%,30% { opacity: .25; letter-spacing: .3em; filter: blur(.3cqw) } 55%,88% { opacity: 1; letter-spacing: -.02em; filter: none } 100% { opacity: .25; letter-spacing: .3em; filter: blur(.3cqw) } }
.fx--scramble .subj { animation: k-scramble 3.4s steps(9, end) infinite; }
@keyframes k-count { 0%,8% { transform: translateY(0) } 40%,88% { transform: translateY(-66.66%) } 100% { transform: translateY(-66.66%) } }
.fx--counter .s-num { overflow: hidden; height: 1em; }
.fx--counter .subj::after { content: "\\A 64 \\A 128"; white-space: pre; }
.fx--counter .subj { display: block; animation: k-count 3.4s cubic-bezier(.2,.8,.2,1) infinite; }
@keyframes k-odo { 0% { transform: translateY(0) } 100% { transform: translateY(-66.66%) } }
.fx--odometer .s-num { overflow: hidden; height: 1em; }
.fx--odometer .subj::after { content: "\\A 129 \\A 130"; white-space: pre; }
.fx--odometer .subj { display: block; animation: k-odo 1.8s steps(2) infinite; }
@keyframes k-marquee { to { transform: translateX(-50%) } }
.fx--marquee .s-line { display: flex; width: max-content; animation: k-marquee 6s linear infinite; }
.fx--marquee .subj::after { content: " · Movimento giusto · Movimento giusto"; }
@keyframes k-marquee-scroll { 0% { transform: translateX(0) } 40% { transform: translateX(-14%) } 55% { transform: translateX(-11%) } 100% { transform: translateX(-40%) } }
.fx--marquee-scroll .s-line { display: flex; width: max-content; animation: k-marquee-scroll 5s cubic-bezier(.4,0,.5,1) infinite alternate; }
.fx--marquee-scroll .subj::after { content: " · Movimento giusto · Movimento giusto"; }
@keyframes k-spin { to { transform: rotate(360deg) } }
.fx--circular-text .s-path svg { animation: k-spin 9s linear infinite; }
.fx--circular-text .subj--tick, .fx--circular-text circle { display: none; }
.fx--circular-text .s-path__ring { display: block; }
@keyframes k-grad { to { background-position: 200% 0 } }
.fx--gradient-text .subj { background: linear-gradient(90deg, #2f5d50, #b1442a, #3f5c68, #2f5d50);
  background-size: 200% 100%; -webkit-background-clip: text; background-clip: text; color: transparent;
  animation: k-grad 3.6s linear infinite; }
@keyframes k-underline { 0%,8% { transform: scaleX(0) } 46%,88% { transform: scaleX(1) } 100% { transform: scaleX(0) } }
.fx--underline-draw .subj { position: relative; }
.fx--underline-draw .subj::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: .1em;
  background: var(--hot); transform-origin: left; animation: k-underline 3.4s cubic-bezier(.6,0,.2,1) infinite; }

/* 24-37 scroll */
.fx--reveal-scroll .subj { animation: k-fade-up 3.4s cubic-bezier(.2,.7,.3,1) infinite; }
.fx--reveal-scroll .subj:nth-child(4) { animation-delay: .1s } .fx--reveal-scroll .subj:nth-child(5) { animation-delay: .16s }
.fx--reveal-scroll .subj:nth-child(6) { animation-delay: .22s }
@keyframes k-par-a { 0% { transform: translateY(9%) } 100% { transform: translateY(-9%) } }
@keyframes k-par-b { 0% { transform: translateY(16%) scale(1.42) } 100% { transform: translateY(-16%) scale(1.42) } }
.fx--parallax-layers .s-photo { overflow: hidden; }
.fx--parallax-layers .subj { animation: k-par-b 3.4s ease-in-out infinite alternate; }
.fx--parallax-layers .s-photo::after { content: ""; position: absolute; left: 18%; right: 18%; top: 34%; height: 22%;
  background: var(--paper); animation: k-par-a 3.4s ease-in-out infinite alternate; }
.fx--parallax-bg .subj { animation: k-par-b 4s ease-in-out infinite alternate; }
@keyframes k-scrub { 0% { transform: scale(1) rotate(0) } 100% { transform: scale(1.16) rotate(4deg) } }
.fx--scrub .subj { animation: k-scrub 3s cubic-bezier(.5,0,.5,1) infinite alternate; }
@keyframes k-pin-inner { 0%,18% { transform: translateY(0) } 82%,100% { transform: translateY(-52%) } }
.fx--pin .subj { animation: k-pin-inner 4s cubic-bezier(.4,0,.4,1) infinite alternate; }
.fx--pin .s-scrollbox::after { content: "pinned"; position: absolute; left: 0; top: 0; padding: .2rem .4rem;
  font-family: var(--mono); font-size: .55rem; letter-spacing: .1em; text-transform: uppercase; background: var(--ink); color: var(--paper); }
@keyframes k-hscroll { 0% { transform: translateX(14%) } 100% { transform: translateX(-14%) } }
.fx--hscroll .s-grid { grid-template-columns: repeat(6, 1fr); width: 128%; animation: k-hscroll 4s cubic-bezier(.4,0,.4,1) infinite alternate; }
@keyframes k-prog { 0% { width: 4% } 100% { width: 100% } }
.fx--progress-bar .s-bar { position: absolute; top: 0; left: 0; right: 0; width: auto; height: 2.4cqw; }
.fx--progress-bar .subj { animation: k-prog 3.4s cubic-bezier(.4,0,.5,1) infinite alternate; }
@keyframes k-shrink { 0%,20% { padding-top: 5.6cqw; padding-bottom: 5.6cqw } 80%,100% { padding-top: 2cqw; padding-bottom: 2cqw } }
.fx--header-shrink .s-nav { animation: k-shrink 3.4s ease-in-out infinite alternate; }
@keyframes k-hide { 0%,30% { transform: translateY(0) } 60%,80% { transform: translateY(-110%) } 100% { transform: translateY(0) } }
.fx--header-hide .s-nav { animation: k-hide 4s cubic-bezier(.5,0,.3,1) infinite; }
@keyframes k-snap { 0%,22% { transform: translateY(0) } 30%,52% { transform: translateY(-25%) } 60%,82% { transform: translateY(-50%) } 90%,100% { transform: translateY(-75%) } }
.fx--scroll-snap .subj { animation: k-snap 5s cubic-bezier(.6,0,.2,1) infinite; }
@keyframes k-seqframes { 0%,100% { filter: hue-rotate(0) saturate(1) } 25% { filter: hue-rotate(24deg) saturate(1.3) } 50% { filter: hue-rotate(-18deg) saturate(.85) } 75% { filter: hue-rotate(12deg) saturate(1.15) } }
.fx--image-seq .subj { animation: k-seqframes 2.4s steps(1, end) infinite; }
.fx--scroll-driven .subj { animation: k-fade-up 3s cubic-bezier(.3,.7,.3,1) infinite alternate; }
@keyframes k-smooth { 0% { transform: translateY(0) } 100% { transform: translateY(-48%) } }
.fx--smooth-scroll .subj { animation: k-smooth 3.6s cubic-bezier(.22,1,.36,1) infinite alternate; }
@keyframes k-sect-color { 0%,100% { background: #e8e3da } 33% { background: #d8e0dc } 66% { background: #e6dcd2 } }
.fx--section-color .s-scrollbox { animation: k-sect-color 5s ease-in-out infinite; }
.fx--section-color .subj { animation: k-smooth 5s linear infinite alternate; }

/* 38-49 hero e sfondi */
@keyframes k-ken { 0% { transform: scale(1) translate(0,0) } 100% { transform: scale(1.14) translate(-2%, -2%) } }
.fx--ken-burns .subj { animation: k-ken 7s ease-in-out infinite alternate; }
@keyframes k-cross { 0%,42% { opacity: 1 } 58%,100% { opacity: 0 } }
.fx--hero-crossfade .s-photo { background: linear-gradient(150deg, #8a5a3c, #c2a878); }
.fx--hero-crossfade .subj { animation: k-cross 3.6s ease-in-out infinite alternate; }
@keyframes k-videobg { 0% { transform: scale(1.06) translateX(-1%) } 100% { transform: scale(1.06) translateX(1%) } }
.fx--video-bg .subj { animation: k-videobg 6s ease-in-out infinite alternate; }
.fx--video-bg .s-photo::after { content: ""; position: absolute; inset: 0; background: linear-gradient(0deg, rgb(0 0 0 / .55), transparent 70%); }
.fx--text-video-mask .subj { background: linear-gradient(150deg, #3f5c68, #6d8a86 40%, #c2a878 75%, #8a5a3c);
  background-size: 160% 160%; -webkit-background-clip: text; background-clip: text; color: transparent;
  font-family: var(--sans); font-weight: 900; animation: k-mesh 6s ease-in-out infinite alternate; }
@keyframes k-mesh { 0% { background-position: 0% 0% } 100% { background-position: 100% 100% } }
.fx--gradient-mesh .subj { width: 100%; height: 100%; background:
  radial-gradient(circle at 24% 28%, #6d8a86, transparent 44%),
  radial-gradient(circle at 76% 70%, #c2a878, transparent 46%),
  radial-gradient(circle at 52% 88%, #3f5c68, transparent 40%); background-size: 160% 160%;
  animation: k-mesh 7s ease-in-out infinite alternate; }
@keyframes k-blob-move { 0% { transform: translate(-6%, 4%) scale(1) } 100% { transform: translate(6%, -4%) scale(1.12) } }
.fx--aurora .subj { filter: blur(1.6cqw); animation: k-blob-move 5s ease-in-out infinite alternate; }
@keyframes k-particle { 0%,100% { transform: translateY(0) scale(1); opacity: .45 } 50% { transform: translateY(-22%) scale(1.3); opacity: .9 } }
.fx--particles .subj { animation: k-particle 3s ease-in-out infinite; }
.fx--particles .subj:nth-child(2n) { animation-delay: .5s } .fx--particles .subj:nth-child(3n) { animation-delay: 1.1s }
.fx--particles .subj:nth-child(5n) { animation-delay: 1.7s }
.fx--starfield .subj { animation: k-particle 3.4s ease-in-out infinite; }
.fx--starfield .subj:nth-child(2n) { animation-delay: .7s } .fx--starfield .subj:nth-child(3n) { animation-delay: 1.4s }
.fx--starfield .s-dots::after { content: ""; position: absolute; inset: 12% 6%; border-top: 1px solid rgb(22 21 26 / .2);
  border-bottom: 1px solid rgb(22 21 26 / .2); transform: rotate(-8deg); }
@keyframes k-distort { 0%,100% { transform: skewY(0) scale(1) } 50% { transform: skewY(2.5deg) scale(1.06) } }
.fx--shader-distort .subj { animation: k-distort 3.4s ease-in-out infinite; }
@keyframes k-ripple { 0% { transform: scale(.2); opacity: .7 } 100% { transform: scale(2.4); opacity: 0 } }
.fx--ripple .s-photo::after { content: ""; position: absolute; left: 42%; top: 44%; width: 20%; aspect-ratio: 1;
  border: 2px solid rgb(255 255 255 / .85); border-radius: 50%; animation: k-ripple 2.6s ease-out infinite; }
@keyframes k-noise { 0% { transform: translate(0,0) } 25% { transform: translate(-2%, 1%) } 50% { transform: translate(1%, -2%) } 75% { transform: translate(2%, 2%) } 100% { transform: translate(0,0) } }
.fx--noise .s-photo::after { content: ""; position: absolute; inset: -6%; opacity: .3; mix-blend-mode: overlay;
  background-size: 3px 3px; background-image: repeating-conic-gradient(#fff 0 25%, #000 0 50%);
  animation: k-noise .5s steps(1) infinite; }
@keyframes k-split-open { 0%,14% { transform: translateX(0) } 60%,100% { transform: translateX(-102%) } }
.fx--split-open .stage, .fx--split-open .s-block { position: relative; }
.fx--split-open .subj::before, .fx--split-open .subj::after { content: ""; position: absolute; top: -200%; bottom: -200%; width: 300%; background: var(--paper-2); }
.fx--split-open .subj::before { right: 100%; animation: k-split-open 3.6s cubic-bezier(.7,0,.2,1) infinite alternate; }
.fx--split-open .subj::after { left: 100%; animation: k-split-open 3.6s cubic-bezier(.7,0,.2,1) infinite alternate reverse; }

/* 50-65 hover */
@keyframes k-imgzoom { 0%,100% { transform: scale(1) } 50% { transform: scale(1.09) } }
.fx--img-zoom .subj { animation: k-imgzoom 3.4s ease-in-out infinite; }
@keyframes k-caption { 0%,25% { transform: translateY(100%); opacity: 0 } 50%,80% { transform: none; opacity: 1 } 100% { transform: translateY(100%); opacity: 0 } }
.fx--caption-rise .s-photo::after { content: "Casa sul mare"; position: absolute; left: 0; right: 0; bottom: 0;
  padding: 4cqw 3cqw 3cqw; font-family: var(--mono); font-size: 3cqw; letter-spacing: .1em; text-transform: uppercase;
  color: #fff; background: linear-gradient(0deg, rgb(0 0 0 / .7), transparent);
  animation: k-caption 3.4s cubic-bezier(.3,.8,.3,1) infinite; }
@keyframes k-lift { 0%,100% { transform: translateY(0); box-shadow: 0 .4cqw 1.4cqw rgb(0 0 0 / .16) } 50% { transform: translateY(-4%); box-shadow: 0 1.6cqw 3.4cqw rgb(0 0 0 / .26) } }
.fx--card-lift .subj { animation: k-lift 3s ease-in-out infinite; }
@keyframes k-tilt { 0%,100% { transform: perspective(60cqw) rotateX(6deg) rotateY(-9deg) } 50% { transform: perspective(60cqw) rotateX(-5deg) rotateY(9deg) } }
.fx--tilt-3d .subj { animation: k-tilt 4s ease-in-out infinite; }
@keyframes k-fill { 0%,12% { transform: scaleX(0) } 48%,88% { transform: scaleX(1) } 100% { transform: scaleX(0) } }
.fx--btn-fill .subj { position: relative; }
.fx--btn-fill .subj::before { content: ""; position: absolute; inset: 0; background: var(--ink); transform-origin: left;
  animation: k-fill 3.4s cubic-bezier(.6,0,.2,1) infinite; }
.fx--btn-fill em { position: relative; mix-blend-mode: difference; color: #fff; }
@keyframes k-magnet { 0%,100% { transform: translate(0,0) } 30% { transform: translate(9%, -7%) } 65% { transform: translate(-7%, 5%) } }
.fx--btn-magnetic .subj { animation: k-magnet 3.6s cubic-bezier(.3,.8,.3,1) infinite; }
.fx--link-underline .subj { position: relative; }
.fx--link-underline .subj::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 1px;
  background: currentColor; transform-origin: left; animation: k-underline 3s cubic-bezier(.6,0,.2,1) infinite; }
@keyframes k-roll { 0%,20% { transform: translateY(0) } 50%,100% { transform: translateY(-100%) } }
/* la finestra è alta esattamente una riga: il duplicato entra solo scorrendo */
.fx--text-roll .subj { overflow: hidden; height: 5.1cqw; align-items: flex-start; padding: 1.7cqw 5cqw 0; }
.fx--text-roll em { line-height: 1; animation: k-roll 3s cubic-bezier(.6,0,.2,1) infinite; }
.fx--text-roll em::after { content: "Prenota ora"; display: block; }
@keyframes k-ripple-click { 0% { transform: translate(-50%,-50%) scale(0); opacity: .55 } 100% { transform: translate(-50%,-50%) scale(4); opacity: 0 } }
.fx--ripple-click .subj { position: relative; }
.fx--ripple-click .subj::after { content: ""; position: absolute; left: 50%; top: 50%; width: 30%; aspect-ratio: 1;
  border-radius: 50%; background: var(--ink); animation: k-ripple-click 2.4s ease-out infinite; }
@keyframes k-cursor { 0% { transform: translate(-120%, 80%) } 35% { transform: translate(60%, -40%) } 70% { transform: translate(-40%, -90%) } 100% { transform: translate(-120%, 80%) } }
.fx--cursor-follow .subj { animation: k-cursor 5s cubic-bezier(.4,0,.4,1) infinite; }
@keyframes k-cursor-exp { 0%,30% { transform: scale(1); background: transparent } 50%,80% { transform: scale(3.4); background: rgb(177 68 42 / .18) } 100% { transform: scale(1); background: transparent } }
.fx--cursor-expand .subj { animation: k-cursor-exp 3.4s cubic-bezier(.3,.8,.3,1) infinite; }
@keyframes k-trail { 0% { opacity: 0; transform: translate(-40%, 18%) scale(.8) } 30% { opacity: 1 } 100% { opacity: 0; transform: translate(40%, -18%) scale(1) } }
.fx--image-trail .s-photo { width: 44%; }
.fx--image-trail .subj { animation: k-trail 2.4s ease-out infinite; }
.fx--image-trail .s-photo::after, .fx--image-trail .s-photo::before { content: ""; position: absolute; inset: 0;
  background: linear-gradient(165deg, #8a5a3c, #c2a878); animation: k-trail 2.4s ease-out infinite; }
.fx--image-trail .s-photo::before { animation-delay: .3s } .fx--image-trail .s-photo::after { animation-delay: .6s }
@keyframes k-preview { 0%,20% { opacity: 0; transform: translate(-50%,-50%) scale(.9) } 40%,80% { opacity: 1; transform: translate(-50%,-50%) scale(1) } 100% { opacity: 0; transform: translate(-50%,-50%) scale(.9) } }
@keyframes k-hl { 0%,20% { opacity: .16 } 40%,80% { opacity: .5 } 100% { opacity: .16 } }
.fx--hover-preview .subj:nth-child(2) { animation: k-hl 3.4s ease-in-out infinite; }
.fx--hover-preview .s-list::after { content: ""; position: absolute; left: 50%; top: 50%; width: 34%; aspect-ratio: 4/3;
  background: linear-gradient(150deg, #3f5c68, #c2a878); animation: k-preview 3.4s cubic-bezier(.3,.8,.3,1) infinite; }
@keyframes k-morph { 0%,45% { clip-path: polygon(28% 20%, 28% 80%, 78% 50%) } 55%,100% { clip-path: polygon(28% 20%, 28% 80%, 44% 80%, 44% 20%) } }
.fx--icon-morph .subj { position: relative; }
.fx--icon-morph .subj::after { content: ""; position: absolute; inset: 0; background: var(--ink); animation: k-morph 3s cubic-bezier(.6,0,.2,1) infinite; }
.fx--icon-morph em { opacity: 0; }
@keyframes k-glow { to { --a: 360deg; transform: rotate(360deg) } }
.fx--glow-border .subj { position: relative; }
.fx--glow-border .subj::before { content: ""; position: absolute; inset: -40%; z-index: -1;
  background: conic-gradient(from 0deg, transparent 0 65%, var(--hot) 78%, transparent 88%);
  animation: k-glow 2.6s linear infinite; }
.fx--glow-border .subj { isolation: isolate; outline: 1px solid var(--rule); }
@keyframes k-shake { 0%,72%,100% { transform: translateX(0) } 76% { transform: translateX(-7%) } 80% { transform: translateX(6%) } 84% { transform: translateX(-4%) } 88% { transform: translateX(3%) } 92% { transform: translateX(-1%) } }
.fx--shake .subj { animation: k-shake 3s ease-in-out infinite; }

/* 66-72 navigazione */
@keyframes k-burger-1 { 0%,30% { transform: translateY(-180%) rotate(0) } 55%,100% { transform: translateY(0) rotate(45deg) } }
@keyframes k-burger-2 { 0%,30% { opacity: 1 } 55%,100% { opacity: 0 } }
@keyframes k-burger-3 { 0%,30% { transform: translateY(180%) rotate(0) } 55%,100% { transform: translateY(0) rotate(-45deg) } }
.fx--hamburger .subj { position: relative; border: 0; padding: 0; width: 16cqw; aspect-ratio: 1; }
.fx--hamburger em { display: none; }
.fx--hamburger .subj::before, .fx--hamburger .subj::after, .fx--hamburger .subj > i { content: ""; position: absolute;
  left: 20%; right: 20%; top: calc(50% - 1px); height: 2px; background: var(--ink); }
.fx--hamburger .subj::before { animation: k-burger-1 3s cubic-bezier(.6,0,.2,1) infinite alternate; }
.fx--hamburger .subj::after { animation: k-burger-3 3s cubic-bezier(.6,0,.2,1) infinite alternate; }
@keyframes k-menu-full { 0%,14% { clip-path: inset(0 0 100% 0) } 46%,90% { clip-path: inset(0 0 0 0) } 100% { clip-path: inset(0 0 100% 0) } }
.fx--menu-full .s-nav { position: absolute; inset: 0; flex-direction: column; align-items: flex-start; justify-content: center;
  gap: 3cqw; padding: 8cqw; background: var(--ink); border: 0; animation: k-menu-full 4s cubic-bezier(.6,0,.2,1) infinite; }
.fx--menu-full .s-nav b, .fx--menu-full .s-nav__ind { display: none; }
.fx--menu-full .subj { color: var(--paper); font-size: 6cqw; animation: k-char 4s cubic-bezier(.2,.8,.3,1) infinite; }
.fx--menu-full .subj:nth-child(3) { animation-delay: .1s } .fx--menu-full .subj:nth-child(4) { animation-delay: .2s }
@keyframes k-offcanvas { 0%,16% { transform: translateX(100%) } 50%,90% { transform: none } 100% { transform: translateX(100%) } }
.fx--offcanvas .s-nav { position: absolute; inset: 0 0 0 46%; flex-direction: column; align-items: flex-start;
  justify-content: center; gap: 3cqw; padding: 5cqw; background: var(--ink); border: 0;
  animation: k-offcanvas 4s cubic-bezier(.5,0,.2,1) infinite; }
.fx--offcanvas .s-nav b { display: none; } .fx--offcanvas .s-nav__ind { display: none; }
.fx--offcanvas .subj { color: var(--paper); }
@keyframes k-mega { 0%,20% { opacity: 0; transform: translateY(-8%) } 46%,86% { opacity: 1; transform: none } 100% { opacity: 0; transform: translateY(-8%) } }
.fx--megamenu .s-nav::after { content: ""; position: absolute; left: 40%; right: 4cqw; top: 100%; height: 20cqw;
  background: var(--paper); box-shadow: 0 1cqw 2cqw rgb(0 0 0 / .18); animation: k-mega 3.6s cubic-bezier(.3,.8,.3,1) infinite; }
@keyframes k-indicator { 0%,20% { left: 46%; width: 12cqw } 45%,70% { left: 62%; width: 14cqw } 95%,100% { left: 80%; width: 12cqw } }
.fx--active-ind .s-nav__ind { animation: k-indicator 4s cubic-bezier(.5,0,.2,1) infinite alternate; }
@keyframes k-dock { 0%,100% { transform: scale(1) } 50% { transform: scale(1.5) translateY(-8%) } }
.fx--dock .subj { animation: k-dock 2.4s ease-in-out infinite; transform-origin: bottom; }
.fx--dock .subj:nth-child(3) { animation-delay: .25s } .fx--dock .subj:nth-child(4) { animation-delay: .5s }
@keyframes k-step { 0%,10% { width: 4% } 45%,60% { width: 52% } 92%,100% { width: 100% } }
.fx--step-progress .s-bar::before, .fx--step-progress .s-bar::after { content: ""; position: absolute; top: 50%;
  width: 3cqw; aspect-ratio: 1; margin-top: -1.5cqw; border-radius: 50%; background: var(--paper); box-shadow: 0 0 0 1px var(--rule); }
.fx--step-progress .s-bar { position: relative; overflow: visible; }
.fx--step-progress .s-bar::before { left: 48%; } .fx--step-progress .s-bar::after { right: 0; }
.fx--step-progress .subj { animation: k-step 4s cubic-bezier(.5,0,.2,1) infinite alternate; }

/* 73-82 layout e liste */
@keyframes k-flip-a { 0%,100% { transform: none } 50% { transform: translate(105%, 0) } }
@keyframes k-flip-b { 0%,100% { transform: none } 50% { transform: translate(-105%, 0) } }
.fx--filter-flip .subj:nth-child(1) { animation: k-flip-a 3.4s cubic-bezier(.5,0,.2,1) infinite; }
.fx--filter-flip .subj:nth-child(2) { animation: k-flip-b 3.4s cubic-bezier(.5,0,.2,1) infinite; }
.fx--filter-flip .subj:nth-child(5) { animation: k-flip-a 3.4s cubic-bezier(.5,0,.2,1) infinite .1s; }
.fx--filter-flip .subj:nth-child(6) { animation: k-flip-b 3.4s cubic-bezier(.5,0,.2,1) infinite .1s; }
@keyframes k-masonry { 0%,6% { opacity: 0; transform: translateY(40%) scaleY(.4) } 34%,92% { opacity: 1; transform: none } 100% { opacity: 0; transform: translateY(40%) scaleY(.4) } }
.fx--masonry-in .s-grid { align-items: start; }
.fx--masonry-in .subj { transform-origin: top; animation: k-masonry 3.6s cubic-bezier(.3,.8,.3,1) infinite; }
.fx--masonry-in .subj:nth-child(2) { aspect-ratio: 1/1.6; animation-delay: .12s }
.fx--masonry-in .subj:nth-child(3) { animation-delay: .24s } .fx--masonry-in .subj:nth-child(5) { aspect-ratio: 1/.7; animation-delay: .3s }
@keyframes k-accordion { 0%,18% { grid-template-rows: 0fr } 50%,88% { grid-template-rows: 1fr } 100% { grid-template-rows: 0fr } }
.fx--accordion .s-list i:nth-child(2) { display: grid; height: auto; opacity: 1; background: none;
  animation: k-accordion 3.6s cubic-bezier(.5,0,.2,1) infinite; }
.fx--accordion .s-list i:nth-child(2)::after { content: ""; display: block; min-height: 0; overflow: hidden;
  background: var(--ink); opacity: .16; }
@keyframes k-tab-a { 0%,45% { opacity: 1 } 55%,100% { opacity: 0 } }
.fx--tabs-cross .s-grid { grid-template-columns: 1fr; width: 44%; }
.fx--tabs-cross .subj:nth-child(n+3) { display: none; }
.fx--tabs-cross .subj:nth-child(1), .fx--tabs-cross .subj:nth-child(2) { grid-area: 1 / 1; aspect-ratio: 16/10; }
.fx--tabs-cross .subj:nth-child(1) { animation: k-tab-a 3.4s ease-in-out infinite alternate; }
.fx--tabs-cross .subj:nth-child(2) { background: var(--accent); animation: k-tab-a 3.4s ease-in-out infinite alternate-reverse; }
.fx--tabs-cross .s-grid::after { content: ""; position: absolute; left: 28%; right: 28%; top: -12%; height: 2px; background: var(--hot);
  animation: k-tabind 3.4s ease-in-out infinite alternate; }
@keyframes k-tabind { 0% { transform: translateX(-46%) } 100% { transform: translateX(46%) } }
@keyframes k-carousel { 0%,24% { transform: translateX(0) } 33%,57% { transform: translateX(-33.4%) } 66%,90% { transform: translateX(-66.8%) } 100% { transform: translateX(-100%) } }
.fx--carousel-loop .s-grid { width: 200%; grid-template-columns: repeat(6, 1fr); animation: k-carousel 6s cubic-bezier(.6,0,.2,1) infinite; }
@keyframes k-coverflow { 0%,100% { transform: perspective(60cqw) rotateY(38deg) scale(.78); opacity: .5 } 50% { transform: perspective(60cqw) rotateY(0) scale(1); opacity: 1 } }
.fx--coverflow .s-grid { grid-template-columns: repeat(3, 1fr); }
.fx--coverflow .subj:nth-child(n+4) { display: none; }
.fx--coverflow .subj:nth-child(1) { animation: k-coverflow 4s ease-in-out infinite; }
.fx--coverflow .subj:nth-child(2) { animation: k-coverflow 4s ease-in-out infinite 1.33s; }
.fx--coverflow .subj:nth-child(3) { animation: k-coverflow 4s ease-in-out infinite 2.66s; }
@keyframes k-ba { 0%,100% { clip-path: inset(0 62% 0 0) } 50% { clip-path: inset(0 14% 0 0) } }
@keyframes k-ba-h { 0%,100% { left: 38% } 50% { left: 86% } }
.fx--before-after .s-photo::before { content: ""; position: absolute; inset: 0; z-index: 1;
  background: linear-gradient(165deg, #8a5a3c, #c2a878); animation: k-ba 4s ease-in-out infinite; }
.fx--before-after .s-photo::after { content: ""; position: absolute; z-index: 2; top: 0; bottom: 0; width: 2px;
  background: var(--paper); animation: k-ba-h 4s ease-in-out infinite; }
@keyframes k-lightbox { 0%,16% { transform: scale(.32) translate(-64%, 48%) } 50%,88% { transform: none } 100% { transform: scale(.32) translate(-64%, 48%) } }
.fx--lightbox .s-photo { animation: k-lightbox 3.8s cubic-bezier(.4,0,.2,1) infinite; }
@keyframes k-drag { 0%,100% { transform: none; box-shadow: none } 25% { transform: translate(58%, -8%) rotate(3deg); box-shadow: 0 1.6cqw 3cqw rgb(0 0 0 / .3) } 60% { transform: translate(112%, 0) rotate(0) } }
.fx--drag-drop .subj:nth-child(1) { position: relative; z-index: 2; animation: k-drag 4s cubic-bezier(.4,0,.3,1) infinite; }
@keyframes k-shimmer { 0% { background-position: -140% 0 } 100% { background-position: 240% 0 } }
.fx--skeleton-list .subj { opacity: 1; background: linear-gradient(90deg, rgb(22 21 26 / .1) 0 40%, rgb(22 21 26 / .04) 50%, rgb(22 21 26 / .1) 60%);
  background-size: 240% 100%; animation: k-shimmer 1.8s linear infinite; }
.fx--skeleton-list .subj:nth-child(2) { animation-delay: .15s } .fx--skeleton-list .subj:nth-child(3) { animation-delay: .3s }

/* 83-88 transizioni di pagina */
@keyframes k-viewtrans { 0%,42% { opacity: 1; transform: none } 58%,100% { opacity: 0; transform: scale(1.04) } }
.fx--view-trans .p-a { animation: k-viewtrans 3.6s cubic-bezier(.4,0,.2,1) infinite alternate; }
@keyframes k-shared { 0%,20% { inset: 60% 58% 8% 8%; border-radius: 0 } 55%,90% { inset: 0; border-radius: 0 } 100% { inset: 60% 58% 8% 8% } }
.fx--shared-el .p-a { z-index: 1; animation: k-shared 3.8s cubic-bezier(.4,0,.2,1) infinite; }
@keyframes k-curtain-page { 0%,10% { transform: translateY(100%) } 40%,55% { transform: none } 90%,100% { transform: translateY(-100%) } }
.fx--curtain-page .p-b { z-index: 2; animation: k-curtain-page 3.8s cubic-bezier(.7,0,.2,1) infinite; }
@keyframes k-route { 0%,40% { opacity: 1; transform: none } 50% { opacity: 0; transform: translateX(-6%) } 60%,100% { opacity: 1; transform: none } }
.fx--route-fade .p-a { animation: k-route 3.4s ease-in-out infinite; }
@keyframes k-pre { 0% { transform: translateY(0) } 100% { transform: translateY(-66.66%) } }
.fx--preloader .s-num { overflow: hidden; height: 1em; }
.fx--preloader .subj::after { content: "\\A 68 \\A 100"; white-space: pre; }
.fx--preloader .subj { display: block; animation: k-pre 3s steps(2) infinite; }
@keyframes k-draw { 0% { stroke-dashoffset: 100 } 55%,80% { stroke-dashoffset: 0 } 100% { stroke-dashoffset: -100 } }
.fx--preloader-logo .subj { stroke-dasharray: 100; animation: k-draw 3.6s cubic-bezier(.5,0,.3,1) infinite; }
.fx--preloader-logo .subj--tick { animation-delay: .3s; }

/* 89-97 feedback */
.fx--skeleton .subj { opacity: 1; background: linear-gradient(90deg, rgb(22 21 26 / .1) 0 40%, rgb(22 21 26 / .03) 50%, rgb(22 21 26 / .1) 60%);
  background-size: 240% 100%; animation: k-shimmer 1.6s linear infinite; }
.fx--spinner .subj { width: 20%; height: auto; aspect-ratio: 1; background: none; border: 3px solid rgb(22 21 26 / .18);
  border-top-color: var(--ink); border-radius: 50%; animation: k-spin 1s linear infinite; }
@keyframes k-progdet { 0% { width: 6% } 40% { width: 42% } 70% { width: 68% } 100% { width: 100% } }
.fx--progress-det .subj { animation: k-progdet 3.4s cubic-bezier(.4,0,.3,1) infinite; }
@keyframes k-toast { 0%,12% { opacity: 0; transform: translateY(120%) } 30%,72% { opacity: 1; transform: none } 90%,100% { opacity: 0; transform: translateY(120%) } }
.fx--toast .subj { position: absolute; right: 5%; bottom: 6%; width: 46%; padding: 2.6cqw;
  animation: k-toast 3.8s cubic-bezier(.3,.8,.3,1) infinite; }
@keyframes k-modal { 0%,14% { opacity: 0; transform: scale(.92) } 40%,86% { opacity: 1; transform: none } 100% { opacity: 0; transform: scale(.92) } }
@keyframes k-backdrop { 0%,14% { opacity: 0 } 40%,86% { opacity: 1 } 100% { opacity: 0 } }
.fx--modal .stage { position: relative; }
.fx--modal .subj { z-index: 1; animation: k-modal 3.6s cubic-bezier(.3,.8,.3,1) infinite; }
.fx--modal .subj::before { content: ""; position: fixed; inset: 0; }
.fx--modal::before { content: ""; position: absolute; inset: 0; background: rgb(22 21 26 / .34);
  backdrop-filter: blur(2px); animation: k-backdrop 3.6s ease-in-out infinite; }
.fx--checkmark .subj { stroke-dasharray: 100; animation: k-draw 3.4s cubic-bezier(.5,0,.3,1) infinite; }
.fx--checkmark .subj--tick { animation-delay: .35s; }
@keyframes k-err { 0%,60%,100% { border-color: transparent } 68% { transform: translateX(-6%) } 72% { transform: translateX(5%) } 76% { transform: translateX(-3%) } 80%,95% { border-color: var(--hot) } }
.fx--error-shake .subj { border: 2px solid transparent; animation: k-err 3.4s ease-in-out infinite; }
@keyframes k-confetti { 0% { transform: translate(0,0) rotate(0); opacity: 0 } 12% { opacity: 1 } 100% { transform: translate(var(--dx, 40%), 150%) rotate(220deg); opacity: 0 } }
.fx--confetti .s-dots { grid-template-columns: repeat(7, 1fr); }
.fx--confetti .subj { border-radius: 1px; opacity: 0; animation: k-confetti 2.4s cubic-bezier(.3,.6,.6,1) infinite; }
.fx--confetti .subj:nth-child(2n) { --dx: -40%; background: var(--hot); animation-delay: .2s }
.fx--confetti .subj:nth-child(3n) { --dx: 18%; background: var(--accent); animation-delay: .45s }
.fx--confetti .subj:nth-child(5n) { --dx: -12%; animation-delay: .7s }
@keyframes k-pull { 0%,10% { transform: translateY(-40%); opacity: 0 } 40%,64% { transform: translateY(28%); opacity: 1 } 92%,100% { transform: translateY(-40%); opacity: 0 } }
.fx--pull-refresh .subj { width: 14%; height: auto; aspect-ratio: 1; border-radius: 50%; background: none;
  border: 3px solid rgb(22 21 26 / .18); border-top-color: var(--ink);
  animation: k-pull 3.4s cubic-bezier(.3,.8,.3,1) infinite, k-spin 1s linear infinite; }

/* 98-105 loop ambientali */
@keyframes k-float { 0%,100% { transform: translateY(-6%) } 50% { transform: translateY(6%) } }
.fx--float .subj { animation: k-float 3.6s ease-in-out infinite; }
@keyframes k-pulse { 0%,100% { transform: scale(1); opacity: .9 } 50% { transform: scale(1.08); opacity: 1 } }
.fx--pulse .subj { border-radius: 50%; width: 24%; height: auto; aspect-ratio: 1; animation: k-pulse 2.2s ease-in-out infinite; }
.fx--pulse .subj::after { content: ""; position: absolute; inset: 0; border-radius: 50%; border: 2px solid var(--ink);
  animation: k-ripple 2.2s ease-out infinite; }
.fx--spin-slow .s-path svg { animation: k-spin 12s linear infinite; }
.fx--spin-slow .subj--tick { display: none; }
@keyframes k-wave { 0% { transform: translateX(0) } 100% { transform: translateX(-50%) } }
.fx--wave .s-path { width: 100%; }
.fx--wave circle { display: none; }
.fx--wave .subj--tick { stroke: var(--accent); stroke-width: 3;
  d: path("M-100 52 Q -87 38 -75 52 T -50 52 T -25 52 T 0 52 T 25 52 T 50 52 T 75 52 T 100 52 T 125 52 T 150 52 T 175 52 T 200 52");
  animation: k-wave 4s linear infinite; }
.fx--wave .s-path svg { overflow: hidden; }
.fx--wave .s-path::after { content: ""; position: absolute; left: 0; right: 0; top: 58%; bottom: -20%;
  background: rgb(47 93 80 / .16); }
@keyframes k-blobmorph { 0%,100% { border-radius: 46% 54% 40% 60% / 52% 44% 56% 48% } 33% { border-radius: 62% 38% 58% 42% / 40% 62% 38% 60% } 66% { border-radius: 38% 62% 46% 54% / 58% 36% 64% 42% } }
.fx--blob-morph .subj { filter: none; animation: k-blobmorph 6s ease-in-out infinite; }
.fx--gradient-shift .subj { width: 100%; height: 100%;
  background: linear-gradient(120deg, #3f5c68, #6d8a86 30%, #c2a878 60%, #8a5a3c); background-size: 260% 260%;
  animation: k-mesh 8s ease-in-out infinite alternate; }
@keyframes k-hint { 0%,100% { transform: translateY(-24%); opacity: .4 } 50% { transform: translateY(24%); opacity: 1 } }
.fx--scroll-hint .subj { width: 2px; height: 26%; background: var(--ink); animation: k-hint 1.8s ease-in-out infinite; }
.fx--rot-badge .s-path svg { animation: k-spin 14s linear infinite; }
.fx--rot-badge .subj--tick { display: none; }
.fx--rot-badge circle { stroke: var(--rule); stroke-width: 1.5; }
.fx--rot-badge .s-path__ring { display: block; fill: var(--accent); }
.fx--rot-badge .s-path::after { content: "↓"; position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%);
  font-size: 6cqw; color: var(--ink); }

/* 106-111 svg */
.fx--line-draw .subj { stroke-dasharray: 100; animation: k-draw 3.8s cubic-bezier(.5,0,.3,1) infinite; }
.fx--line-draw .subj--tick { animation-delay: .4s; }
@keyframes k-pathmorph { 0%,45% { d: path("M34 51 L46 63 L68 39") } 55%,100% { d: path("M34 44 L50 62 L68 44") } }
.fx--path-morph .subj--tick { animation: k-pathmorph 3s cubic-bezier(.5,0,.3,1) infinite; }
.fx--path-morph circle { animation: k-blobmorph 6s ease-in-out infinite; }
@keyframes k-fill-prog { 0% { clip-path: inset(100% 0 0 0) } 55%,80% { clip-path: inset(0 0 0 0) } 100% { clip-path: inset(100% 0 0 0) } }
.fx--fill-prog circle { fill: var(--accent); stroke: var(--ink); animation: k-fill-prog 3.6s cubic-bezier(.4,0,.3,1) infinite; }
.fx--fill-prog .subj--tick { stroke: var(--paper); }
@keyframes k-lottie { 0%,100% { transform: scale(1) rotate(0) } 30% { transform: scale(1.14) rotate(-6deg) } 60% { transform: scale(.94) rotate(5deg) } }
.fx--lottie .subj { border-radius: 12%; animation: k-lottie 2.6s cubic-bezier(.4,0,.3,1) infinite; }
@keyframes k-rive { 0%,40% { border-radius: 6%; background: var(--ink) } 55%,95% { border-radius: 50%; background: var(--accent) } 100% { border-radius: 6%; background: var(--ink) } }
.fx--rive .subj { animation: k-rive 3.4s cubic-bezier(.5,0,.3,1) infinite; }
@keyframes k-icon-hover { 0%,100% { transform: translateX(0) } 50% { transform: translateX(28%) } }
.fx--icon-hover .subj { position: relative; }
.fx--icon-hover em { display: none; }
.fx--icon-hover .subj::after { content: ""; position: absolute; left: 30%; top: calc(50% - 1px); width: 40%; height: 2px;
  background: var(--ink); animation: k-icon-hover 2.4s cubic-bezier(.5,0,.3,1) infinite; }
.fx--icon-hover .subj { width: 16cqw; aspect-ratio: 1; border: 1px solid var(--ink); padding: 0; }

/* 112-117 3d */
@keyframes k-cube { 0% { transform: rotateX(-14deg) rotateY(0) } 100% { transform: rotateX(-14deg) rotateY(360deg) } }
.fx--three-model .subj { animation: k-cube 7s linear infinite; }
@keyframes k-camera { 0% { transform: rotateX(-8deg) rotateY(-38deg) translateZ(-6cqw) } 100% { transform: rotateX(14deg) rotateY(38deg) translateZ(6cqw) } }
.fx--camera-scroll .subj { animation: k-camera 4s cubic-bezier(.4,0,.4,1) infinite alternate; }
@keyframes k-hoverdist { 0%,100% { transform: perspective(50cqw) rotateY(0) skewY(0) } 50% { transform: perspective(50cqw) rotateY(-11deg) skewY(1.6deg) } }
.fx--hover-distort .subj { animation: k-hoverdist 3.4s ease-in-out infinite; }
@keyframes k-disp { 0%,44% { opacity: 1; filter: blur(0) } 50% { opacity: .5; filter: blur(1.2cqw) } 56%,100% { opacity: 0; filter: blur(0) } }
.fx--displacement .s-photo { background: linear-gradient(150deg, #8a5a3c, #c2a878); }
.fx--displacement .subj { animation: k-disp 3.6s ease-in-out infinite alternate; }
@keyframes k-text3d { 0%,100% { transform: perspective(60cqw) rotateY(-13deg) rotateX(5deg) } 50% { transform: perspective(60cqw) rotateY(13deg) rotateX(-4deg) } }
.fx--text-3d .subj { animation: k-text3d 4s ease-in-out infinite; }
.fx--text-3d .s-scene b { background: rgb(47 93 80 / .34); }
@keyframes k-depth-a { 0%,100% { transform: perspective(60cqw) rotateY(-10deg) rotateX(5deg) } 50% { transform: perspective(60cqw) rotateY(10deg) rotateX(-5deg) } }
.fx--card-depth .subj { transform-style: preserve-3d; animation: k-depth-a 4s ease-in-out infinite; }
.fx--card-depth .s-card__ph { transform: translateZ(6cqw); }
.fx--card-depth b { transform: translateZ(11cqw); }
.fx--card-depth u { transform: translateZ(16cqw); }
"""


def _js() -> str:
    return """
(function () {
  var cards = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var q = document.getElementById('q');
  var count = document.getElementById('count');
  var empty = document.getElementById('empty');
  var tray = document.getElementById('tray');
  var picked = document.getElementById('picked');
  var active = { cat: null };
  var chosen = [];

  function apply() {
    var term = (q.value || '').trim().toLowerCase();
    var shown = 0;
    cards.forEach(function (c) {
      var ok = true;
      if (active.cat && c.dataset.cat !== active.cat) ok = false;
      if (ok && term && c.dataset.search.indexOf(term) === -1) ok = false;
      c.hidden = !ok;
      if (ok) shown++;
    });
    count.textContent = shown + ' / ' + cards.length + ' effetti';
    empty.hidden = shown !== 0;
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var g = chip.dataset.group, v = chip.dataset.value;
      var on = active[g] === v;
      active[g] = on ? null : v;
      chips.filter(function (o) { return o.dataset.group === g; })
           .forEach(function (o) { o.setAttribute('aria-pressed', String(!on && o === chip)); });
      apply();
    });
  });

  q.addEventListener('input', apply);

  document.getElementById('reset').addEventListener('click', function () {
    active = { cat: null };
    chips.forEach(function (o) { o.setAttribute('aria-pressed', 'false'); });
    q.value = '';
    apply();
  });

  var motion = document.getElementById('motion');
  motion.addEventListener('click', function () {
    var paused = document.body.classList.toggle('is-paused');
    motion.textContent = paused ? 'Riprendi' : 'Metti in pausa';
    motion.setAttribute('aria-pressed', String(paused));
  });

  function refreshTray() {
    tray.hidden = chosen.length === 0;
    picked.textContent = chosen.join(', ');
  }

  function toggle(card) {
    var id = card.dataset.id;
    var i = chosen.indexOf(id);
    if (i === -1) { chosen.push(id); card.setAttribute('aria-pressed', 'true'); }
    else { chosen.splice(i, 1); card.setAttribute('aria-pressed', 'false'); }
    refreshTray();
  }

  cards.forEach(function (card) {
    card.addEventListener('click', function () { toggle(card); });
    card.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(card); }
    });
  });

  Array.prototype.slice.call(document.querySelectorAll('[data-kit]')).forEach(function (btn) {
    btn.addEventListener('click', function () {
      var wanted = btn.dataset.kit.split(',');
      chosen = [];
      cards.forEach(function (c) {
        var on = wanted.indexOf(c.dataset.n) !== -1;
        c.setAttribute('aria-pressed', String(on));
        if (on) chosen.push(c.dataset.id);
      });
      refreshTray();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  document.getElementById('copy').addEventListener('click', function () {
    var text = chosen.join(', ');
    if (navigator.clipboard) navigator.clipboard.writeText(text);
    var b = document.getElementById('copy');
    b.textContent = 'Copiato';
    setTimeout(function () { b.textContent = 'Copia'; }, 1200);
  });

  document.getElementById('clear').addEventListener('click', function () {
    chosen = [];
    cards.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
    refreshTray();
  });

  apply();
})();
"""


# ------------------------------------------------------------------ cli


def main() -> int:
    p = argparse.ArgumentParser(description="Catalogo effetti — lista, scheda, kit, pagina.")
    p.add_argument("--filter", action="append", default=[], metavar="CHIAVE=VALORE")
    p.add_argument("--show", metavar="ID")
    p.add_argument("--kit", metavar="ID")
    p.add_argument("--suggest", type=int, metavar="N")
    p.add_argument("--seed", default="", help="seed YYYYMMDDHH per una shortlist deterministica")
    p.add_argument("--last", nargs="*", default=[], help="id/famiglie da escludere (anti-ripetizione)")
    p.add_argument("--build", action="store_true", help="scrive assets/effects-gallery.html")
    p.add_argument("--check", action="store_true", help="verifica che la pagina sia in sync")
    p.add_argument("--format", choices=("md", "json"), default="md")
    args = p.parse_args()

    catalog = load()
    effects = catalog["effects"]

    if args.build:
        PAGE.write_text(render_html(catalog), encoding="utf-8")
        print(f"effects gallery: {PAGE}  ({len(effects)} effetti)")
        print(f"apri con: open {PAGE}")
        return 0

    if args.check:
        if not PAGE.exists():
            print(f"manca {PAGE}: esegui --build")
            return 1
        if PAGE.read_text(encoding="utf-8") != render_html(catalog):
            print(f"{PAGE} non è in sync con effects-catalog.json: esegui --build")
            return 1
        print(f"ok: {PAGE} in sync con effects-catalog.json")
        return 0

    if args.show:
        found = [e for e in effects if e["id"] == args.show or str(e["n"]) == args.show]
        if not found:
            print(f"nessun effetto con id o numero '{args.show}'")
            return 1
        print(json.dumps(found[0], ensure_ascii=False, indent=2) if args.format == "json"
              else render_show(catalog, found[0]))
        return 0

    if args.kit:
        found = [k for k in catalog["kits"] if k["id"] == args.kit]
        if not found:
            ids = ", ".join(k["id"] for k in catalog["kits"])
            print(f"nessun kit '{args.kit}' — disponibili: {ids}")
            return 1
        print(json.dumps(found[0], ensure_ascii=False, indent=2) if args.format == "json"
              else render_kit(catalog, found[0]))
        return 0

    entries = [e for e in effects if match_filters(e, parse_filters(args.filter, catalog))]
    if args.suggest:
        entries = suggest(entries, args.suggest, args.seed or "no-seed", args.last)
    print(json.dumps(entries, ensure_ascii=False, indent=2) if args.format == "json"
          else render_list(catalog, entries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
