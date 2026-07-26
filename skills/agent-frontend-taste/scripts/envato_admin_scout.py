#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Scout Envato Elements admin/dashboard web templates.

Canonical catalog (no ad tracking query noise):
  https://elements.envato.com/web-templates/admin-templates

Also rotates sibling catalogs for variety:
  /web-templates/dashboard
  /web-templates/admin-dashboards

Stdlib only. Structure research — do not clone templates.

Usage:
    uv run scripts/envato_admin_scout.py --list [--limit 30]
    uv run scripts/envato_admin_scout.py --sample 30
    uv run scripts/envato_admin_scout.py --sample 30 --seed 2026072514
    uv run scripts/envato_admin_scout.py --dry-run --sample 30
"""

from __future__ import annotations

import argparse
import random
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime

UA = "VesperFrontendTaste/1.0 (+local craft research; respectful)"
BASE = "https://elements.envato.com"

# Path catalogs that return distinct item sets (verified 2026-07-25).
# Prefer clean paths — strip gclid/gad marketing params.
CATALOGS = [
    f"{BASE}/web-templates/admin-templates",
    f"{BASE}/web-templates/dashboard",
    f"{BASE}/web-templates/admin-dashboards",
]

# /slug-title-ITEMCODE  (Envato item code is uppercase alnum, len≥6)
ITEM_HREF = re.compile(r'href="(/([a-z0-9-]+)-([A-Z0-9]{6,}))"')


@dataclass(frozen=True)
class EnvatoCard:
    code: str
    slug: str
    label: str
    url: str
    catalog: str


def hour_seed(when: datetime | None = None) -> str:
    return (when or datetime.now()).strftime("%Y%m%d%H")


def fetch(url: str, timeout: float = 30.0) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} for {url}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error for {url}: {e}") from e


def parse_catalog(page: str, catalog_url: str) -> list[EnvatoCard]:
    out: list[EnvatoCard] = []
    seen: set[str] = set()
    for path, slug, code in ITEM_HREF.findall(page):
        if code in seen:
            continue
        if path.count("/") != 1:
            continue
        # Skip category/nav shells that might match pattern loosely
        if any(
            bad in path
            for bad in (
                "/web-templates",
                "/graphic-templates",
                "/presentation",
                "/wordpress",
            )
        ):
            continue
        seen.add(code)
        label = slug.replace("-", " ").strip()
        out.append(
            EnvatoCard(
                code=code,
                slug=slug,
                label=label,
                url=f"{BASE}{path}",
                catalog=catalog_url,
            )
        )
    return out


def catalog_index(seed: str, n: int = 3) -> int:
    digits = "".join(ch for ch in seed if ch.isdigit())
    if not digits:
        return hash(seed) % n
    return int(digits) % n


def build_pool(
    seed: str,
    fetch_fn=fetch,
) -> tuple[list[EnvatoCard], int, list[str]]:
    """Primary catalog from seed hour + fillers for a larger unique pool."""
    idx = catalog_index(seed, len(CATALOGS))
    order = CATALOGS[idx:] + CATALOGS[:idx]
    errors: list[str] = []
    pool: list[EnvatoCard] = []
    seen: set[str] = set()

    for url in order:
        try:
            page = fetch_fn(url)
        except RuntimeError as e:
            errors.append(str(e))
            continue
        for c in parse_catalog(page, url):
            if c.code in seen:
                continue
            seen.add(c.code)
            pool.append(c)
        if len(pool) >= 60:
            break
    return pool, idx, errors


def sample_cards(pool: list[EnvatoCard], count: int, seed: str) -> list[EnvatoCard]:
    rng = random.Random(seed)
    items = list(pool)
    rng.shuffle(items)
    return items[: max(0, count)]


def dry_run_pool() -> list[EnvatoCard]:
    return [
        EnvatoCard(
            code=f"CODE{i:04d}",
            slug=f"demo-admin-dashboard-template-{i}",
            label=f"demo admin dashboard template {i}",
            url=f"{BASE}/demo-admin-dashboard-template-{i}-CODE{i:04d}",
            catalog=CATALOGS[i % len(CATALOGS)],
        )
        for i in range(1, 45)
    ]


def render(
    sample: list[EnvatoCard],
    *,
    seed: str,
    catalog_idx: int,
    pool_size: int,
    errors: list[str],
    count: int,
) -> str:
    lines = [
        "# Envato Elements — admin templates batch",
        f"Canonical: {CATALOGS[0]}",
        f"Seed (YYYYMMDDHH): `{seed}`",
        f"Primary catalog index: {catalog_idx} / {len(CATALOGS)}",
        f"Pool size: {pool_size} → evaluating: {len(sample)} (target ≥{count})",
        "",
        "Lenses (structure only — do not clone markup/assets):",
        "- **IA / nav** — sidebar, icon-rail, topbar, wayfinding",
        "- **Tables** — density, filters, row actions, avatars",
        "- **KPI / cards** — summary hierarchy without card spam",
        "- **Forms / dialogs** — create-edit patterns",
        "- **Light + dark** — dual theme cues",
        "- **Chrome** — icon menu, theme icon toggle, row-click edit",
        "",
        "**Mix mandate:** after scoring the 30, **blend the best concepts** "
        "into one coherent dashboard direction (2–5 structural principles). "
        "Do not ship a single Envato clone.",
        "",
    ]
    if errors:
        lines.append("## Fetch gaps")
        for e in errors:
            lines.append(f"- {e}")
        lines.append("")
    if len(sample) < count:
        lines.append(
            f"_WARNING: only {len(sample)} cards — below target {count}. "
            "Declare gap; do not invent refs._"
        )
        lines.append("")
    lines.append("## Evaluation set")
    lines.append("")
    for i, c in enumerate(sample, 1):
        lines.append(f"{i}. **{c.label}** — {c.url}")
    lines.append("")
    lines.append(
        "After review: write a short **mix notes** block (bullet principles), "
        "then apply via DX/UE/AF — structure, not hex/asset clone."
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Scout Envato admin templates")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true", help="List from primary catalog")
    g.add_argument(
        "--sample",
        type=int,
        metavar="N",
        help="Datetime-seeded sample of N templates (≥30 typical)",
    )
    p.add_argument("--limit", type=int, default=48, help="Max for --list")
    p.add_argument("--seed", default=None, help="Override YYYYMMDDHH seed")
    p.add_argument("--dry-run", action="store_true", help="Fixture pool, no network")
    args = p.parse_args()
    seed = args.seed or hour_seed()

    # Validate BEFORE building the pool: without --dry-run that step spends
    # real network requests, and an input invalid from the start must not
    # cost anything. (Review finding: these checks used to sit after it.)
    if args.limit < 1:
        raise SystemExit(f"--limit {args.limit}: deve essere ≥1")
    if not args.list and args.sample < 1:
        raise SystemExit(f"--sample {args.sample}: deve essere ≥1")

    if args.dry_run:
        pool = dry_run_pool()
        idx = catalog_index(seed, len(CATALOGS))
        errors: list[str] = []
    else:
        pool, idx, errors = build_pool(seed)

    if args.list:
        cards = pool[: args.limit]
        # If dry-run list without sample: still show
        print(f"# Envato admin-templates")
        print(f"Source: {CATALOGS[idx]}")
        print(f"Found: {len(cards)}")
        print()
        for i, c in enumerate(cards, 1):
            print(f"{i}. **{c.label}** — {c.url}")
        return 0 if cards else 1

    count = args.sample
    sample = sample_cards(pool, count, seed)
    print(
        render(
            sample,
            seed=seed,
            catalog_idx=idx,
            pool_size=len(pool),
            errors=errors,
            count=count,
        )
    )
    return 0 if len(sample) >= count else 1


if __name__ == "__main__":
    raise SystemExit(main())
