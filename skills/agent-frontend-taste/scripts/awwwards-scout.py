#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Scout Awwwards list/detail pages into compact markdown.

Uses path-based URLs that return 200 and are robots-friendlier than
/websites/? query lists. Stdlib only.

The Awwwards detail page only carries <title> + og:description, which is no
structural signal at all. --inspect follows the awarded site's own URL and
measures its CSS on the three craft axes (type / composition / surface), so the
batch produces counts instead of impressions.

Usage:
    uv run awwwards-scout.py --list sotd|nominees|sotm|best-of|websites [--limit N]
    uv run awwwards-scout.py --site <slug> [--inspect]
    uv run awwwards-scout.py --live https://example.com
"""

from __future__ import annotations

import argparse
import html as html_lib
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass

UA = "VesperFrontendTaste/1.0 (+local craft research; respectful)"
BASE = "https://www.awwwards.com"

LISTS = {
    "sotd": f"{BASE}/websites/sites_of_the_day/",
    "sotm": f"{BASE}/websites/sites_of_the_month/",
    "nominees": f"{BASE}/websites/nominees/",
    "best-of": f"{BASE}/websites/best-of/",
    "websites": f"{BASE}/websites/",
}

SITE_HREF = re.compile(r'href="(/sites/([a-zA-Z0-9_-]+)/?)"')
TITLE_TAG = re.compile(r"<title>([^<]+)</title>", re.I)
OG_DESC = re.compile(r'property="og:description"\s+content="([^"]*)"', re.I)
# Cards often put studio/site names in avatar-name titles near the slug.
NEAR_TITLE = re.compile(
    r'href="(/sites/([a-zA-Z0-9_-]+)/?)"[^>]*>.*?'
    r'class="[^"]*avatar-name__title[^"]*"[^>]*>([^<]+)</',
    re.I | re.S,
)
# The awarded site's own URL sits on a nofollow link (either attribute order).
NOFOLLOW_FIRST = re.compile(r'rel="[^"]*nofollow[^"]*"[^>]*href="(https?://[^"]+)"', re.I)
HREF_FIRST = re.compile(r'href="(https?://[^"]+)"[^>]*rel="[^"]*nofollow[^"]*"', re.I)

SKIP_HOSTS = (
    "awwwards.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "pinterest.com",
    "youtube.com",
    "vimeo.com",
    "behance.net",
    "dribbble.com",
    "github.com",
    "apple.com",
    "google.com",
)

STYLESHEET = re.compile(r'<link[^>]+rel="stylesheet"[^>]*>', re.I)
HREF_ATTR = re.compile(r'href="([^"]+)"', re.I)
INLINE_STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.I | re.S)
# Many sites preload their bundle or inject it from JS: <link rel="stylesheet"> alone misses it.
ANY_CSS = re.compile(r"""["'((](/[^"'()\s]+\.css[^"'()\s]*|https?://[^"'()\s]+\.css[^"'()\s]*)["')]""")


@dataclass(frozen=True)
class SiteCard:
    slug: str
    path: str
    label: str


def fetch(url: str, timeout: float = 25.0, hard: bool = True) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,text/css"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        if hard:
            raise SystemExit(f"HTTP {e.code} for {url}") from e
        return ""
    except (urllib.error.URLError, TimeoutError) as e:
        if hard:
            raise SystemExit(f"Network error for {url}: {e}") from e
        return ""


def parse_list(page: str) -> list[SiteCard]:
    labeled: dict[str, str] = {}
    for _path, slug, label in NEAR_TITLE.findall(page):
        labeled[slug] = html_lib.unescape(label.strip())

    cards: list[SiteCard] = []
    seen: set[str] = set()
    for path, slug in SITE_HREF.findall(page):
        if slug in seen:
            continue
        seen.add(slug)
        norm = path if path.endswith("/") else path + "/"
        cards.append(
            SiteCard(slug=slug, path=norm, label=labeled.get(slug, slug.replace("-", " ")))
        )
    return cards


def parse_site(page: str, slug: str) -> tuple[str, str, str | None]:
    title = TITLE_TAG.search(page)
    desc = OG_DESC.search(page)
    t = html_lib.unescape(title.group(1).strip()) if title else slug
    d = html_lib.unescape(desc.group(1).strip()) if desc else ""
    return t, d, find_live_url(page)


def find_live_url(page: str) -> str | None:
    for pattern in (NOFOLLOW_FIRST, HREF_FIRST):
        for candidate in pattern.findall(page):
            host = urllib.parse.urlparse(candidate).netloc.lower()
            if any(host == s or host.endswith("." + s) for s in SKIP_HOSTS):
                continue
            return candidate.split("?")[0]
    return None


def collect_css(url: str, css_limit: int) -> tuple[str, int, list[str]]:
    """Return concatenated CSS, request count, and notes about what failed."""
    notes: list[str] = []
    page = fetch(url, hard=False)
    if not page:
        return "", 1, [f"live page unreachable: {url}"]

    css_parts = INLINE_STYLE.findall(page)
    candidates: list[str] = []
    for tag in STYLESHEET.findall(page):
        m = HREF_ATTR.search(tag)
        if m:
            candidates.append(m.group(1))
    candidates.extend(ANY_CSS.findall(page))

    hrefs: list[str] = []
    for raw in candidates:
        href = urllib.parse.urljoin(url, html_lib.unescape(raw))
        host = urllib.parse.urlparse(href).netloc.lower()
        if host.startswith(("localhost", "127.0.0.1")):
            continue  # dev leftover shipped to prod
        if href not in hrefs:
            hrefs.append(href)

    requests = 1
    for href in hrefs[:css_limit]:
        text = fetch(href, hard=False)
        requests += 1
        if text:
            css_parts.append(text)
        else:
            notes.append(f"stylesheet unreachable: {href}")
    if len(hrefs) > css_limit:
        notes.append(f"{len(hrefs) - css_limit} stylesheet(s) skipped (--css-limit {css_limit})")
    return "\n".join(css_parts), requests, notes


def _count(pattern: str, css: str) -> int:
    return len(re.findall(pattern, css, re.I))


def _top(values: list[str], n: int = 6) -> str:
    if not values:
        return "—"
    return " · ".join(f"{v} ×{c}" for v, c in Counter(values).most_common(n))


def report_css(css: str) -> None:
    families = [f.strip() for f in re.findall(r'font-family:\s*["\']?([^;,"\'{}]+)', css)]
    tokens = sorted({t for t in re.findall(r"--(?:font|f)-[a-z0-9-]+", css, re.I)})
    clamps = re.findall(r"clamp\(([^()]*(?:\([^()]*\)[^()]*)*)\)", css)
    degenerate = 0
    for c in clamps:
        parts = [p.strip() for p in c.split(",")]
        if len(parts) == 3 and parts[0] == parts[2]:
            degenerate += 1
    vw_display = sorted(
        {v for v in re.findall(r"font-size:\s*([0-9.]+vw)", css)},
        key=lambda s: float(s[:-2]),
        reverse=True,
    )
    tracking_neg = sorted({v for v in re.findall(r"letter-spacing:\s*(-[0-9.]+[a-z%]+)", css)})
    tracking_pos = sorted({v for v in re.findall(r"letter-spacing:\s*(0?\.[0-9]+e?m)", css)})
    leading = re.findall(r"line-height:\s*([0-9.]+%?)", css)
    weights = re.findall(r"font-weight:\s*([1-9]00)", css)

    print("## Tipografia")
    print(f"- famiglie distinte: {len(set(families))} → {_top(families, 6)}")
    print(f"- token font: {', '.join(tokens[:8]) if tokens else '—'}")
    print(f"- clamp(): {len(clamps)} (degeneri min=max: {degenerate})")
    print(f"- font-size in vw (type-first): {', '.join(vw_display[:6]) if vw_display else '—'}")
    print(f"- tracking negativo: {', '.join(tracking_neg[:6]) if tracking_neg else '—'}")
    print(f"- tracking positivo: {', '.join(tracking_pos[:6]) if tracking_pos else '—'}")
    print(f"- line-height ricorrenti: {_top(leading, 5)}")
    print(f"- pesi: {_top(weights, 5)}")
    uppercase = _count(r"text-transform:\s*uppercase", css)
    tabular = _count(r"tabular-nums", css)
    optical = _count(r"font-optical-sizing", css)
    wrap = _count(r"text-wrap:", css)
    print(f"- uppercase: {uppercase}")
    print(f"- tabular-nums: {tabular} · optical-sizing: {optical} · text-wrap: {wrap}")

    cols = re.findall(r"grid-template-columns:\s*repeat\((\d+)", css)
    explicit = re.findall(r"grid-column:\s*(-?\d+\s*/\s*(?:span\s*)?-?\d+)", css)
    spans = _count(r"grid-column:\s*span", css)
    rails = re.findall(r"grid-template-columns:\s*([0-9.]+(?:vw|rem|px)\s+1fr)", css)
    ch_widths = sorted({v for v in re.findall(r"max-width:\s*(\d+)ch", css)}, key=int)
    aligns = re.findall(r"text-align:\s*(left|right|center|justify)", css)
    justify = re.findall(r"justify-self:\s*(start|end|center)", css)
    # Numeric ratios only: minified CSS makes a greedy [^;]+ swallow whole rules.
    ratios = sorted(
        {
            v.strip()
            for v in re.findall(
                r"aspect-ratio:\s*(\.?\d+(?:\.\d+)?(?:\s*/\s*\.?\d+(?:\.\d+)?)?)", css
            )
        }
    )

    print()
    print("## Composizione")
    print(f"- griglie repeat(N): {_top(cols, 6)}")
    print(f"- rail asimmetrici: {', '.join(sorted(set(rails))[:4]) if rails else '—'}")
    print(f"- grid-column espliciti: {len(explicit)} (vs span: {spans}) → {', '.join(explicit[:6]) if explicit else '—'}")
    print(f"- subgrid: {_count('subgrid', css)}")
    print(f"- max-width in ch: {', '.join(ch_widths[:10]) if ch_widths else '—'}")
    print(f"- text-align: {_top(aligns, 4)}")
    print(f"- justify-self: {_top(justify, 3)}")
    bleeds = _count(r"\b100vw\b", css)
    vertical = _count(r"writing-mode:\s*vertical", css)
    print(f"- 100vw (bleed): {bleeds} · writing-mode vertical: {vertical}")
    print(f"- aspect-ratio: {', '.join(ratios[:8]) if ratios else '—'}")

    solid = _count(r"1px solid", css)
    dashed = _count(r"1px dashed", css)
    bg_sizes = sorted({v.strip() for v in re.findall(r"background-size:\s*([^;]+)", css)})
    blurs = re.findall(r"blur\(([0-9.]+px)\)", css)
    angles = re.findall(r"linear-gradient\(\s*([0-9.]+deg)", css)
    blends = re.findall(r"mix-blend-mode:\s*([a-z-]+)", css)
    opacities = re.findall(r"opacity:\s*(0?\.\d+)", css)
    radii = re.findall(r"border-radius:\s*([^;]+)", css)

    print()
    print("## Superfici")
    print(f"- hairline: 1px solid ×{solid} · 1px dashed ×{dashed}")
    print(f"- background-size (pattern/baseline): {', '.join(bg_sizes[:6]) if bg_sizes else '—'}")
    radial = _count("radial-gradient", css)
    linear = _count("linear-gradient", css)
    backdrop = _count("backdrop-filter", css)
    inverts = _count(r"invert\(", css)
    clips = _count("clip-path", css)
    masks = _count(r"(?:-webkit-)?mask(?:-image)?:", css)
    grain = _count(r"feTurbulence|noise", css)
    print(f"- radial-gradient: {radial} · linear-gradient: {linear}")
    print(f"- angoli gradiente: {_top(angles, 5)}")
    print(f"- blur come luce: {_top(blurs, 5)} · backdrop-filter: {backdrop}")
    print(f"- blend mode: {_top(blends, 4)} · invert: {inverts}")
    print(f"- clip-path: {clips} · mask: {masks}")
    print(f"- grana: {grain}")
    print(f"- scala opacità: {_top(opacities, 6)}")
    print(f"- border-radius ricorrenti: {_top([r.strip() for r in radii], 5)}")
    themed = _count("data-theme", css)
    theme_classes = _count(r"\.theme-[a-z]+", css)
    print(f"- theme per sezione: data-theme ×{themed} · classi tema ×{theme_classes}")


def cmd_list(kind: str, limit: int) -> int:
    url = LISTS[kind]
    page = fetch(url)
    cards = parse_list(page)[:limit]
    print(f"# Awwwards {kind}")
    print(f"Source: {url}")
    print(f"Found: {len(cards)} (showing up to {limit})")
    print()
    if not cards:
        print("_No /sites/ links parsed. Page shape may have changed._")
        return 1
    for i, c in enumerate(cards, 1):
        print(f"{i}. **{c.label}** — {BASE}{c.path}")
    return 0


def cmd_site(slug: str, inspect: bool, css_limit: int) -> int:
    slug = slug.strip().strip("/")
    if not slug:
        # An empty slug built /sites// — which 200'd on the generic Nominees
        # page and printed it as if it were the requested site. A wrong slug
        # must fail loud, not silently answer with the wrong page.
        raise SystemExit("--site: valore vuoto (usa lo slug del sito, es. --site siena-film)")
    url = f"{BASE}/sites/{slug}/"
    page = fetch(url)
    title, desc, live = parse_site(page, slug)
    print(f"# {title}")
    print(f"URL: {url}")
    print(f"Live: {live or '_not found on the page_'}")
    if desc:
        print()
        print(desc)
    if not inspect:
        print()
        print("_Solo title + og:description: nessun segnale strutturale. Usa --inspect._")
        return 0
    if not live:
        print()
        print("_--inspect impossibile: URL live non trovato._")
        return 1
    print()
    return cmd_live(live, css_limit)


def cmd_live(url: str, css_limit: int) -> int:
    css, requests, notes = collect_css(url, css_limit)
    print(f"# Segnali misurati — {url}")
    print(f"CSS raccolto: {len(css)} char in {requests} request")
    for n in notes:
        print(f"- gap: {n}")
    print()
    if not css:
        print("_Nessun CSS leggibile: dichiara il gap e usa un altro riferimento._")
        return 1
    report_css(css)
    print()
    print("_Conteggi, non ricette: estrai principi, mai hex o asset. Clonare un sito = fallimento._")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Scout Awwwards lists/sites")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", choices=sorted(LISTS), help="List page to scout")
    g.add_argument("--site", help="Site slug under /sites/")
    g.add_argument("--live", help="Inspect a live URL directly (skip Awwwards)")
    p.add_argument("--limit", type=int, default=12, help="Max cards for --list")
    p.add_argument(
        "--inspect",
        action="store_true",
        help="With --site: follow the awarded site and measure its CSS",
    )
    p.add_argument("--css-limit", type=int, default=6, help="Max stylesheets to fetch (default 6)")
    args = p.parse_args()

    # Was `max(1, n)`: silent — `--limit 0` quietly showed 1 result instead of
    # saying the value made no sense.
    if args.limit < 1:
        raise SystemExit(f"--limit {args.limit}: deve essere ≥1")
    if args.css_limit < 1:
        raise SystemExit(f"--css-limit {args.css_limit}: deve essere ≥1")

    if args.list:
        return cmd_list(args.list, args.limit)
    if args.live:
        return cmd_live(args.live, args.css_limit)
    return cmd_site(args.site, args.inspect, args.css_limit)


if __name__ == "__main__":
    raise SystemExit(main())
