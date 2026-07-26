#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Scout Dribbble list pages into compact markdown.

/tags/* is robots-disallowed and returns empty (202). For the owner's
website-template intent, use --list website-template which hits
/shots?q=website+template (verified 200). Stdlib only.

Usage:
    uv run dribbble-scout.py --list shots|website-template|home [--limit N]
    uv run dribbble-scout.py --shot <id-or-slug-path>
"""

from __future__ import annotations

import argparse
import html as html_lib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

UA = "VesperFrontendTaste/1.0 (+local craft research; respectful)"
BASE = "https://dribbble.com"

# Path intent → fetchable URL (see references/inspire-ops.md)
LISTS = {
    "shots": f"{BASE}/shots",
    "home": f"{BASE}/",
    # Functional stand-in for https://dribbble.com/tags/website-template
    "website-template": f"{BASE}/shots?q={urllib.parse.quote('website template')}",
}

SHOT_HREF = re.compile(r'href="(/shots/(\d+)-([^"?#]+))"')
TITLE_TAG = re.compile(r"<title>([^<]+)</title>", re.I)
OG_DESC = re.compile(
    r'property="og:description"\s+content="([^"]*)"', re.I
)


@dataclass(frozen=True)
class ShotCard:
    shot_id: str
    path: str
    label: str


def fetch(url: str, timeout: float = 25.0) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code} for {url}") from e
    except urllib.error.URLError as e:
        raise SystemExit(f"Network error for {url}: {e}") from e


WEB_HINT = re.compile(
    r"(?:^|[\s_-])(landing|website|web|dashboard|page|ui|ux|template|saas|app|site|ecommerce|e-commerce|shop)(?:$|[\s_-])",
    re.I,
)


def parse_list(page: str) -> list[ShotCard]:
    cards: list[ShotCard] = []
    seen: set[str] = set()
    for path, shot_id, slug in SHOT_HREF.findall(page):
        if shot_id in seen:
            continue
        seen.add(shot_id)
        label = html_lib.unescape(slug.replace("-", " ").strip())
        cards.append(ShotCard(shot_id=shot_id, path=path, label=label))
    return cards


def prefer_web_ui(cards: list[ShotCard]) -> list[ShotCard]:
    """Soft filter for website-template intent: keep UI/web-ish labels first."""
    preferred = [c for c in cards if WEB_HINT.search(c.label)]
    return preferred if preferred else cards


def cmd_list(kind: str, limit: int) -> int:
    url = LISTS[kind]
    page = fetch(url)
    cards = parse_list(page)
    if kind == "website-template":
        cards = prefer_web_ui(cards)
    cards = cards[:limit]
    print(f"# Dribbble {kind}")
    print(f"Source: {url}")
    if kind == "website-template":
        print(
            "Note: /tags/website-template is robots-disallowed and empty; "
            "this list is the working equivalent via /shots?q=website+template"
        )
    print(f"Found: {len(cards)} (showing up to {limit})")
    print()
    if not cards:
        print("_No /shots/ links parsed. Page shape may have changed or bot-blocked._")
        return 1
    for i, c in enumerate(cards, 1):
        print(f"{i}. **{c.label}** — {BASE}{c.path}")
    return 0


def parse_shot(page: str, spec: str) -> tuple[str, str]:
    """Title + og:description of a shot detail page — same pattern as
    awwwards-scout.parse_site, since detail pages here are equally bot-gated
    and carry little beyond those two tags."""
    title = TITLE_TAG.search(page)
    desc = OG_DESC.search(page)
    t = html_lib.unescape(title.group(1).strip()) if title else spec
    d = html_lib.unescape(desc.group(1).strip()) if desc else ""
    return t, d


def cmd_shot(spec: str) -> int:
    spec = spec.strip().lstrip("/")
    if not spec:
        raise SystemExit("--shot: valore vuoto (usa un id o uno slug, es. --shot 12345-nome)")
    if spec.startswith("shots/"):
        path = "/" + spec
    elif re.fullmatch(r"\d+", spec):
        # id alone: list page may be needed; try as path fragment
        path = f"/shots/{spec}"
    else:
        path = f"/shots/{spec}" if not spec.startswith("shots/") else "/" + spec
    url = BASE + path
    page = fetch(url)
    title, desc = parse_shot(page, spec)
    print(f"# {title}")
    print(f"URL: {url}")
    if desc:
        print()
        print(desc)
    elif len(page) < 500:
        print()
        print("_Empty/blocked detail page — use list labels and open URL in browser._")
        return 1
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Scout Dribbble shots")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", choices=sorted(LISTS), help="List page to scout")
    g.add_argument("--shot", help="Shot id, slug, or shots/… path")
    p.add_argument("--limit", type=int, default=12, help="Max cards for --list")
    args = p.parse_args()

    if args.list:
        if args.limit < 1:
            raise SystemExit(f"--limit {args.limit}: deve essere ≥1")
        return cmd_list(args.list, args.limit)
    return cmd_shot(args.shot)


if __name__ == "__main__":
    raise SystemExit(main())
