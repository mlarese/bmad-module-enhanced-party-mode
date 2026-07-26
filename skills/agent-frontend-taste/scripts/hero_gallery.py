#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Hero archetypes — visual chooser page + text lookup from assets/hero-catalog.json.

The catalog covers every hero case the skill can build: still · carousel · video ·
no-media (type/graphic) · collage · scroll sequence · product UI · map · before-after,
crossed with copy placement (left · right · center · bottom · top · split · rail) and
panel (solid plate · transparent · light wash · glass · band · single-edge gradient).

`--build` renders the chooser page: every archetype gets a thumbnail with a **real
photo** from `assets/hero-media/` and **real copy** (eyebrow, headline, subline, CTA),
so the owner reads the hero instead of decoding a wireframe. Local files only — no
network, no webfonts.

Usage:
    uv run scripts/hero_gallery.py                          # markdown list
    uv run scripts/hero_gallery.py --filter media=video     # filtered list
    uv run scripts/hero_gallery.py --show still-inset-frame
    uv run scripts/hero_gallery.py --suggest 6 --seed 2026072520 --last left-solid split
    uv run scripts/hero_gallery.py --build                  # write assets/hero-gallery.html
    uv run scripts/hero_gallery.py --check                  # page in sync with catalog?
    uv run scripts/hero_gallery.py --format json
"""

from __future__ import annotations

import argparse
import html
import json
import random
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CATALOG = ASSETS / "hero-catalog.json"
PAGE = ASSETS / "hero-gallery.html"

# Muted hue ring for washes and graphic fills — no purple-indigo (skill hard-reject).
HUES = [18, 32, 44, 66, 88, 128, 156, 172, 190, 206, 224, 348]

FIELDS = ("id", "name", "media", "treatment", "placement", "panel", "tone", "desc", "use", "watch")
COPY_FIELDS = ("eyebrow", "title", "sub", "cta")

MEDIA_AREAS = {
    "full",
    "half-left",
    "half-right",
    "half-fold",
    "inset",
    "inset-top",
    "inset-left",
    "top",
    "bottom",
    "window-right",
    "mask-arc",
    "arc-bottom",
    "circle",
    "corner",
    "frame",
    "angled",
    "portrait",
    "cutout",
    "tilt",
    "device-duo",
    "mosaic",
    "mosaic-right",
    "bento",
    "columns",
    "stack",
    "scatter",
    "strip-bottom",
    "strip-top",
    "compare",
    "compare-v",
    "none",
}

CHROME = {
    "dots",
    "dots-vertical",
    "arrows",
    "thumbs",
    "counter",
    "peek",
    "deck",
    "play",
    "progress",
    "frames",
    "marquee",
    "pin",
    "handle",
    "handle-v",
    "mask-type",
    "window",
    "rules",
    "mesh",
    "flat-brand",
    "duotone",
    "inserts",
    "loops",
    "scroll-cue",
    "vertical-label",
    "offset",
    # funzionali: la hero che deve far fare qualcosa
    "searchbar",
    "bookingbar",
    "stats",
    "logos",
    "quote",
    "price-list",
    "index-list",
    "form",
    "countdown",
    "badge",
    "avatars",
    # piani e texture
    "map-pins",
    "grain",
    "arc-type",
    "hover-cue",
    "steps",
}

# Chrome that paints its own plane — the only way a card can skip `media_area`.
PAINTS = {"mask-type", "rules", "mesh", "flat-brand", "inserts", "arc-type"}

# Chrome that sits beside the media instead of inside it (the media clips overflow).
# Anything spanning the whole hero — a search bar, a stat row, a logo wall — has to
# live outside the photo plane, or a half-width `media_area` would crop it.
OUTSIDE_MEDIA = {
    "vertical-label",
    "searchbar",
    "bookingbar",
    "stats",
    "logos",
    "quote",
    "price-list",
    "index-list",
    "form",
    "countdown",
    "badge",
    "avatars",
    "steps",
    "hover-cue",
}

# How many photo cells each multi-image plane draws.
CELLS = {
    "mosaic": 3,
    "mosaic-right": 4,
    "bento": 5,
    "columns": 3,
    "stack": 3,
    "scatter": 4,
    "device-duo": 2,
    "strip-bottom": 6,
    "strip-top": 5,
}


# ------------------------------------------------------------------ catalog


def load(path: Path = CATALOG) -> dict:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    validate(catalog)
    return catalog


def validate(catalog: dict, media_root: Path | None = None) -> None:
    """Fail loud on a catalog the renderer could only draw wrong."""
    axes = catalog["axes"]
    pool = catalog["media_pool"]
    root = media_root if media_root is not None else ASSETS / catalog["media_dir"]
    for key, media in pool.items():
        if media.get("kind") not in ("photo", "ui", "map"):
            raise SystemExit(f"media_pool['{key}']: kind '{media.get('kind')}' sconosciuto")
        if not (root / media["file"]).exists():
            raise SystemExit(f"media_pool['{key}']: file mancante {root / media['file']}")
        for f in COPY_FIELDS:
            if not media.get(f):
                raise SystemExit(f"media_pool['{key}']: manca il testo '{f}'")
    seen: set[str] = set()
    for a in catalog["archetypes"]:
        where = a.get("id", "<senza id>")
        missing = [f for f in FIELDS if not a.get(f)]
        if missing:
            raise SystemExit(f"{where}: campi mancanti {missing}")
        if a["id"] in seen:
            raise SystemExit(f"id duplicato: {a['id']}")
        seen.add(a["id"])
        for axis in ("media", "placement", "panel"):
            if a[axis] not in axes[axis]:
                raise SystemExit(f"{where}: {axis} '{a[axis]}' non è negli assi")
        if a["tone"] not in ("light", "dark"):
            raise SystemExit(f"{where}: tone '{a['tone']}' non valido")
        if "hero_copy" not in a:
            raise SystemExit(f"{where}: hero_copy assente (usa null se il placement è extra)")
        if "photo" not in a:
            raise SystemExit(f"{where}: photo assente (usa null se la hero non ha media)")
        if a["photo"] and a["photo"] not in pool:
            raise SystemExit(f"{where}: photo '{a['photo']}' non è nel media_pool")
        if not a["photo"] and not a.get("copy"):
            raise SystemExit(f"{where}: senza photo servono i testi in 'copy'")
        for f in COPY_FIELDS:
            if not copy_of(catalog, a).get(f):
                raise SystemExit(f"{where}: testo '{f}' vuoto — la miniatura resterebbe muta")
        if set(a["sketch"].get("copy_hide") or []) - set(COPY_FIELDS):
            raise SystemExit(f"{where}: copy_hide fuori dai campi di testo")
        if a["sketch"].get("title_scale") not in (None, "xl"):
            raise SystemExit(f"{where}: title_scale '{a['sketch']['title_scale']}' sconosciuto")
        if a["sketch"]["media_area"] not in MEDIA_AREAS:
            raise SystemExit(f"{where}: media_area '{a['sketch']['media_area']}' sconosciuta")
        for c in a["sketch"]["chrome"]:
            if c not in CHROME:
                raise SystemExit(f"{where}: chrome '{c}' sconosciuto")
        if a["sketch"]["media_area"] == "none" and not (set(a["sketch"]["chrome"]) & PAINTS):
            raise SystemExit(f"{where}: senza media_area serve un chrome che disegni il fondo")
        if a["sketch"]["media_area"] != "none" and not a["photo"]:
            raise SystemExit(f"{where}: media_area '{a['sketch']['media_area']}' senza foto")


def copy_of(catalog: dict, entry: dict) -> dict:
    """Real hero copy for a card: the photo's story, overridden per archetype."""
    base = dict(catalog["media_pool"].get(entry["photo"] or "", {}))
    base.update(entry.get("copy") or {})
    return {f: base.get(f, "") for f in COPY_FIELDS}


def match_filters(entry: dict, filters: list[tuple[str, str]]) -> bool:
    for key, value in filters:
        if str(entry.get(key, "")) != value:
            return False
    return True


def parse_filters(raw: list[str], catalog: dict | None = None) -> list[tuple[str, str]]:
    """Parse `key=value` filters, refusing keys and values the catalog does not have.

    Without the check a typo is indistinguishable from an honest empty result:
    `--filter mdia=still` and `--filter media=nonesiste` both printed zero rows
    and said nothing, so you read "no archetype matches" instead of "you typed it
    wrong". Silence on a typo is the worst of the three outcomes.
    """
    out: list[tuple[str, str]] = []
    seen: dict[str, set[str]] = {}
    if catalog:
        for entry in catalog["archetypes"]:
            for k, v in entry.items():
                if isinstance(v, str):
                    seen.setdefault(k, set()).add(v)
    # Only categorical fields are worth filtering on: `desc` and `watch` are free
    # text, one value per archetype, so offering them as filter keys is noise.
    fields = {k: v for k, v in seen.items() if len(v) <= 20}

    for item in raw:
        if "=" not in item:
            raise SystemExit(f"filtro non valido: {item} (usa chiave=valore, es. media=video)")
        key, _, value = item.partition("=")
        key, value = key.strip(), value.strip()
        if fields:
            if key not in fields:
                raise SystemExit(
                    f"filtro: chiave sconosciuta `{key}`. "
                    f"Disponibili: {', '.join(sorted(fields))}"
                )
            if value not in fields[key]:
                known = ", ".join(sorted(fields[key]))
                raise SystemExit(
                    f"filtro: `{key}` non ha il valore `{value}`. Valori reali: {known}"
                )
        out.append((key, value))
    return out


def suggest(archetypes: list[dict], n: int, seed: str, last: list[str]) -> list[dict]:
    """Deterministic shortlist per seed, diverse on media + placement, MEMORY-aware."""
    dropped = {v.strip() for v in last if v.strip()}
    pool = [
        a
        for a in archetypes
        if not dropped & {a["id"], a["treatment"], a.get("hero_copy") or "", a["media"]}
    ]
    if not pool:
        pool = list(archetypes)
    rng = random.Random(f"{seed}|hero-gallery")
    rng.shuffle(pool)
    picked: list[dict] = []
    seen_media: set[str] = set()
    seen_place: set[str] = set()
    for strict in (True, False):
        for a in pool:
            if len(picked) >= n:
                break
            if a in picked:
                continue
            if strict and (a["media"] in seen_media or a["placement"] in seen_place):
                continue
            picked.append(a)
            seen_media.add(a["media"])
            seen_place.add(a["placement"])
    return picked[:n]


# ------------------------------------------------------------------ text out


def render_list(catalog: dict, entries: list[dict]) -> str:
    axes = catalog["axes"]
    lines = [
        "# Hero archetypes",
        "",
        f"Catalogo: `assets/hero-catalog.json` · pagina: `assets/hero-gallery.html` "
        f"({len(catalog['archetypes'])} archetipi, {len(entries)} elencati)",
        "",
        "| id | Nome | Media | Testo | Pannello | hero_copy |",
        "|---|---|---|---|---|---|",
    ]
    for a in entries:
        lines.append(
            f"| `{a['id']}` | {a['name']} | {axes['media'][a['media']]['label']} | "
            f"{axes['placement'][a['placement']]['label']} | {axes['panel'][a['panel']]['label']} | "
            f"{'`' + a['hero_copy'] + '`' if a.get('hero_copy') else '—'} |"
        )
    lines += [
        "",
        "Scegli tu il primo che regge dominio e `register` (`--show <id>` per assi e "
        "vincoli): la shortlist è deterministica dal seed e non si sottopone all'owner. "
        "La pagina a vista (`--build` → `open`) solo se l'owner la chiede.",
    ]
    return "\n".join(lines)


def render_show(catalog: dict, entry: dict) -> str:
    axes = catalog["axes"]
    c = copy_of(catalog, entry)
    return "\n".join(
        [
            f"# {entry['name']}  (`{entry['id']}`)",
            "",
            entry["desc"],
            "",
            f"- **Media:** {axes['media'][entry['media']]['label']} (`{entry['media']}`) — {axes['media'][entry['media']]['note']}",
            f"- **hero_treatment:** `{entry['treatment']}`",
            f"- **Testo:** {axes['placement'][entry['placement']]['label']} (`{entry['placement']}`)",
            f"- **Pannello:** {axes['panel'][entry['panel']]['label']} (`{entry['panel']}`) — {axes['panel'][entry['panel']]['note']}",
            f"- **hero_copy:** {entry['hero_copy'] or '— (placement fuori dalle 6 etichette: dichiara id + placement + panel)'}",
            f"- **Quando:** {entry['use']}",
            f"- **Attenzione:** {entry['watch']}",
            "",
            f"Esempio in miniatura: «{c['title']}» — {c['eyebrow']} · CTA «{c['cta']}»",
        ]
    )


# ------------------------------------------------------------------ HTML out


def _img(catalog: dict, key: str, extra: str = "") -> str:
    media = catalog["media_pool"][key]
    src = f"{catalog['media_dir']}/{media['file']}"
    cls = f' class="{extra}"' if extra else ""
    return f'<img{cls} src="{html.escape(src)}" alt="" loading="lazy" decoding="async">'


def _rotate(catalog: dict, start: str, n: int) -> list[str]:
    """Photo keys for a multi-cell plane: start at the archetype's photo, then walk the pool.

    Only generic photos rotate — a map or a product screenshot is not a spare slide —
    but the archetype's own media always leads, or a UI hero would open on a landscape.
    """
    keys = [k for k, m in catalog["media_pool"].items() if m["kind"] == "photo"]
    if start not in keys:
        # A screenshot or a map has no sibling slides: repeat it rather than
        # drop a landscape into the second device.
        return [start] * n
    i = keys.index(start)
    return [keys[(i + k) % len(keys)] for k in range(n)]


def _facing(entry: dict) -> str:
    """Which side a full-height block takes: always opposite the copy."""
    return "left" if entry["placement"] == "right" else "right"


def _chrome_html(chrome: list[str], entry: dict, catalog: dict) -> str:
    photo = entry["photo"]
    parts: list[str] = []
    for c in chrome:
        if c == "dots":
            parts.append('<span class="ui-dots"><i></i><i></i><i></i><i></i></span>')
        elif c == "dots-vertical":
            parts.append('<span class="ui-dots ui-dots--v"><i></i><i></i><i></i><i></i></span>')
        elif c == "arrows":
            parts.append('<span class="ui-arrow ui-arrow--l"></span><span class="ui-arrow ui-arrow--r"></span>')
        elif c == "thumbs":
            cells = "".join(f"<i>{_img(catalog, k)}</i>" for k in _rotate(catalog, photo, 3))
            side = "left" if entry["placement"] == "right" else "right"
            parts.append(f'<span class="ui-thumbs ui-thumbs--{side}">{cells}</span>')
        elif c == "counter":
            parts.append('<span class="ui-counter">01/04</span>')
        elif c == "peek":
            nxt = _rotate(catalog, photo, 2)[1]
            parts.append(f'<span class="ui-peek">{_img(catalog, nxt)}</span>')
        elif c == "deck":
            parts.append('<span class="ui-deck ui-deck--2"></span><span class="ui-deck ui-deck--1"></span>')
        elif c == "play":
            parts.append('<span class="ui-play"></span>')
        elif c == "progress":
            parts.append('<span class="ui-progress"><i></i></span>')
        elif c == "frames":
            cells = "".join(f"<i>{_img(catalog, k)}</i>" for k in _rotate(catalog, photo, 3))
            parts.append(f'<span class="ui-frames">{cells}</span>')
        elif c == "marquee":
            parts.append('<span class="ui-marquee"></span>')
        elif c == "pin":
            parts.append('<span class="ui-pin"></span>')
        elif c == "handle":
            parts.append('<span class="ui-handle"></span>')
        elif c == "mask-type":
            word = html.escape(copy_of(catalog, entry)["title"])
            src = f"{catalog['media_dir']}/{catalog['media_pool'][photo]['file']}"
            parts.append(f'<span class="ui-masktype" style="background-image:url(\'{html.escape(src)}\')">{word}</span>')
        elif c == "window":
            parts.append('<span class="ui-winbar"><i></i><i></i><i></i></span>')
        elif c == "rules":
            parts.append('<span class="ui-rules"></span>')
        elif c == "mesh":
            parts.append('<span class="ui-mesh"></span>')
        elif c == "flat-brand":
            parts.append('<span class="ui-flat"></span>')
        elif c == "duotone":
            parts.append('<span class="ui-duotone"></span>')
        elif c == "inserts":
            cells = "".join(f"<i>{_img(catalog, k)}</i>" for k in _rotate(catalog, photo, 2))
            parts.append(f'<span class="ui-inserts">{cells}</span>')
        elif c == "loops":
            parts.append('<span class="ui-loops">3 loop</span>')
        elif c == "scroll-cue":
            parts.append('<span class="ui-cue"></span>')
        elif c == "vertical-label":
            parts.append('<span class="ui-vlabel">Positano · 1964</span>')
        elif c == "offset":
            pass  # handled by the copy block class
        elif c == "handle-v":
            parts.append('<span class="ui-handle ui-handle--v"></span>')
        elif c == "searchbar":
            parts.append(
                '<span class="ui-bar ui-bar--search">'
                '<i class="f">Dove vuoi andare</i><b>Cerca</b></span>'
            )
        elif c == "bookingbar":
            parts.append(
                '<span class="ui-bar ui-bar--booking">'
                '<i class="f">Arrivo</i><i class="f">Partenza</i><i class="f">2 ospiti</i>'
                "<b>Verifica</b></span>"
            )
        elif c == "stats":
            cells = "".join(
                f'<i><b>{n}</b><em>{lab}</em></i>'
                for n, lab in (("12", "stanze"), ("1964", "dal"), ("4.9", "recensioni"))
            )
            parts.append(f'<span class="ui-stats">{cells}</span>')
        elif c == "logos":
            parts.append("<span class=\"ui-logos\">" + "<i></i>" * 5 + "</span>")
        elif c == "quote":
            parts.append(
                f'<span class="ui-quote ui-side--{_facing(entry)}"><b>&ldquo;</b>'
                f'<em>{html.escape(copy_of(catalog, entry)["sub"])}</em>'
                "<span>Gambero Rosso</span></span>"
            )
        elif c == "price-list":
            rows = "".join(
                f"<i><em>{html.escape(n)}</em><b>{p}</b></i>"
                for n, p in (("Crudo del giorno", "24"), ("Spaghetti al riccio", "22"), ("Sorbetto al cedro", "9"))
            )
            parts.append(f'<span class="ui-prices ui-side--{_facing(entry)}">{rows}</span>')
        elif c == "index-list":
            rows = "".join(
                f"<i><em>{n}</em>{html.escape(t)}</i>"
                for n, t in (("01", "Le stanze"), ("02", "La cucina"), ("03", "Il giardino"))
            )
            parts.append(f'<span class="ui-index ui-side--{_facing(entry)}">{rows}</span>')
        elif c == "form":
            parts.append('<span class="ui-bar ui-bar--form"><i class="f">La tua email</i><b>Iscriviti</b></span>')
        elif c == "countdown":
            cells = "".join(
                f"<i><b>{v}</b><em>{lab}</em></i>"
                for v, lab in (("04", "giorni"), ("11", "ore"), ("38", "min"))
            )
            parts.append(f'<span class="ui-count">{cells}</span>')
        elif c == "badge":
            parts.append('<span class="ui-badge"><b>2026</b><em>Guida Michelin</em></span>')
        elif c == "avatars":
            parts.append(
                '<span class="ui-avatars">'
                + "".join(f'<i>{_img(catalog, k)}</i>' for k in _rotate(catalog, photo, 3))
                + "<em>+2.400 ospiti</em></span>"
            )
        elif c == "map-pins":
            parts.append(
                '<span class="ui-pins">'
                '<i class="p1"></i><i class="p2"></i><i class="p3"></i></span>'
            )
        elif c == "grain":
            parts.append('<span class="ui-grain"></span>')
        elif c == "arc-type":
            word = html.escape(copy_of(catalog, entry)["eyebrow"])
            parts.append(
                '<span class="ui-arc"><svg viewBox="0 0 100 100" aria-hidden="true">'
                '<defs><path id="arc" d="M 12,64 A 38,38 0 0 1 88,64"/></defs>'
                f'<text><textPath href="#arc" startOffset="50%">{word}</textPath></text>'
                "</svg></span>"
            )
        elif c == "hover-cue":
            parts.append('<span class="ui-hovercue">passa il mouse</span>')
        elif c == "steps":
            cells = "".join(f"<i>{n}</i>" for n in ("01", "02", "03"))
            parts.append(f'<span class="ui-steps">{cells}</span>')
        else:
            raise SystemExit(f"{entry['id']}: chrome sconosciuto '{c}'")
    return "".join(parts)


def _media_html(entry: dict, catalog: dict, chrome_markup: str) -> str:
    area = entry["sketch"]["media_area"]
    photo = entry["photo"]
    if area == "none":
        return chrome_markup
    if area in CELLS:
        keys = _rotate(catalog, photo, CELLS[area])
        cells = "".join(
            f'<i class="ph ph--cell ph--cell{i}">{_img(catalog, k)}</i>'
            for i, k in enumerate(keys, 1)
        )
        return f'<span class="plane plane--{area}">{cells}{chrome_markup}</span>'
    if area in ("compare", "compare-v"):
        img = _img(catalog, photo)
        return (
            f'<span class="plane plane--{area}">'
            f'<i class="ph ph--compare-a">{img}</i><i class="ph ph--compare-b">{img}</i>'
            f"{chrome_markup}</span>"
        )
    return f'<span class="ph ph--{area}">{_img(catalog, photo)}{chrome_markup}</span>'


def _copy_html(entry: dict, catalog: dict) -> str:
    e = html.escape
    c = copy_of(catalog, entry)
    classes = ["copy", f"copy--{entry['sketch'].get('copy_shift') or entry['placement']}"]
    if entry["sketch"].get("title_scale") == "xl":
        classes.append("copy--xl")
    classes.append(f"panel--{entry['panel']}")
    classes.append(f"tone--{entry['tone']}")
    if entry["panel"] == "transparent" and entry["photo"] and entry["sketch"]["media_area"] != "none":
        classes.append("on-photo")
    if "offset" in entry["sketch"]["chrome"]:
        classes.append("copy--is-offset")
    hide = set(entry["sketch"].get("copy_hide") or [])
    parts = {
        "eyebrow": f'<span class="c-eyebrow">{e(c["eyebrow"])}</span>',
        "title": f'<span class="c-title">{e(c["title"])}</span>',
        "sub": f'<span class="c-sub">{e(c["sub"])}</span>',
        "cta": f'<span class="c-cta">{e(c["cta"])}</span>',
    }
    for k in hide:
        parts[k] = ""
    if entry["placement"] == "split":
        return (
            f'<span class="{" ".join(classes)}">'
            f'<span class="pole">{parts["eyebrow"]}{parts["title"]}</span>'
            f'<span class="pole pole--b">{parts["sub"]}{parts["cta"]}</span>'
            "</span>"
        )
    return f'<span class="{" ".join(classes)}">{"".join(parts.values())}</span>'


def render_card(entry: dict, catalog: dict, index: int) -> str:
    e = html.escape
    axes = catalog["axes"]
    hue = HUES[index % len(HUES)]
    inside, outside = _split_chrome(entry["sketch"]["chrome"])
    chrome = _chrome_html(inside, entry, catalog)
    loose = _chrome_html(outside, entry, catalog)
    edge = (
        f'<span class="edge edge--{entry["placement"]}"></span>'
        if entry["panel"] == "gradient-edge"
        else ""
    )
    wash = '<span class="wash"></span>' if entry["panel"] == "wash" else ""
    c = copy_of(catalog, entry)
    haystack = " ".join(
        [
            entry["id"],
            entry["name"],
            entry["desc"],
            entry["use"],
            entry["watch"],
            axes["media"][entry["media"]]["label"],
            axes["placement"][entry["placement"]]["label"],
            axes["panel"][entry["panel"]]["label"],
            entry["treatment"],
            entry.get("hero_copy") or "",
            c["title"],
        ]
    ).lower()
    return f"""      <article class="card" tabindex="0" role="button" aria-pressed="false"
        data-id="{e(entry['id'])}" data-media="{e(entry['media'])}"
        data-placement="{e(entry['placement'])}" data-panel="{e(entry['panel'])}"
        data-search="{e(haystack)}" style="--h: {hue}">
        <span class="thumb" aria-hidden="true">{_media_html(entry, catalog, chrome)}{loose}{wash}{edge}{_copy_html(entry, catalog)}</span>
        <div class="body">
          <p class="eyebrow"><code>{e(entry['id'])}</code></p>
          <h3>{e(entry['name'])}</h3>
          <p class="desc">{e(entry['desc'])}</p>
          <ul class="tokens">
            <li>{e(axes['media'][entry['media']]['label'])}</li>
            <li>{e(axes['placement'][entry['placement']]['label'])}</li>
            <li>{e(axes['panel'][entry['panel']]['label'])}</li>
            <li><code>{e(entry['treatment'])}</code></li>
            <li>{('<code>' + e(entry['hero_copy']) + '</code>') if entry.get('hero_copy') else 'placement extra'}</li>
          </ul>
          <dl class="notes">
            <dt>Quando</dt><dd>{e(entry['use'])}</dd>
            <dt>Attenzione</dt><dd>{e(entry['watch'])}</dd>
          </dl>
        </div>
      </article>
"""


def _split_chrome(chrome: list[str]) -> tuple[list[str], list[str]]:
    inside = [c for c in chrome if c not in OUTSIDE_MEDIA]
    outside = [c for c in chrome if c in OUTSIDE_MEDIA]
    return inside, outside


def _chip_group(name: str, label: str, values: dict[str, dict], used: set[str]) -> str:
    chips = "".join(
        f'<button type="button" class="chip" data-group="{name}" data-value="{html.escape(k)}" '
        f'title="{html.escape(v["note"])}" aria-pressed="false">{html.escape(v["label"])}</button>'
        for k, v in values.items()
        if k in used
    )
    return f'<div class="chips" role="group" aria-label="{label}"><span class="chips__label">{label}</span>{chips}</div>'


def _legend(axes: dict) -> str:
    blocks = []
    for name, title in (("media", "Media"), ("placement", "Testo"), ("panel", "Pannello")):
        items = "".join(
            f"<dt><code>{html.escape(k)}</code> {html.escape(v['label'])}</dt>"
            f"<dd>{html.escape(v['note'])}</dd>"
            for k, v in axes[name].items()
        )
        blocks.append(f'<div><h3>{title}</h3><dl>{items}</dl></div>')
    return f'<section class="legend"><h2>I tre assi</h2><div class="legend__cols">{"".join(blocks)}</div></section>'


def _credits(catalog: dict) -> str:
    sources = sorted({m["credit"] for m in catalog["media_pool"].values()})
    return (
        '<footer class="credits"><p>Foto e testi delle miniature sono campioni di lavoro: '
        f'{html.escape(" · ".join(sources))}. Marchi e copy sono inventati per far leggere lo schema — '
        "colore, font e palette del progetto reale restano derivati da località + carattere + business.</p></footer>"
    )


def render_html(catalog: dict) -> str:
    axes = catalog["axes"]
    archetypes = catalog["archetypes"]
    cards = "".join(render_card(a, catalog, i) for i, a in enumerate(archetypes))
    filters = "".join(
        [
            _chip_group("media", "Media", axes["media"], {a["media"] for a in archetypes}),
            _chip_group(
                "placement", "Testo", axes["placement"], {a["placement"] for a in archetypes}
            ),
            _chip_group("panel", "Pannello", axes["panel"], {a["panel"] for a in archetypes}),
        ]
    )
    return f"""<!DOCTYPE html>
<html lang="it" data-generated-by="hero_gallery.py">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hero archetypes — scelta a vista</title>
<style>
:root {{
  --paper: #f3f0ea;
  --paper-2: #e9e4da;
  --ink: #171613;
  --ink-2: #4a463f;
  --rule: #c9c2b4;
  --accent: #8a3f1d;
  --plate: #14120f;
  --r-box: 3px;
  --mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}}
* {{ box-sizing: border-box; }}
html {{ -webkit-text-size-adjust: 100%; }}
body {{
  margin: 0; background: var(--paper); color: var(--ink);
  font-family: var(--sans); line-height: 1.5;
  background-image: repeating-linear-gradient(180deg, transparent 0 27px, rgba(23,22,19,.045) 27px 28px);
}}
code {{ font-family: var(--mono); font-size: .82em; }}

/* ------------------------------------------------------------- masthead */
header.masthead {{ padding: clamp(1.5rem, 4vw, 3.5rem) clamp(1rem, 4vw, 3rem) 1.25rem; border-bottom: 1px solid var(--rule); }}
.kicker {{ font-family: var(--mono); font-size: .7rem; letter-spacing: .16em; text-transform: uppercase; color: var(--ink-2); margin: 0 0 .75rem; }}
h1 {{ font-family: var(--serif); font-weight: 500; font-size: clamp(2rem, 5.5vw, 3.4rem); line-height: .95; letter-spacing: -.035em; margin: 0 0 .6rem; max-width: 22ch; text-wrap: balance; }}
.lede {{ margin: 0; max-width: 64ch; color: var(--ink-2); text-wrap: pretty; }}
.lede + .lede {{ margin-top: .5rem; }}

/* --------------------------------------------------------------- toolbar */
.toolbar {{ position: sticky; top: 0; z-index: 5; background: color-mix(in srgb, var(--paper) 92%, transparent); backdrop-filter: blur(6px); border-bottom: 1px solid var(--rule); padding: .75rem clamp(1rem, 4vw, 3rem); display: flex; flex-wrap: wrap; gap: .75rem 1.5rem; align-items: center; }}
.chips {{ display: flex; flex-wrap: wrap; gap: .3rem; align-items: center; }}
.chips__label {{ font-family: var(--mono); font-size: .66rem; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-2); margin-right: .3rem; }}
.chip, .btn {{ font: inherit; font-size: .8rem; padding: .3rem .6rem; border: 1px solid var(--rule); border-radius: var(--r-box); background: transparent; color: var(--ink-2); cursor: pointer; min-height: 34px; }}
.chip[aria-pressed="true"] {{ background: var(--ink); border-color: var(--ink); color: var(--paper); }}
.chip:focus-visible, .btn:focus-visible, .card:focus-visible, input:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.search {{ flex: 1 1 12rem; min-width: 9rem; }}
.search input {{ width: 100%; font: inherit; font-size: .85rem; padding: .4rem .6rem; border: 1px solid var(--rule); border-radius: var(--r-box); background: var(--paper); color: var(--ink); min-height: 34px; }}
.count {{ font-family: var(--mono); font-size: .72rem; color: var(--ink-2); white-space: nowrap; }}

/* ----------------------------------------------------------------- grid */
main {{ padding: 1.5rem clamp(1rem, 4vw, 3rem) 6rem; }}
.grid {{ display: grid; gap: 1px; grid-template-columns: repeat(auto-fill, minmax(min(100%, 25rem), 1fr)); background: var(--rule); border: 1px solid var(--rule); }}
.card {{ background: var(--paper); padding: 1rem; display: flex; flex-direction: column; gap: .75rem; cursor: pointer; }}
.card[aria-pressed="true"] {{ background: var(--paper-2); box-shadow: inset 3px 0 0 var(--accent); }}
.card .eyebrow {{ margin: 0; font-family: var(--mono); font-size: .68rem; letter-spacing: .06em; color: var(--ink-2); }}
.card h3 {{ font-family: var(--serif); font-weight: 500; font-size: 1.18rem; line-height: 1.15; letter-spacing: -.02em; margin: 0; }}
.card .desc {{ margin: 0; font-size: .88rem; color: var(--ink-2); max-width: 52ch; text-wrap: pretty; }}
.tokens {{ list-style: none; display: flex; flex-wrap: wrap; gap: .25rem; margin: 0; padding: 0; }}
.tokens li {{ font-family: var(--mono); font-size: .64rem; letter-spacing: .04em; text-transform: uppercase; padding: .15rem .38rem; border: 1px dashed var(--rule); color: var(--ink-2); }}
.notes {{ margin: 0; display: grid; grid-template-columns: max-content 1fr; gap: .15rem .6rem; font-size: .8rem; }}
.notes dt {{ font-family: var(--mono); font-size: .62rem; letter-spacing: .12em; text-transform: uppercase; color: var(--accent); padding-top: .12rem; }}
.notes dd {{ margin: 0; color: var(--ink-2); }}
.card[hidden] {{ display: none; }}

/* ---------------------------------------------------------- thumbnails */
.thumb {{ position: relative; display: block; aspect-ratio: 16 / 9; overflow: hidden; background: var(--paper-2); border: 1px solid var(--rule); container-type: inline-size; }}
.ph, .plane {{ position: absolute; overflow: hidden; }}
.ph img, .ui-peek img, .ui-thumbs img, .ui-frames img, .ui-inserts img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.ph--full {{ inset: 0; }}
.ph--half-left {{ inset: 0 45% 0 0; }}
.ph--half-right {{ inset: 0 0 0 45%; }}
.ph--inset {{ inset: 12% 10%; }}
.ph--inset-top {{ inset: 6% 7% 44% 7%; }}
.ph--inset-left {{ inset: 10% 46% 10% 7%; }}
.ph--top {{ inset: 0 0 44% 0; }}
.ph--bottom {{ inset: 50% 0 0 0; }}
.ph--window-right {{ inset: 13% 5% 13% 44%; box-shadow: 0 0 0 1px rgb(255 255 255 / .5); }}
.ph--mask-arc {{ inset: 6% 7% 6% 46%; border-radius: 46% 46% 5% 5% / 40% 40% 4% 4%; }}
.ph--half-fold {{ inset: 0; background: hsl(var(--h) 28% 84%); }}
.ph--half-fold img {{ right: 50%; width: 50%; }}
.ph--circle {{ inset: 7% 6% 7% 54%; border-radius: 50%; }}
.ph--corner {{ inset: 42% 4% 6% 60%; box-shadow: 0 0 0 1px rgb(255 255 255 / .5); }}
.ph--frame {{ inset: 7% 6%; box-shadow: inset 0 0 0 1.6cqw var(--paper), inset 0 0 0 1.9cqw rgb(23 22 19 / .22); }}
.ph--angled {{ inset: 0; clip-path: polygon(0 0, 55% 0, 33% 100%, 0 100%); }}
.ph--portrait {{ inset: 5% 7% 5% 63%; }}
.ph--cutout {{ inset: 0; background:
  radial-gradient(ellipse 62% 52% at 72% 54%, hsl(var(--h) 38% 82%), hsl(var(--h) 26% 90%) 70%); }}
.ph--cutout img {{ inset: 9% 9% 9% 50%; clip-path: ellipse(44% 47% at 50% 50%); }}
.ph--tilt {{ inset: 13% -8% 7% 44%; transform: perspective(70cqw) rotateY(-17deg) rotateX(5deg);
  box-shadow: -1cqw 1.4cqw 3cqw rgb(0 0 0 / .3); }}
.ph--arc-bottom {{ inset: 30% 4% 0 4%; border-radius: 50% 50% 0 0 / 34% 34% 0 0; }}
.plane--mosaic {{ inset: 0; display: grid; grid-template-columns: 1.45fr 1fr; grid-template-rows: 1fr 1fr; gap: 3px; }}
.plane--mosaic .ph--cell1 {{ grid-row: span 2; }}
.plane--mosaic-right {{ inset: 5% 5% 5% 43%; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 4px; }}
.plane--bento {{ inset: 4%; display: grid; grid-template-columns: 1.6fr 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 1.2cqw; }}
.plane--bento .ph--cell1 {{ grid-row: span 2; }}
.plane--bento .ph--cell4 {{ grid-column: span 2; }}
.plane--columns {{ inset: 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.4cqw; }}
.plane--columns .ph--cell1 {{ margin-bottom: 14%; }}
.plane--columns .ph--cell2 {{ margin-top: 9%; }}
.plane--columns .ph--cell3 {{ margin-bottom: 20%; }}
.plane--stack {{ inset: 6% 5% 6% 52%; }}
.plane--stack .ph--cell {{ position: absolute; inset: 6% 8%; box-shadow: 0 .6cqw 2cqw rgb(0 0 0 / .3); border: .9cqw solid var(--paper); }}
.plane--stack .ph--cell1 {{ transform: rotate(-7deg) translate(-6%, 4%); }}
.plane--stack .ph--cell2 {{ transform: rotate(4deg) translate(5%, -2%); }}
.plane--stack .ph--cell3 {{ transform: rotate(-1deg); }}
.plane--scatter {{ inset: 0; }}
.plane--scatter .ph--cell {{ position: absolute; box-shadow: 0 .5cqw 1.8cqw rgb(0 0 0 / .26); }}
.plane--scatter .ph--cell1 {{ inset: 8% 58% 42% 6%; transform: rotate(-4deg); }}
.plane--scatter .ph--cell2 {{ inset: 14% 12% 34% 62%; transform: rotate(3deg); }}
.plane--scatter .ph--cell3 {{ inset: 56% 66% 8% 8%; transform: rotate(2deg); }}
.plane--scatter .ph--cell4 {{ inset: 62% 18% 6% 48%; transform: rotate(-3deg); }}
.plane--device-duo {{ inset: 10% 6% 0 40%; }}
.plane--device-duo .ph--cell {{ position: absolute; }}
.plane--device-duo .ph--cell1 {{ inset: 0 8% 14% 0; box-shadow: 0 1cqw 2.4cqw rgb(0 0 0 / .28); border: .7cqw solid #1b1a17; border-radius: .6cqw; }}
.plane--device-duo .ph--cell2 {{ inset: 26% 0 0 62%; box-shadow: 0 1cqw 2cqw rgb(0 0 0 / .32); border: .7cqw solid #1b1a17; border-radius: 1.6cqw; }}
.plane--strip-bottom {{ inset: auto 0 7% 0; height: 44%; display: flex; gap: 4px; padding: 0 5%; }}
.plane--strip-bottom .ph--cell {{ flex: 1 0 23%; }}
.plane--strip-top {{ inset: 5% 0 auto 0; height: 42%; display: flex; gap: 4px; padding: 0 5%; }}
.plane--strip-top .ph--cell {{ flex: 1 0 18%; }}
.plane--compare {{ inset: 36% 0 0 0; }}
.plane--compare-v {{ inset: 0 0 0 46%; }}
.plane--compare-v .ph--compare-a {{ inset: 0 0 50% 0; }}
.plane--compare-v .ph--compare-b {{ inset: 50% 0 0 0; }}
.ph--compare-a {{ inset: 0 50% 0 0; }}
.ph--compare-b {{ inset: 0 0 0 50%; }}
.ph--compare-b img {{ filter: grayscale(1) contrast(.82) brightness(1.1); }}
.ph--cell {{ position: relative; overflow: hidden; }}
.wash {{ position: absolute; inset: 0; background: hsl(var(--h) 40% 94% / .8); }}
.edge {{ position: absolute; }}
.edge--left {{ inset: 0 58% 0 0; background: linear-gradient(90deg, rgb(10 9 8 / .9), rgb(10 9 8 / .5) 55%, transparent); }}
.edge--right {{ inset: 0 0 0 58%; background: linear-gradient(270deg, rgb(10 9 8 / .9), rgb(10 9 8 / .5) 55%, transparent); }}
.edge--bottom, .edge--bottom-left {{ inset: 45% 0 0 0; background: linear-gradient(0deg, rgb(10 9 8 / .92), rgb(10 9 8 / .45) 55%, transparent); }}

/* ------------------------------------------------- copy: testo davvero */
.copy {{ position: absolute; display: flex; flex-direction: column; gap: 2.2cqw; width: 44%; padding: 3.4cqw; }}
.copy--left {{ left: 0; top: 50%; transform: translateY(-50%); }}
.copy--right {{ right: 0; top: 50%; transform: translateY(-50%); }}
.copy--center {{ left: 50%; top: 50%; transform: translate(-50%, -50%); width: 62%; align-items: center; text-align: center; }}
.copy--center-top {{ left: 50%; top: 4%; transform: translateX(-50%); width: 64%; align-items: center; text-align: center; }}
.copy--bottom-left {{ left: 0; bottom: 0; width: 52%; }}
.copy--bottom {{ left: 50%; bottom: 0; transform: translateX(-50%); width: 64%; align-items: center; text-align: center; }}
.copy--top {{ left: 0; top: 0; width: 64%; }}
.copy--rail {{ left: 0; top: 0; bottom: 0; width: 34%; padding-left: 12%; justify-content: flex-end; }}
.copy--split {{ left: 0; right: 0; bottom: 0; width: auto; flex-direction: row; align-items: flex-end; justify-content: space-between; gap: 4cqw; }}
.copy--is-offset {{ right: 4%; width: 48%; }}
.pole {{ display: flex; flex-direction: column; gap: 2cqw; width: 46%; }}
.pole--b {{ align-items: flex-start; }}
.panel--solid {{ background: var(--plate); }}
.panel--band {{ left: 0; right: 0; width: auto; padding: 3.4cqw 9%; transform: translateY(-50%); background: var(--plate); }}
.panel--glass {{ background: rgb(255 255 255 / .66); box-shadow: inset 0 0 0 1px rgb(255 255 255 / .7); backdrop-filter: blur(4px); }}
.c-eyebrow {{ font-family: var(--mono); font-size: 1.9cqw; letter-spacing: .15em; text-transform: uppercase; opacity: .82; }}
.c-title {{ font-family: var(--serif); font-size: 5.4cqw; line-height: .98; letter-spacing: -.03em; text-wrap: balance; }}
.c-sub {{ font-size: 2.3cqw; line-height: 1.35; opacity: .88; }}
.c-cta {{ font-family: var(--mono); font-size: 1.9cqw; letter-spacing: .1em; text-transform: uppercase; border: 1px solid currentColor; padding: .55em .9em; align-self: start; }}
.copy--center .c-cta, .copy--bottom .c-cta, .copy--center-top .c-cta, .panel--band .c-cta {{ align-self: center; }}
.tone--light {{ color: #f6f3ec; }}
.tone--dark {{ color: #14120f; }}
.on-photo.tone--light {{ text-shadow: 0 1px 16px rgb(0 0 0 / .55), 0 0 3px rgb(0 0 0 / .35); }}
.on-photo.tone--dark {{ text-shadow: 0 1px 14px rgb(255 255 255 / .7); }}
.copy--rail .c-sub, .copy--rail .c-cta {{ display: none; }}
.copy--rail .c-title {{ font-size: 3.6cqw; }}
.copy--top .c-title, .copy--bottom .c-title {{ font-size: 4.5cqw; }}
.copy--xl .c-title {{ font-size: 11.5cqw; line-height: .9; }}
.copy--xl .c-sub {{ font-size: 2.6cqw; }}

/* chrome */
.ui-dots {{ position: absolute; left: 50%; bottom: 6%; transform: translateX(-50%); display: flex; gap: 1.2cqw; }}
.ui-dots i {{ width: 1.2cqw; height: 1.2cqw; border-radius: 50%; background: rgb(255 255 255 / .5); }}
.ui-dots i:first-child {{ background: #fff; }}
.ui-dots--v {{ left: auto; right: 4%; bottom: auto; top: 50%; transform: translateY(-50%); flex-direction: column; }}
.ui-arrow {{ position: absolute; top: 50%; width: 3.2cqw; height: 3.2cqw; margin-top: -1.6cqw; background: rgb(255 255 255 / .85); }}
.ui-arrow--l {{ left: 3%; clip-path: polygon(62% 8%, 78% 24%, 46% 50%, 78% 76%, 62% 92%, 16% 50%); }}
.ui-arrow--r {{ right: 3%; clip-path: polygon(38% 8%, 22% 24%, 54% 50%, 22% 76%, 38% 92%, 84% 50%); }}
.ui-thumbs {{ position: absolute; bottom: 6%; display: flex; gap: 1cqw; }}
.ui-thumbs--right {{ right: 4%; }}
.ui-thumbs--left {{ left: 4%; }}
.ui-thumbs i {{ position: relative; width: 7cqw; height: 4.4cqw; overflow: hidden; box-shadow: 0 0 0 1px rgb(255 255 255 / .55); }}
.ui-thumbs i:first-child {{ box-shadow: 0 0 0 2px #fff; }}
.ui-counter {{ position: absolute; right: 4%; top: 5%; font-family: var(--mono); font-size: 1.8cqw; letter-spacing: .1em; color: #fff; text-shadow: 0 1px 8px rgb(0 0 0 / .6); }}
.ui-peek {{ position: absolute; right: 0; top: 7%; bottom: 7%; width: 10%; overflow: hidden; border-left: 2px solid var(--paper); }}
.ui-deck {{ position: absolute; box-shadow: 0 0 0 1px rgb(23 22 19 / .28); }}
.ui-deck--1 {{ inset: -6% -5%; }}
.ui-deck--2 {{ inset: -12% -10%; opacity: .45; }}
.ui-play {{ position: absolute; left: 50%; top: 50%; width: 9cqw; height: 9cqw; margin: -4.5cqw 0 0 -4.5cqw; border-radius: 50%; background: rgb(255 255 255 / .2); box-shadow: inset 0 0 0 1px rgb(255 255 255 / .85); }}
.ui-play::after {{ content: ""; position: absolute; left: 35%; top: 28%; border-left: 3cqw solid rgb(255 255 255 / .95); border-top: 2.1cqw solid transparent; border-bottom: 2.1cqw solid transparent; }}
.ui-progress {{ position: absolute; left: 5%; right: 5%; bottom: 6%; height: 2px; background: rgb(255 255 255 / .35); }}
.ui-progress i {{ display: block; width: 38%; height: 100%; background: #fff; }}
.ui-frames {{ position: absolute; right: 3%; top: 50%; transform: translateY(-50%); display: flex; flex-direction: column; gap: .8cqw; }}
.ui-frames i {{ position: relative; width: 6cqw; height: 3.6cqw; overflow: hidden; box-shadow: 0 0 0 1px rgb(255 255 255 / .6); }}
.ui-marquee {{ position: absolute; right: 2%; top: 50%; width: 5cqw; height: 2px; background: rgb(255 255 255 / .85); }}
.ui-marquee::after {{ content: ""; position: absolute; right: 0; top: -1cqw; border-left: 1.6cqw solid rgb(255 255 255 / .85); border-top: 1cqw solid transparent; border-bottom: 1cqw solid transparent; }}
.ui-pin {{ position: absolute; left: 34%; top: 38%; width: 3.4cqw; height: 3.4cqw; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); background: var(--accent); box-shadow: 0 0 0 .7cqw rgb(255 255 255 / .5); }}
.ui-handle {{ position: absolute; left: 50%; top: 0; bottom: 0; width: 2px; margin-left: -1px; background: var(--paper); box-shadow: 0 0 0 1px rgb(23 22 19 / .25); }}
.ui-handle::after {{ content: ""; position: absolute; left: -2cqw; top: 50%; margin-top: -2cqw; width: 4cqw; height: 4cqw; border-radius: 50%; background: var(--paper); box-shadow: 0 0 0 1px var(--rule), 0 .3cqw 1cqw rgb(0 0 0 / .3); }}
.ui-masktype {{ position: absolute; inset: 0 0 26% 0; display: grid; place-items: center; font-family: var(--sans); font-weight: 900; font-size: 15cqw; letter-spacing: -.055em;
  background-size: cover; background-position: center; -webkit-background-clip: text; background-clip: text; color: transparent; }}
.ui-winbar {{ position: absolute; left: 0; right: 0; top: 0; height: 3cqw; display: flex; align-items: center; gap: .7cqw; padding-left: 1.2cqw; background: rgb(246 243 236 / .9); }}
.ui-winbar i {{ width: 1cqw; height: 1cqw; border-radius: 50%; background: #b9b3a5; }}
.ui-rules {{ position: absolute; inset: 0; background-image: repeating-linear-gradient(180deg, transparent 0 3.4cqw, var(--rule) 3.4cqw calc(3.4cqw + 1px)); }}
.ui-mesh {{ position: absolute; inset: 0; background:
  radial-gradient(circle at 22% 26%, hsl(var(--h) 62% 72% / .85), transparent 42%),
  radial-gradient(circle at 78% 74%, hsl(calc(var(--h) - 32) 58% 70% / .8), transparent 46%); }}
.ui-flat {{ position: absolute; inset: 0; background: hsl(var(--h) 30% 26%); }}
.ui-duotone {{ position: absolute; inset: 0; background: linear-gradient(150deg, hsl(var(--h) 64% 34% / .82), hsl(calc(var(--h) - 60) 50% 52% / .78)); mix-blend-mode: hard-light; }}
.ui-inserts {{ position: absolute; right: 4%; bottom: 6%; display: flex; gap: 1cqw; }}
.ui-inserts i {{ position: relative; width: 11cqw; height: 8cqw; overflow: hidden; box-shadow: 0 0 0 1px var(--rule); }}
.ui-loops {{ position: absolute; left: 4%; bottom: 5%; font-family: var(--mono); font-size: 1.7cqw; letter-spacing: .08em; text-transform: uppercase; color: #fff; text-shadow: 0 1px 8px rgb(0 0 0 / .7); }}
.ui-cue {{ position: absolute; left: 50%; bottom: 3%; width: 1px; height: 3.4cqw; background: rgb(255 255 255 / .85); }}
.ui-cue::after {{ content: ""; position: absolute; left: -.7cqw; bottom: 0; border-top: 1.2cqw solid rgb(255 255 255 / .85); border-left: .8cqw solid transparent; border-right: .8cqw solid transparent; }}
.ui-vlabel {{ position: absolute; left: 3%; top: 8%; font-family: var(--mono); font-size: 1.8cqw; letter-spacing: .18em; text-transform: uppercase; color: var(--ink-2); writing-mode: vertical-rl; }}
.ui-handle--v {{ left: 0; right: 0; top: 50%; bottom: auto; width: auto; height: 2px; margin: -1px 0 0; }}
.ui-handle--v::after {{ left: 50%; top: 50%; margin: -2cqw 0 0 -2cqw; }}

/* chrome funzionale: la hero che chiede un'azione */
.ui-bar {{ position: absolute; left: 50%; bottom: 8%; transform: translateX(-50%); display: flex; align-items: stretch; gap: .5cqw;
  width: 74%; padding: .8cqw; background: rgb(255 255 255 / .94); box-shadow: 0 1cqw 2.6cqw rgb(0 0 0 / .22); }}
.ui-bar .f {{ flex: 1 1 0; display: flex; align-items: center; padding: .9cqw 1.1cqw; font-family: var(--mono); font-size: 1.7cqw;
  letter-spacing: .04em; color: #6d675c; background: #f2efe8; white-space: nowrap; overflow: hidden; }}
.ui-bar .f + .f {{ border-left: 1px solid rgb(23 22 19 / .1); }}
.ui-bar b {{ display: flex; align-items: center; padding: .9cqw 1.6cqw; font-family: var(--mono); font-size: 1.7cqw;
  letter-spacing: .1em; text-transform: uppercase; color: #fff; background: var(--accent); }}
.ui-bar--form {{ width: 56%; }}
.ui-stats {{ position: absolute; left: 6%; right: 6%; bottom: 7%; display: flex; gap: 6%; }}
.ui-stats i {{ display: flex; flex-direction: column; gap: .3cqw; }}
.ui-stats b {{ font-family: var(--serif); font-size: 6cqw; line-height: .9; letter-spacing: -.03em; color: #fff; text-shadow: 0 1px 12px rgb(0 0 0 / .5); }}
.ui-stats em {{ font-family: var(--mono); font-style: normal; font-size: 1.5cqw; letter-spacing: .14em; text-transform: uppercase; color: rgb(255 255 255 / .8); }}
.ui-logos {{ position: absolute; left: 8%; right: 8%; bottom: 8%; display: flex; align-items: center; justify-content: space-between; gap: 4%; }}
.ui-logos i {{ height: 2.4cqw; background: currentColor; opacity: .3; border-radius: .6cqw; }}
.ui-logos i:nth-child(1) {{ width: 13cqw; }}
.ui-logos i:nth-child(2) {{ width: 3.6cqw; height: 3.6cqw; border-radius: 50%; }}
.ui-logos i:nth-child(3) {{ width: 9cqw; }}
.ui-logos i:nth-child(4) {{ width: 15cqw; height: 1.8cqw; }}
.ui-logos i:nth-child(5) {{ width: 7cqw; height: 3cqw; border-radius: 0; }}
.ui-quote, .ui-prices, .ui-index {{ position: absolute; top: 50%; transform: translateY(-50%); width: 40%; display: flex; flex-direction: column;
  padding: 2.8cqw; background: var(--paper); box-shadow: 0 1cqw 2.8cqw rgb(0 0 0 / .22); }}
.ui-side--right {{ right: 5%; }}
.ui-side--left {{ left: 5%; }}
.ui-quote {{ gap: 1cqw; }}
.ui-quote b {{ font-family: var(--serif); font-size: 9cqw; line-height: .6; color: var(--accent); }}
.ui-quote em {{ font-family: var(--serif); font-style: italic; font-size: 3cqw; line-height: 1.25; color: var(--ink); }}
.ui-quote span {{ font-family: var(--mono); font-size: 1.5cqw; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-2); }}
.ui-prices i {{ display: flex; align-items: baseline; gap: 1cqw; padding: 1.1cqw 0; border-bottom: 1px solid rgb(23 22 19 / .18); }}
.ui-prices em {{ flex: 1 1 auto; font-family: var(--serif); font-style: normal; font-size: 2.4cqw; color: var(--ink); }}
.ui-prices b {{ font-family: var(--mono); font-size: 2cqw; font-variant-numeric: tabular-nums; color: var(--ink-2); }}
.ui-index i {{ display: flex; align-items: baseline; gap: 1.4cqw; padding: 1.2cqw 0; border-top: 1px solid rgb(23 22 19 / .2); font-family: var(--serif); font-size: 3cqw; color: var(--ink); }}
.ui-index i:first-child {{ color: var(--accent); }}
.ui-index em {{ font-family: var(--mono); font-style: normal; font-size: 1.5cqw; letter-spacing: .1em; color: var(--ink-2); }}
.ui-count {{ position: absolute; left: 50%; bottom: 8%; transform: translateX(-50%); display: flex; gap: 2.4cqw; }}
.ui-count i {{ display: flex; flex-direction: column; align-items: center; gap: .2cqw; min-width: 9cqw; padding: 1cqw .6cqw; background: rgb(255 255 255 / .9); }}
.ui-count b {{ font-family: var(--mono); font-size: 4cqw; font-variant-numeric: tabular-nums; letter-spacing: -.02em; color: var(--ink); }}
.ui-count em {{ font-family: var(--mono); font-style: normal; font-size: 1.3cqw; letter-spacing: .12em; text-transform: uppercase; color: var(--ink-2); }}
.ui-badge {{ position: absolute; right: 5%; top: 8%; width: 15cqw; height: 15cqw; border-radius: 50%; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: .3cqw; text-align: center; background: var(--paper); box-shadow: 0 .6cqw 2cqw rgb(0 0 0 / .28); }}
.ui-badge b {{ font-family: var(--serif); font-size: 3.4cqw; line-height: 1; color: var(--ink); }}
.ui-badge em {{ font-family: var(--mono); font-style: normal; font-size: 1.2cqw; letter-spacing: .08em; text-transform: uppercase; color: var(--ink-2); max-width: 11cqw; }}
.ui-avatars {{ position: absolute; left: 6%; bottom: 8%; display: flex; align-items: center; gap: 1.2cqw; }}
.ui-avatars i {{ position: relative; width: 5cqw; height: 5cqw; border-radius: 50%; overflow: hidden; box-shadow: 0 0 0 .4cqw var(--paper); }}
.ui-avatars i + i {{ margin-left: -2.2cqw; }}
.ui-avatars em {{ margin-left: .6cqw; font-family: var(--mono); font-style: normal; font-size: 1.5cqw; letter-spacing: .1em; text-transform: uppercase; color: #fff; text-shadow: 0 1px 8px rgb(0 0 0 / .7); }}
.ui-pins i {{ position: absolute; width: 3cqw; height: 3cqw; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); background: var(--accent); box-shadow: 0 0 0 .6cqw rgb(255 255 255 / .45); }}
.ui-pins .p1 {{ left: 26%; top: 34%; }}
.ui-pins .p2 {{ left: 52%; top: 56%; opacity: .75; }}
.ui-pins .p3 {{ left: 68%; top: 28%; opacity: .55; }}
.ui-grain {{ position: absolute; inset: 0; opacity: .28; mix-blend-mode: overlay; background-size: .5cqw .5cqw;
  background-image: repeating-conic-gradient(rgb(255 255 255 / .55) 0 25%, rgb(0 0 0 / .55) 0 50%); }}
.ui-arc {{ position: absolute; inset: 0; background: hsl(var(--h) 24% 90%); }}
.ui-arc svg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
.ui-arc text {{ font-family: var(--mono); font-size: 6px; letter-spacing: .32em; text-transform: uppercase; fill: hsl(var(--h) 40% 28%); text-anchor: middle; }}
.ui-hovercue {{ position: absolute; right: 6%; bottom: 9%; padding: .7cqw 1.2cqw; font-family: var(--mono); font-size: 1.4cqw;
  letter-spacing: .12em; text-transform: uppercase; color: var(--ink); background: var(--paper); border-radius: 2cqw; }}
.ui-steps {{ position: absolute; left: 6%; top: 50%; transform: translateY(-50%); display: flex; flex-direction: column; gap: 1.6cqw; }}
.ui-steps i {{ font-family: var(--mono); font-size: 1.6cqw; letter-spacing: .1em; color: rgb(255 255 255 / .55); }}
.ui-steps i:first-child {{ color: #fff; }}

/* --------------------------------------------------------------- legend */
.legend {{ margin-top: 3rem; border-top: 1px solid var(--rule); padding-top: 1.5rem; }}
.legend h2 {{ font-family: var(--serif); font-weight: 500; font-size: 1.5rem; letter-spacing: -.025em; margin: 0 0 1rem; }}
.legend__cols {{ display: grid; gap: 1.5rem 2.5rem; grid-template-columns: repeat(auto-fit, minmax(min(100%, 17rem), 1fr)); }}
.legend h3 {{ font-family: var(--mono); font-size: .68rem; letter-spacing: .14em; text-transform: uppercase; color: var(--accent); margin: 0 0 .5rem; }}
.legend dl {{ margin: 0; }}
.legend dt {{ font-size: .82rem; }}
.legend dt code {{ color: var(--ink-2); }}
.legend dd {{ margin: 0 0 .6rem; font-size: .8rem; color: var(--ink-2); max-width: 46ch; }}
.credits {{ margin-top: 2rem; border-top: 1px solid var(--rule); padding-top: 1rem; }}
.credits p {{ margin: 0; font-family: var(--mono); font-size: .7rem; line-height: 1.6; color: var(--ink-2); max-width: 80ch; }}

/* ------------------------------------------------------------- selection */
.tray {{ position: fixed; left: 0; right: 0; bottom: 0; z-index: 10; display: flex; flex-wrap: wrap; gap: .5rem 1rem; align-items: center; padding: .7rem clamp(1rem, 4vw, 3rem); background: var(--ink); color: var(--paper); }}
.tray[hidden] {{ display: none; }}
.tray p {{ margin: 0; font-family: var(--mono); font-size: .74rem; flex: 1 1 14rem; word-break: break-word; }}
.tray .btn {{ border-color: rgb(255 255 255 / .45); color: var(--paper); }}
.empty {{ font-family: var(--mono); font-size: .8rem; color: var(--ink-2); padding: 2rem 0; }}
.empty[hidden] {{ display: none; }}

@media (max-width: 720px) {{
  .toolbar {{ position: static; }}
  .notes {{ grid-template-columns: 1fr; }}
}}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; animation: none !important; }} }}
</style>
</head>
<body>
<header class="masthead">
  <p class="kicker">agent-frontend-taste · hero archetypes</p>
  <h1>Scegli la hero guardandola.</h1>
  <p class="lede">Ogni miniatura è una hero vera in piccolo: foto, titolo, sottotitolo e pulsante
  al loro posto. Cambia solo lo <strong>schema</strong> — che media occupa il primo viewport, dove
  va il blocco di testo, se sta su un pannello pieno o su niente. {len(archetypes)} archetipi:
  foto singola, carosello, video, nessun media, collage, sequenza a scroll, UI di prodotto, mappa,
  prima/dopo.</p>
  <p class="lede">Dimmi l'<code>id</code> (o selezionane più di uno e copia la lista): da lì fisso
  <code>hero_treatment</code>, <code>hero_copy</code>, placement e pannello, e la scelta a vista batte
  il sorteggio da seed. Foto e marchi qui sono campioni: nel progetto vero palette, font e immagini
  restano derivati da località + carattere + business.</p>
</header>

<div class="toolbar">
  {filters}
  <label class="search">
    <input type="search" id="q" placeholder="Cerca: video, centrato, plate, mappa…" aria-label="Cerca archetipo">
  </label>
  <button type="button" class="btn" id="reset">Azzera</button>
  <span class="count" id="count"></span>
</div>

<main>
  <div class="grid" id="grid">
{cards}  </div>
  <p class="empty" hidden id="empty">Nessun archetipo con questi filtri.</p>
  {_legend(axes)}
  {_credits(catalog)}
</main>

<div class="tray" hidden id="tray">
  <p id="picked"></p>
  <button type="button" class="btn" id="copy">Copia gli id</button>
  <button type="button" class="btn" id="clear">Deseleziona</button>
</div>

<script>
(function () {{
  var cards = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var q = document.getElementById('q');
  var count = document.getElementById('count');
  var empty = document.getElementById('empty');
  var tray = document.getElementById('tray');
  var picked = document.getElementById('picked');
  var active = {{ media: [], placement: [], panel: [] }};

  function apply() {{
    var needle = q.value.trim().toLowerCase();
    var shown = 0;
    cards.forEach(function (card) {{
      var ok = Object.keys(active).every(function (group) {{
        return !active[group].length || active[group].indexOf(card.dataset[group]) > -1;
      }});
      if (ok && needle) ok = card.dataset.search.indexOf(needle) > -1;
      card.hidden = !ok;
      if (ok) shown++;
    }});
    count.textContent = shown + ' / ' + cards.length + ' archetipi';
    empty.hidden = shown > 0;
  }}

  function refreshTray() {{
    var ids = cards.filter(function (c) {{ return c.getAttribute('aria-pressed') === 'true'; }})
      .map(function (c) {{ return c.dataset.id; }});
    tray.hidden = ids.length === 0;
    picked.textContent = ids.join(' · ');
    return ids;
  }}

  chips.forEach(function (chip) {{
    chip.addEventListener('click', function () {{
      var on = chip.getAttribute('aria-pressed') === 'true';
      chip.setAttribute('aria-pressed', on ? 'false' : 'true');
      var list = active[chip.dataset.group];
      var i = list.indexOf(chip.dataset.value);
      if (on && i > -1) list.splice(i, 1);
      if (!on && i === -1) list.push(chip.dataset.value);
      apply();
    }});
  }});

  q.addEventListener('input', apply);

  document.getElementById('reset').addEventListener('click', function () {{
    chips.forEach(function (c) {{ c.setAttribute('aria-pressed', 'false'); }});
    Object.keys(active).forEach(function (k) {{ active[k] = []; }});
    q.value = '';
    apply();
  }});

  cards.forEach(function (card) {{
    function toggle() {{
      card.setAttribute('aria-pressed', card.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      refreshTray();
    }}
    card.addEventListener('click', toggle);
    card.addEventListener('keydown', function (e) {{
      if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); toggle(); }}
    }});
  }});

  document.getElementById('clear').addEventListener('click', function () {{
    cards.forEach(function (c) {{ c.setAttribute('aria-pressed', 'false'); }});
    refreshTray();
  }});

  document.getElementById('copy').addEventListener('click', function (e) {{
    var ids = refreshTray().join(' ');
    var done = function () {{ e.target.textContent = 'Copiati'; setTimeout(function () {{ e.target.textContent = 'Copia gli id'; }}, 1400); }};
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(ids).then(done, done);
    }} else {{
      var ta = document.createElement('textarea');
      ta.value = ids; document.body.appendChild(ta); ta.select();
      try {{ document.execCommand('copy'); }} catch (err) {{}}
      document.body.removeChild(ta); done();
    }}
  }});

  apply();
}})();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------- CLI


def main() -> int:
    ap = argparse.ArgumentParser(description="Hero archetypes: pagina di scelta + lookup")
    ap.add_argument("--build", action="store_true", help="scrive la pagina HTML")
    ap.add_argument("--check", action="store_true", help="verifica che la pagina sia in sync col catalogo")
    ap.add_argument("--out", type=Path, default=PAGE, help=f"path della pagina (default {PAGE})")
    ap.add_argument("--show", metavar="ID", help="dettaglio di un archetipo")
    ap.add_argument("--filter", action="append", default=[], metavar="K=V", help="es. media=video, placement=center")
    ap.add_argument("--suggest", type=int, metavar="N", help="shortlist da seed, diversa su media e placement")
    ap.add_argument("--seed", default=None, help="YYYYMMDDHH (default: ora corrente)")
    ap.add_argument("--last", nargs="*", default=[], help="id / treatment / hero_copy da escludere (da MEMORY)")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    args = ap.parse_args()

    catalog = load()
    archetypes = catalog["archetypes"]

    if args.check:
        if not args.out.exists():
            print(f"FAIL: {args.out} non esiste — esegui --build")
            return 1
        if args.out.read_text(encoding="utf-8") != render_html(catalog):
            print(f"FAIL: {args.out} non è in sync col catalogo — esegui --build")
            return 1
        print(f"ok: {args.out} in sync con {CATALOG.name}")
        return 0

    if args.build:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(render_html(catalog), encoding="utf-8")
        print(f"hero gallery: {args.out}  ({len(archetypes)} archetipi)")
        print(f"apri con: open {args.out}")
        return 0

    if args.show:
        entry = next((a for a in archetypes if a["id"] == args.show), None)
        if not entry:
            print(f"id sconosciuto: {args.show}")
            return 1
        print(json.dumps(entry, ensure_ascii=False, indent=2) if args.format == "json" else render_show(catalog, entry))
        return 0

    entries = [a for a in archetypes if match_filters(a, parse_filters(args.filter, catalog))]

    if args.suggest:
        seed = args.seed or datetime.now().strftime("%Y%m%d%H")
        entries = suggest(entries, args.suggest, seed, args.last)
        if args.format == "md":
            print(f"seed: `{seed}`" + (f" · esclusi: {', '.join(args.last)}" if args.last else ""))

    if args.format == "json":
        print(json.dumps(entries, ensure_ascii=False, indent=2))
    else:
        print(render_list(catalog, entries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
