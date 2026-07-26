#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Datetime-seeded sampling of ≥30 template/site cards for craft research.

Surfaces:
  marketing (default) — hero/landing; with --activity uses Envato vertical
                        catalogs (~48 each; 2+ cats ≈ 100 pool) as primary
  dashboard — Envato admin templates (primary) + mix
  mobile — Envato mobile / mobile-app / PWA catalogs (web app mobile);
           combine with --activity for vertical + mobile

Measured 2026-07-26: Dribbble `?q=` returns the same shot set for any query —
do NOT rely on DRB search for activity. Envato `/web-templates/{category}`
paths are disjoint and activity-true.

Stdlib only.

Usage:
    uv run scripts/hero_sample.py
    uv run scripts/hero_sample.py --activity ristorante --count 40
    uv run scripts/hero_sample.py --surface mobile --activity hotel
    uv run scripts/hero_sample.py --surface dashboard --count 30
    uv run scripts/hero_sample.py --seed 2026072513
    uv run scripts/hero_sample.py --dry-run --activity saas --surface mobile
"""

from __future__ import annotations

import argparse
import html as html_lib
import random
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

UA = "VesperFrontendTaste/1.0 (+local craft research; respectful)"
AWW_BASE = "https://www.awwwards.com"
DRB_BASE = "https://dribbble.com"
ENV_BASE = "https://elements.envato.com"

# Envato Elements admin catalogs (clean paths — no gclid/gad query noise).
# Canonical: https://elements.envato.com/web-templates/admin-templates
ENV_CATALOGS = [
    f"{ENV_BASE}/web-templates/admin-templates",
    f"{ENV_BASE}/web-templates/dashboard",
    f"{ENV_BASE}/web-templates/admin-dashboards",
]

# Mobile / PWA web-app catalogs (measured 2026-07-26: 48 each, near-disjoint).
# Kept to the core six so an hourly batch stays a handful of requests. Real
# breadth (16 catalogs, ~610 unique) is `mobile_corpus.py`'s job, not this one.
# Note the dead lever: `/web-templates/mobile/{tag}` returns the SAME 48 items as
# the base catalog — unlike admin-templates, the tag path is ignored here.
ENV_MOBILE_CATALOGS = [
    f"{ENV_BASE}/web-templates/mobile",
    f"{ENV_BASE}/web-templates/mobile-app",
    f"{ENV_BASE}/web-templates/pwa",
    f"{ENV_BASE}/web-templates/progressive-web-app",
    f"{ENV_BASE}/web-templates/mobile-website",
    f"{ENV_BASE}/web-templates/ui-kits",
]

# Activity → Envato web-templates category slugs (2+ → ~96–100 unique SSR cards).
# Aliases normalize IT/EN owner language to one key.
ACTIVITY_ALIASES: dict[str, str] = {
    "ristorante": "ristorante",
    "restaurant": "ristorante",
    "food": "ristorante",
    "trattoria": "ristorante",
    "hotel": "hotel",
    "albergo": "hotel",
    "hospitality": "hotel",
    "resort": "hotel",
    "saas": "saas",
    "software": "saas",
    "startup": "saas",
    "booking": "booking",
    "prenotazioni": "booking",
    "ecommerce": "ecommerce",
    "e-commerce": "ecommerce",
    "shop": "ecommerce",
    "negozio": "ecommerce",
    "fitness": "fitness",
    "palestra": "fitness",
    "medical": "medical",
    "medico": "medical",
    "clinic": "medical",
    "realestate": "realestate",
    "real-estate": "realestate",
    "immobiliare": "realestate",
    "agency": "agency",
    "agenzia": "agency",
    "portfolio": "portfolio",
    "studio": "portfolio",
    "landing": "landing",
    "generic": "landing",
}

ACTIVITY_ENVATO: dict[str, list[str]] = {
    "ristorante": ["restaurant", "food-and-drink"],
    "hotel": ["hotel", "hospitality"],
    "saas": ["saas", "landing-page"],
    "booking": ["booking", "hotel"],
    "ecommerce": ["ecommerce", "landing-page"],
    "fitness": ["fitness", "landing-page"],
    "medical": ["medical", "landing-page"],
    "realestate": ["real-estate", "landing-page"],
    "agency": ["agency", "landing-page"],
    "portfolio": ["portfolio", "landing-page"],
    "landing": ["landing-page", "responsive"],
}

ENV_ITEM_HREF = re.compile(r'href="(/([a-z0-9-]+)-([A-Z0-9]{6,}))"')

# Rotating source groups — hour seed picks which cluster to weight first.
SOURCE_GROUPS_MARKETING: list[list[tuple[str, str]]] = [
    [
        ("aww", f"{AWW_BASE}/websites/sites_of_the_day/"),
        ("aww", f"{AWW_BASE}/websites/nominees/"),
        ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('website template')}"),
        ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('landing page hero')}"),
    ],
    [
        ("aww", f"{AWW_BASE}/websites/best-of/"),
        ("aww", f"{AWW_BASE}/websites/sites_of_the_month/"),
        ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('hotel website')}"),
        ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('website template')}"),
    ],
    [
        ("aww", f"{AWW_BASE}/websites/"),
        ("aww", f"{AWW_BASE}/websites/sites_of_the_day/"),
        ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('fullscreen hero')}"),
        ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('parallax website')}"),
    ],
    [
        ("aww", f"{AWW_BASE}/websites/nominees/"),
        ("aww", f"{AWW_BASE}/websites/best-of/"),
        ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('carousel landing')}"),
        ("drb", f"{DRB_BASE}/shots"),
    ],
]

SOURCE_GROUPS_DASHBOARD: list[list[tuple[str, str]]] = [
    [
        ("env", ENV_CATALOGS[0]),
        ("env", ENV_CATALOGS[1]),
        ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('admin dashboard')}"),
        ("aww", f"{AWW_BASE}/websites/nominees/"),
    ],
    [
        ("env", ENV_CATALOGS[1]),
        ("env", ENV_CATALOGS[2]),
        ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('saas dashboard ui')}"),
        ("aww", f"{AWW_BASE}/websites/sites_of_the_day/"),
    ],
    [
        ("env", ENV_CATALOGS[2]),
        ("env", ENV_CATALOGS[0]),
        ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('crm dashboard')}"),
        ("aww", f"{AWW_BASE}/websites/best-of/"),
    ],
    [
        ("env", ENV_CATALOGS[0]),
        ("env", ENV_CATALOGS[2]),
        ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('admin panel template')}"),
        ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('user management ui')}"),
    ],
]

SOURCE_GROUPS_MOBILE: list[list[tuple[str, str]]] = [
    [
        ("env", ENV_MOBILE_CATALOGS[0]),
        ("env", ENV_MOBILE_CATALOGS[1]),
        ("env", ENV_MOBILE_CATALOGS[2]),
        ("aww", f"{AWW_BASE}/websites/nominees/"),
    ],
    [
        ("env", ENV_MOBILE_CATALOGS[1]),
        ("env", ENV_MOBILE_CATALOGS[2]),
        ("env", ENV_MOBILE_CATALOGS[3]),
        ("aww", f"{AWW_BASE}/websites/sites_of_the_day/"),
    ],
    [
        ("env", ENV_MOBILE_CATALOGS[2]),
        ("env", ENV_MOBILE_CATALOGS[0]),
        ("env", ENV_MOBILE_CATALOGS[3]),
        ("aww", f"{AWW_BASE}/websites/best-of/"),
    ],
    [
        ("env", ENV_MOBILE_CATALOGS[3]),
        ("env", ENV_MOBILE_CATALOGS[0]),
        ("env", ENV_MOBILE_CATALOGS[1]),
        ("aww", f"{AWW_BASE}/websites/nominees/"),
    ],
]

# Back-compat alias used by tests / callers that expect SOURCE_GROUPS
SOURCE_GROUPS = SOURCE_GROUPS_MARKETING

LENSES = {
    "marketing": [
        "- **Hero** — first-viewport composition, brand weight, media plane",
        "- **Carousel / layered media** — multi-slide or stacked hero media",
        "- **Parallax / depth** — scroll depth cues (not clone of JS)",
        "- **Type** — display vs body pairing cues worth chasing in fonts",
        "- **Palette novelty** — note hue family; do NOT copy hex; avoid repeating last job",
        "- **Activity match** — if --activity set, prefer vertical structure from Envato cats",
    ],
    "dashboard": [
        "- **Envato admin** — IA/nav, tables, KPI chrome from Elements admin-templates",
        "- **Tables / lists** — scanability; **row-click edit** (pointer); **icon-only row actions**; **round avatars**",
        "- **IA / nav** — icons + labels; **theme toggle = icon** (sun/moon), not text",
        "- **KPI / summary** — hierarchy without card spam",
        "- **Forms / dialogs** — create-edit patterns, focus states",
        "- **Motion product** — subtle enter/stagger (not hero parallax)",
        "- **Light + dark** — same family, dual token maps; note contrast in both",
        "- **Mix** — blend best concepts from the ≥30; do not clone one Envato item",
        "- **Palette novelty** — note hue family; do NOT copy hex; avoid repeating last job",
    ],
    "mobile": [
        "- **Mobile web app / PWA** — task-first chrome, not landing theatre",
        "- **Brand background** — is it a gradient, a solid + texture, or nothing? "
        "one background across the whole app, or a different one per screen (= decoration)?",
        "- **Splash / first frame** — does the app say its name, or does the shell just "
        "assemble? any white flash before content?",
        "- **App mark** — icon that survives a maskable crop and reads at 48px, "
        "not a shrunk wordmark",
        "- **Thumb zone** — primary CTA and tab bar in easy reach; ≥44px targets",
        "- **Bottom nav / app shell** — persistent wayfinding; one primary job per screen",
        "- **Lists / forms / states** — empty, loading, error; scanability on narrow width",
        "- **Safe areas** — notch/home-indicator padding; no edge-clipped controls",
        "- **Mix** — blend Envato mobile/PWA concepts; do not clone one template",
        "- **Activity** — if --activity set, vertical cats + mobile cats both in the pool",
        "- **Palette novelty** — note hue family; do NOT copy hex; avoid repeating last job",
        "- **Graphic craft gap** — Envato does not cover splash/background honestly "
        "(measured 6% and 0% fidelity): look at Figma Community by hand, or decide it",
    ],
}

FILLER_URLS_MARKETING: list[tuple[str, str]] = [
    ("aww", f"{AWW_BASE}/websites/sites_of_the_day/"),
    ("aww", f"{AWW_BASE}/websites/nominees/"),
    ("aww", f"{AWW_BASE}/websites/best-of/"),
    ("aww", f"{AWW_BASE}/websites/"),
    ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('website template')}"),
    ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('landing page')}"),
    ("drb", f"{DRB_BASE}/shots"),
]

FILLER_URLS_DASHBOARD: list[tuple[str, str]] = [
    ("env", ENV_CATALOGS[0]),
    ("env", ENV_CATALOGS[1]),
    ("env", ENV_CATALOGS[2]),
    ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('admin dashboard')}"),
    ("drb", f"{DRB_BASE}/shots?q={urllib.parse.quote('saas dashboard')}"),
    ("aww", f"{AWW_BASE}/websites/nominees/"),
    ("drb", f"{DRB_BASE}/shots"),
]

FILLER_URLS_MOBILE: list[tuple[str, str]] = [
    ("env", ENV_MOBILE_CATALOGS[0]),
    ("env", ENV_MOBILE_CATALOGS[1]),
    ("env", ENV_MOBILE_CATALOGS[2]),
    ("env", ENV_MOBILE_CATALOGS[3]),
    ("aww", f"{AWW_BASE}/websites/nominees/"),
    ("aww", f"{AWW_BASE}/websites/sites_of_the_day/"),
]

FILLER_URLS = FILLER_URLS_MARKETING

SITE_HREF = re.compile(r'href="(/sites/([a-zA-Z0-9_-]+)/?)"')
NEAR_TITLE = re.compile(
    r'href="(/sites/([a-zA-Z0-9_-]+)/?)"[^>]*>.*?'
    r'class="[^"]*avatar-name__title[^"]*"[^>]*>([^<]+)</',
    re.I | re.S,
)
SHOT_HREF = re.compile(r'href="(/shots/(\d+)-([^"?#]+))"')
WEB_HINT = re.compile(
    r"(?:^|[\s_-])(landing|website|web|dashboard|page|ui|ux|template|saas|"
    r"app|site|ecommerce|e-commerce|shop|hero|hotel|parallax|carousel|"
    r"mobile|pwa|restaurant|food)"
    r"(?:$|[\s_-])",
    re.I,
)


@dataclass(frozen=True)
class RefCard:
    source: str  # aww | drb | env
    key: str
    label: str
    url: str


def env_cat(slug: str) -> str:
    return f"{ENV_BASE}/web-templates/{slug}"


def normalize_activity(raw: str | None) -> str | None:
    if not raw:
        return None
    key = raw.strip().lower().replace(" ", "-")
    if key in ACTIVITY_ALIASES:
        return ACTIVITY_ALIASES[key]
    if key in ACTIVITY_ENVATO:
        return key
    # unknown: treat as landing + keep slug for logging
    return key if key else None


def is_known_activity(activity: str | None) -> bool:
    """Whether the vertical maps to real Envato categories.

    An unknown one still works — it falls back to the generic landing catalogs —
    but silently, and the batch header would only hint at it by listing
    `landing-page, responsive`. A typo would then read as a vertical batch that
    is nothing of the sort, so the caller says it out loud.
    """
    return bool(activity) and activity in ACTIVITY_ENVATO


def activity_env_urls(activity: str | None) -> list[str]:
    if not activity:
        return []
    slugs = ACTIVITY_ENVATO.get(activity, ACTIVITY_ENVATO["landing"])
    return [env_cat(s) for s in slugs]


def prefers_env_majority(surface: str, activity: str | None) -> bool:
    return surface in ("dashboard", "mobile") or bool(activity)


def surface_groups(
    surface: str, activity: str | None = None
) -> tuple[list[list[tuple[str, str]]], list[tuple[str, str]]]:
    """Return rotating primary groups + fillers for the surface/activity."""
    act_urls = activity_env_urls(activity)

    if surface == "dashboard":
        return SOURCE_GROUPS_DASHBOARD, FILLER_URLS_DASHBOARD

    if surface == "mobile":
        if act_urls:
            # Vertical + mobile catalogs → ~100+ pool when 2+2 categories fetch.
            groups: list[list[tuple[str, str]]] = []
            for i in range(4):
                cats = act_urls + ENV_MOBILE_CATALOGS
                rotated = cats[i % len(cats) :] + cats[: i % len(cats)]
                primary = [("env", u) for u in rotated[:4]]
                primary.append(("aww", f"{AWW_BASE}/websites/nominees/"))
                groups.append(primary)
            fillers = [("env", u) for u in act_urls + ENV_MOBILE_CATALOGS] + [
                ("aww", f"{AWW_BASE}/websites/sites_of_the_day/"),
                ("aww", f"{AWW_BASE}/websites/nominees/"),
            ]
            return groups, fillers
        return SOURCE_GROUPS_MOBILE, FILLER_URLS_MOBILE

    # marketing
    if act_urls:
        groups = []
        for i in range(4):
            rotated = act_urls[i % len(act_urls) :] + act_urls[: i % len(act_urls)]
            # pad with landing-page / responsive for breadth toward ~100
            extra = [env_cat("landing-page"), env_cat("responsive")]
            pool_urls = rotated + [u for u in extra if u not in rotated]
            primary = [("env", u) for u in pool_urls[:3]]
            primary.append(("aww", f"{AWW_BASE}/websites/sites_of_the_day/"))
            groups.append(primary)
        fillers = [("env", u) for u in act_urls] + [
            ("env", env_cat("landing-page")),
            ("aww", f"{AWW_BASE}/websites/nominees/"),
            ("aww", f"{AWW_BASE}/websites/best-of/"),
            ("aww", f"{AWW_BASE}/websites/"),
        ]
        return groups, fillers

    return SOURCE_GROUPS_MARKETING, FILLER_URLS_MARKETING


def hour_seed(when: datetime | None = None) -> str:
    when = when or datetime.now()
    return when.strftime("%Y%m%d%H")


def group_index(seed: str, n_groups: int = 4) -> int:
    digits = "".join(ch for ch in seed if ch.isdigit())
    if not digits:
        return hash(seed) % n_groups
    return int(digits) % n_groups


def sample_group(
    items: list[RefCard], count: int, seed: str, surface: str = "marketing",
    activity: str | None = None,
) -> list[RefCard]:
    """Shuffle with seed; mix sources. Env majority when dashboard/mobile/activity."""
    count = max(0, count)
    rng = random.Random(seed)
    by = {
        "aww": [c for c in items if c.source == "aww"],
        "drb": [c for c in items if c.source == "drb"],
        "env": [c for c in items if c.source == "env"],
    }
    for v in by.values():
        rng.shuffle(v)

    if prefers_env_majority(surface, activity) and by["env"]:
        take_env = min(len(by["env"]), max(count // 2, min(count, 15)))
        # With activity/mobile, push Envato higher (≥⅔ when available)
        if surface == "mobile" or activity:
            take_env = min(len(by["env"]), max((count * 2) // 3, min(count, 20)))
        rest_n = count - take_env
        others = by["drb"] + by["aww"]
        rng.shuffle(others)
        mixed = by["env"][:take_env] + others[:rest_n]
        rng.shuffle(mixed)
        if len(mixed) < count:
            leftover = [c for c in items if c not in mixed]
            rng.shuffle(leftover)
            mixed.extend(leftover[: count - len(mixed)])
        return mixed[:count]

    aww, drb = by["aww"], by["drb"]
    if not aww or not drb:
        pool = list(items)
        rng.shuffle(pool)
        return pool[:count]
    minority_target = min(len(aww), len(drb), max(count // 3, 1))
    if len(drb) <= len(aww):
        take_drb = minority_target
        take_aww = min(len(aww), count - take_drb)
        take_drb = min(len(drb), count - take_aww)
    else:
        take_aww = minority_target
        take_drb = min(len(drb), count - take_aww)
        take_aww = min(len(aww), count - take_drb)
    mixed = aww[:take_aww] + drb[:take_drb]
    rng.shuffle(mixed)
    if len(mixed) < count:
        rest = [c for c in items if c not in mixed]
        rng.shuffle(rest)
        mixed.extend(rest[: count - len(mixed)])
    return mixed[:count]


def fetch(url: str, timeout: float = 25.0) -> str:
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


def parse_aww(page: str) -> list[RefCard]:
    labeled: dict[str, str] = {}
    for _path, slug, label in NEAR_TITLE.findall(page):
        labeled[slug] = html_lib.unescape(label.strip())
    out: list[RefCard] = []
    seen: set[str] = set()
    for path, slug in SITE_HREF.findall(page):
        if slug in seen:
            continue
        seen.add(slug)
        norm = path if path.endswith("/") else path + "/"
        out.append(
            RefCard(
                source="aww",
                key=slug,
                label=labeled.get(slug, slug.replace("-", " ")),
                url=f"{AWW_BASE}{norm}",
            )
        )
    return out


def parse_drb(page: str, prefer_web: bool = True) -> list[RefCard]:
    cards: list[RefCard] = []
    seen: set[str] = set()
    for path, shot_id, slug in SHOT_HREF.findall(page):
        if shot_id in seen:
            continue
        seen.add(shot_id)
        label = html_lib.unescape(slug.replace("-", " ").strip())
        cards.append(
            RefCard(
                source="drb",
                key=shot_id,
                label=label,
                url=f"{DRB_BASE}{path}",
            )
        )
    if prefer_web:
        preferred = [c for c in cards if WEB_HINT.search(c.label)]
        if preferred:
            cards = preferred
    return cards


def parse_env(page: str) -> list[RefCard]:
    """Parse Envato Elements item cards from admin/dashboard/vertical catalogs."""
    out: list[RefCard] = []
    seen: set[str] = set()
    for path, slug, code in ENV_ITEM_HREF.findall(page):
        if code in seen:
            continue
        if path.count("/") != 1:
            continue
        if any(
            bad in path
            for bad in ("/web-templates", "/graphic-templates", "/presentation", "/wordpress")
        ):
            continue
        seen.add(code)
        out.append(
            RefCard(
                source="env",
                key=code,
                label=slug.replace("-", " ").strip(),
                url=f"{ENV_BASE}{path}",
            )
        )
    return out


def merge_unique(pool: list[RefCard], more: list[RefCard]) -> int:
    """Append unseen cards; return how many were added."""
    keys = {(c.source, c.key) for c in pool}
    added = 0
    for c in more:
        k = (c.source, c.key)
        if k in keys:
            continue
        keys.add(k)
        pool.append(c)
        added += 1
    return added


def build_pool(
    seed: str,
    min_pool: int,
    fetch_fn=fetch,
    surface: str = "marketing",
    activity: str | None = None,
) -> tuple[list[RefCard], int, list[str]]:
    """Fetch rotating group + fillers until min_pool or sources exhausted."""
    groups, fillers = surface_groups(surface, activity)
    gidx = group_index(seed, len(groups))
    primary = groups[gidx]
    errors: list[str] = []
    pool: list[RefCard] = []

    def ingest(kind: str, url: str) -> None:
        try:
            page = fetch_fn(url)
        except RuntimeError as e:
            errors.append(str(e))
            return
        if kind == "aww":
            merge_unique(pool, parse_aww(page))
        elif kind == "env":
            merge_unique(pool, parse_env(page))
        else:
            merge_unique(pool, parse_drb(page, prefer_web=True))

    for kind, url in primary:
        ingest(kind, url)

    # Aim for ~2× count when activity/mobile (breadth toward ~100 pool)
    target_pool = max(min_pool * 2, min_pool + 10)
    if prefers_env_majority(surface, activity):
        target_pool = max(target_pool, 90)

    for kind, url in fillers:
        if len(pool) >= target_pool:
            if prefers_env_majority(surface, activity):
                if any(c.source == "env" for c in pool):
                    break
            elif any(c.source == "drb" for c in pool):
                break
        if (kind, url) in {(k, u) for k, u in primary}:
            continue
        ingest(kind, url)

    return pool, gidx, errors


def render_markdown(
    sample: list[RefCard],
    *,
    seed: str,
    group_idx: int,
    pool_size: int,
    errors: list[str],
    count: int,
    surface: str = "marketing",
    activity: str | None = None,
) -> str:
    groups, _ = surface_groups(surface, activity)
    lenses = LENSES.get(surface, LENSES["marketing"])
    if surface == "dashboard":
        title = "Dashboard inspire batch (Envato admin + product/UI)"
    elif surface == "mobile":
        title = "Mobile web-app inspire batch (Envato mobile/PWA)"
    else:
        title = "Hero inspire batch (template sample)"
    if activity:
        title += f" — activity `{activity}`"

    if surface == "dashboard":
        keep_note = (
            "After review: **mix the best concepts** from the ≥30 into 2–5 structural "
            "principles for DX/UE/AF (Envato admin chrome + tables/KPI — structure, "
            "not clone of one template / not palette hex)."
        )
    elif surface == "mobile":
        keep_note = (
            "After review: keep **2–5** structural principles for a **mobile web app** "
            "(task shell, thumb nav, states — not landing theatre; not clone)."
        )
    else:
        keep_note = (
            "After review: keep **2–5** structural refs for DX/UE/AF "
            "(hero impact only — structure, not palette clone)."
        )

    tag_map = {"aww": "Awwwards", "drb": "Dribbble", "env": "Envato"}
    lines = [
        f"# {title}",
        f"Surface: `{surface}`",
    ]
    if activity:
        lines.append(f"Activity: `{activity}`")
        cats = ACTIVITY_ENVATO.get(activity, ACTIVITY_ENVATO["landing"])
        lines.append(f"Envato categories: {', '.join('`' + c + '`' for c in cats)}")
        if not is_known_activity(activity):
            lines.append(
                f"> **attenzione** — `{activity}` non è una vertical nota: il batch usa i "
                f"cataloghi **generici** di landing, non è tipizzato. "
                f"Note: {list_activities()}"
            )
    if surface == "mobile":
        lines.append(
            "Mobile catalogs: `mobile`, `mobile-app`, `pwa`, `progressive-web-app`, "
            "`mobile-website`, `ui-kits`"
        )
    lines.extend(
        [
            f"Seed (YYYYMMDDHH): `{seed}`",
            f"Source group index: {group_idx} / {len(groups)}",
            f"Pool size: {pool_size} → evaluating: {len(sample)} (target ≥{count})",
            "",
        ]
    )
    if surface == "dashboard":
        lines.append(f"Envato canonical: {ENV_CATALOGS[0]}")
        lines.append("")
    if activity or surface == "mobile":
        lines.append(
            "_Note: Dribbble search is not activity-true (same cards any query). "
            "Vertical signal comes from Envato category paths._"
        )
        lines.append("")
    lines.extend(
        [
            "Lenses for each ref (score mentally, do not invent unseen details):",
            *lenses,
            "",
        ]
    )
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
        tag = tag_map.get(c.source, c.source)
        lines.append(f"{i}. **[{tag}] {c.label}** — {c.url}")
    lines.append("")
    lines.append(keep_note)
    return "\n".join(lines)


def dry_run_pool(surface: str = "marketing", activity: str | None = None) -> list[RefCard]:
    """Synthetic pool for offline tests."""
    base = [
        RefCard("aww", f"site-{i}", f"Site {i}", f"{AWW_BASE}/sites/site-{i}/")
        for i in range(1, 41)
    ] + [
        RefCard(
            "drb",
            f"{1000 + i}",
            f"Landing Page Template {i}",
            f"{DRB_BASE}/shots/{1000 + i}-Landing-Page-Template-{i}",
        )
        for i in range(1, 21)
    ]
    if surface == "dashboard":
        return [
            RefCard(
                "env",
                f"ENV{i:04d}",
                f"admin dashboard template {i}",
                f"{ENV_BASE}/admin-dashboard-template-{i}-ENV{i:04d}",
            )
            for i in range(1, 40)
        ] + base[:20]
    if surface == "mobile" or activity:
        prefix = "mobile pwa" if surface == "mobile" else (activity or "landing")
        env = [
            RefCard(
                "env",
                f"MOB{i:04d}",
                f"{prefix} html template {i}",
                f"{ENV_BASE}/{prefix.replace(' ', '-')}-html-template-{i}-MOB{i:04d}",
            )
            for i in range(1, 80)
        ]
        return env + base[:15]
    return base


def list_activities() -> str:
    keys = sorted(ACTIVITY_ENVATO.keys())
    return ", ".join(keys)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Sample ≥30 template sites with datetime hour seed"
    )
    p.add_argument(
        "--surface",
        choices=("marketing", "dashboard", "mobile"),
        default="marketing",
        help="marketing=landing; dashboard=admin; mobile=web-app mobile/PWA",
    )
    p.add_argument(
        "--activity",
        default=None,
        help=(
            "Vertical for Envato categories (ristorante, hotel, saas, …). "
            f"Known: {list_activities()}"
        ),
    )
    p.add_argument(
        "--count",
        type=int,
        default=30,
        help="How many refs to evaluate (default 30; 40–50 ok; corpus breadth separate)",
    )
    p.add_argument(
        "--seed",
        default=None,
        help="Override seed (default: current YYYYMMDDHH)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Use fixture pool; no network",
    )
    p.add_argument(
        "--list-activities",
        action="store_true",
        help="Print known activity keys and Envato categories, then exit",
    )
    args = p.parse_args()

    if args.list_activities:
        for key, slugs in sorted(ACTIVITY_ENVATO.items()):
            print(f"{key}: {', '.join(slugs)}")
        print("mobile catalogs: mobile, mobile-app, pwa, progressive-web-app")
        return 0

    # Was `max(1, args.count)`: silent — `--count 0` and negatives quietly
    # became 1, no sign the value was out of range.
    if args.count < 1:
        raise SystemExit(f"--count {args.count}: deve essere ≥1")
    count = args.count
    seed = args.seed or hour_seed()
    surface = args.surface
    activity = normalize_activity(args.activity)
    groups, _ = surface_groups(surface, activity)

    if args.dry_run:
        pool = dry_run_pool(surface, activity)
        gidx = group_index(seed, len(groups))
        errors: list[str] = []
    else:
        pool, gidx, errors = build_pool(
            seed, min_pool=count, surface=surface, activity=activity
        )

    sample = sample_group(
        pool, count, seed, surface=surface, activity=activity
    )
    print(
        render_markdown(
            sample,
            seed=seed,
            group_idx=gidx,
            pool_size=len(pool),
            errors=errors,
            count=count,
            surface=surface,
            activity=activity,
        )
    )
    if len(sample) < count:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
