#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Build a few-hundred-item corpus of mobile web-app / PWA templates, with traits.

Why a separate corpus from `dashboard_corpus.py`: the breadth lever is different.
Under `admin-templates` the tag paths are the lever (48 disjoint cards each).
Under the mobile catalogs the tag path is **dead** — measured 2026-07-26:
`/web-templates/mobile/{dark,ios,tailwind}` return the *same* 48 items as
`/web-templates/mobile` (100% overlap). Breadth here comes from rotating many
sibling **category** catalogs, which are near-disjoint (0-8% overlap).

The catalog an item came from is kept as `origin`, but it is only promoted to a
**trait** for the catalogs measured to honour their own theme — see the table on
ENV_CATALOGS. `/gradient` and `/splash-screen` do not, so they widen the corpus
without stamping a label the item cannot back up.

Sources (public HTML / public API, stdlib only):
  env  Envato Elements mobile/PWA/graphic catalogs
  gh   GitHub repository search (PWA / mobile UI kits)

Usage:
    uv run scripts/mobile_corpus.py --build
    uv run scripts/mobile_corpus.py --build --target 300   # cap sugli Envato
    uv run scripts/mobile_corpus.py --stats
    uv run scripts/mobile_corpus.py --build --offline     # fixtures, no network
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

UA = "VesperFrontendTaste/1.0 (+local craft research; respectful)"
ENV_BASE = "https://elements.envato.com"
GH_API = "https://api.github.com/search/repositories"

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "assets" / "mobile-corpus.json"
CORPUS_VERSION = 1

# Measured 2026-07-26: every path below returned HTTP 200 with 48 SSR cards, and
# they are near-disjoint (0-8% shared) — that is the breadth lever.
#
# But a catalog name is NOT automatically a trait. Measured on the same pull, by
# checking how many labels actually confirm the catalog's theme:
#
#   food-delivery 100%  ·  fitness 93%  ·  mobile 90%  ·  pwa 68%  ·  ui-kits 62%
#   flutter 10%  ·  onboarding 5%  ·  splash-screen 6%  ·  gradient 0%  ·  ionic 0%
#
# The bottom row are shop-window labels: 48 generic templates each. They stay in
# the corpus because they are disjoint and widen it, but they must not stamp a
# trait — a ref tagged `gradient` that has no gradient is worse than no ref.
# `trusted=False` means: keep the item, infer traits from the label only.
ENV_CATALOGS: dict[str, tuple[str, str, bool]] = {
    # slug: (trait_bucket, trait_value, trusted)
    "mobile": ("graphic", "mobile", True),
    "mobile-app": ("graphic", "app", True),
    "pwa": ("graphic", "pwa", True),
    "progressive-web-app": ("graphic", "pwa", True),
    "mobile-website": ("graphic", "mobile-web", True),
    "ui-kits": ("graphic", "ui-kit", True),
    "app-landing-page": ("graphic", "app-landing", True),
    "food-delivery": ("domain", "food", True),
    "fitness": ("domain", "fitness", True),
    "banking": ("domain", "fintech", True),
    "travel": ("domain", "travel", True),
    # Breadth only — theme not honoured by the source (see measurements above).
    "splash-screen": ("graphic", "splash", False),
    "gradient": ("graphic", "gradient", False),
    "onboarding": ("graphic", "onboarding", False),
    "ionic": ("stack", "ionic", False),
    "flutter": ("stack", "flutter", False),
}

GH_QUERIES = [
    "pwa template",
    "mobile web app template",
    "progressive web app starter",
    "mobile ui kit html css",
    "ionic app template",
    "mobile first css framework",
]

ENV_ITEM_HREF = re.compile(r'href="(/([a-z0-9-]+)-([A-Z0-9]{6,}))"')
ENV_SKIP_PREFIX = ("/collections/", "/user/", "/photos/", "/sign-in", "/pricing", "/all-items")

STACK_HINTS = {
    "tailwind": "tailwind",
    "bootstrap": "bootstrap",
    "react": "react",
    "vue": "vue",
    "angular": "angular",
    "svelte": "svelte",
    "ionic": "ionic",
    "flutter": "flutter",
    "capacitor": "capacitor",
    "next": "next",
    "html": "html",
    "jquery": "jquery",
    "typescript": "typescript",
}

DOMAIN_HINTS = {
    "food": "food",
    "delivery": "food",
    "restaurant": "food",
    "grocery": "food",
    "fitness": "fitness",
    "workout": "fitness",
    "health": "health",
    "medical": "health",
    "doctor": "health",
    "bank": "fintech",
    "wallet": "fintech",
    "finance": "fintech",
    "crypto": "fintech",
    "pay": "fintech",
    "travel": "travel",
    "hotel": "travel",
    "booking": "booking",
    "flight": "travel",
    "shop": "ecommerce",
    "store": "ecommerce",
    "ecommerce": "ecommerce",
    "commerce": "ecommerce",
    "chat": "social",
    "social": "social",
    "music": "media",
    "video": "media",
    "podcast": "media",
    "news": "media",
    "learn": "education",
    "course": "education",
    "education": "education",
    "task": "productivity",
    "todo": "productivity",
    "note": "productivity",
    "real estate": "realestate",
    "property": "realestate",
    "taxi": "mobility",
    "ride": "mobility",
    "car": "mobility",
}

# The graphic vocabulary. Locutions, not single words: a template *named*
# «Splashes» or «Splashdash» is not a splash screen, and matching on `splash`
# alone made both look like one.
GRAPHIC_HINTS = {
    "splash screen": "splash",
    "splash page": "splash",
    "onboarding": "onboarding",
    "walkthrough": "onboarding",
    "gradient": "gradient",
    "mesh gradient": "gradient",
    "aurora": "gradient",
    "glassmorph": "glass",
    "neumorph": "neumorphism",
    "dark mode": "dark",
    "illustration": "illustration",
    "icon set": "icon-set",
    "animated": "animated",
}


@dataclass
class TemplateRef:
    source: str
    key: str
    label: str
    url: str
    origin: str
    stack: list[str] = field(default_factory=list)
    domain: list[str] = field(default_factory=list)
    graphic: list[str] = field(default_factory=list)


# Needles that must match a whole word. Only for those that live inside common
# unrelated words: `car` would otherwise tag `card`, `cart` and `carrent`, which
# is how 19 of 21 `mobility` hits turned out to be false.
# Everything else matches at a word start, so `bank` still catches `banking` and
# `pay` catches `payment` — a suffix is fine, a prefix is not.
WHOLE_WORD_ONLY = {"car"}


def _matches(needle: str, low: str) -> bool:
    """Word-start match; whole-word for the needles listed above.

    Plain substring was wrong in both directions: it tagged `shopping cart` as
    mobility, and the template *named* «Splashes» as a splash screen (the latter
    is handled by using locutions in GRAPHIC_HINTS).
    """
    pattern = (
        rf"\b{re.escape(needle)}\b" if needle in WHOLE_WORD_ONLY else rf"\b{re.escape(needle)}"
    )
    return re.search(pattern, low) is not None


def infer_traits(
    label: str, hint: tuple[str, str] | None = None
) -> tuple[list[str], list[str], list[str]]:
    """Traits from the label, plus the catalog hint when that catalog is trusted."""
    low = label.lower()
    stack: list[str] = []
    domain: list[str] = []
    graphic: list[str] = []
    for needle, value in STACK_HINTS.items():
        if _matches(needle, low) and value not in stack:
            stack.append(value)
    for needle, value in DOMAIN_HINTS.items():
        if _matches(needle, low) and value not in domain:
            domain.append(value)
    for needle, value in GRAPHIC_HINTS.items():
        if _matches(needle, low) and value not in graphic:
            graphic.append(value)
    if hint:
        bucket, value = hint
        target = {"stack": stack, "domain": domain, "graphic": graphic}.get(bucket)
        if target is not None and value not in target:
            target.append(value)
    return sorted(stack), sorted(domain) or ["generic"], sorted(graphic)


def fetch(url: str, timeout: float = 30.0) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} for {url}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error for {url}: {e}") from e


def parse_env(page: str, origin: str, hint: tuple[str, str] | None = None) -> list[TemplateRef]:
    out: list[TemplateRef] = []
    seen: set[str] = set()
    for path, slug, code in ENV_ITEM_HREF.findall(page):
        if code in seen or path.count("/") != 1:
            continue
        if any(bad in path for bad in ENV_SKIP_PREFIX):
            continue
        seen.add(code)
        label = slug.replace("-", " ").strip()
        stack, domain, graphic = infer_traits(label, hint)
        out.append(
            TemplateRef(
                source="env",
                key=code,
                label=label,
                url=f"{ENV_BASE}{path}",
                origin=origin,
                stack=stack,
                domain=domain,
                graphic=graphic,
            )
        )
    return out


def parse_github(payload: str, origin: str) -> list[TemplateRef]:
    data = json.loads(payload)
    out: list[TemplateRef] = []
    for repo in data.get("items", []):
        label = " ".join(
            filter(None, [repo.get("full_name", ""), repo.get("description") or ""])
        )[:200]
        stack, domain, graphic = infer_traits(label)
        out.append(
            TemplateRef(
                source="gh",
                key=str(repo.get("id")),
                label=label or repo.get("full_name", "repo"),
                url=repo.get("html_url", ""),
                origin=origin,
                stack=stack,
                domain=domain,
                graphic=graphic,
            )
        )
    return out


OFFLINE_FIXTURE = [
    ("mobile", "splash gradient mobile app kit"),
    ("splash-screen", "aurora splash screen starter"),
    ("gradient", "mesh gradient pwa ui kit"),
    ("onboarding", "onboarding walkthrough tailwind"),
    ("banking", "wallet fintech mobile app"),
    ("food-delivery", "food delivery react mobile"),
]


def build_offline() -> list[TemplateRef]:
    out: list[TemplateRef] = []
    for i, (origin, label) in enumerate(OFFLINE_FIXTURE):
        cat = ENV_CATALOGS.get(origin)
        hint = (cat[0], cat[1]) if cat and cat[2] else None
        stack, domain, graphic = infer_traits(label, hint)
        out.append(
            TemplateRef("env", f"OFFLINE{i:04d}", label, f"{ENV_BASE}/{label}-OFFLINE{i:04d}",
                        origin, stack, domain, graphic)
        )
    return out


def build(target: int, delay: float, offline: bool) -> dict:
    items: dict[str, TemplateRef] = {}
    gaps: list[str] = []

    if offline:
        for ref in build_offline():
            items[f"{ref.source}:{ref.key}"] = ref
    else:
        # Budget per source, not one shared cap: the Envato catalogs alone clear
        # any sane target, so a shared cap would silently never reach GitHub —
        # and GitHub is what carries real descriptions, hence usable domains.
        for slug, (bucket, value, trusted) in ENV_CATALOGS.items():
            if sum(1 for r in items.values() if r.source == "env") >= target:
                break
            url = f"{ENV_BASE}/web-templates/{slug}"
            try:
                page = fetch(url)
            except RuntimeError as e:
                gaps.append(f"{url} — {e}")
                continue
            hint = (bucket, value) if trusted else None
            for ref in parse_env(page, slug, hint):
                items.setdefault(f"{ref.source}:{ref.key}", ref)
            time.sleep(delay)

        for query in GH_QUERIES:
            qs = urllib.parse.urlencode(
                {"q": query, "sort": "stars", "order": "desc", "per_page": 50}
            )
            try:
                payload = fetch(f"{GH_API}?{qs}")
            except RuntimeError as e:
                gaps.append(f"github:{query} — {e}")
                continue
            for ref in parse_github(payload, f"gh:{query}"):
                items.setdefault(f"{ref.source}:{ref.key}", ref)
            time.sleep(delay)

    refs = list(items.values())
    counts = {
        "total": len(refs),
        "by_source": _tally(r.source for r in refs),
        "by_origin": _tally(r.origin for r in refs),
        "by_domain": _tally(d for r in refs for d in r.domain),
        "by_graphic": _tally(g for r in refs for g in r.graphic),
        "by_stack": _tally(s for r in refs for s in r.stack),
    }
    return {
        "version": CORPUS_VERSION,
        "surface": "mobile",
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": counts,
        "gaps": gaps,
        "items": [asdict(r) for r in refs],
    }


def _tally(values) -> dict[str, int]:
    out: dict[str, int] = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def show_stats(path: Path) -> int:
    if not path.exists():
        print(f"corpus assente: {path}\nesegui: uv run scripts/mobile_corpus.py --build")
        return 1
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    counts = data.get("counts", {})
    print(f"corpus mobile: {counts.get('total', 0)} item · built_at {data.get('built_at')}")
    for key in ("by_source", "by_origin", "by_graphic", "by_domain", "by_stack"):
        tally = counts.get(key) or {}
        if not tally:
            continue
        head = " · ".join(f"{k} {v}" for k, v in list(tally.items())[:10])
        print(f"  {key[3:]:<8} {head}")
    if data.get("gaps"):
        print(f"  gaps     {len(data['gaps'])} (dichiarali, non fingerli)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Mobile web-app / PWA template corpus")
    p.add_argument("--build", action="store_true", help="Fetch and write the corpus")
    p.add_argument("--stats", action="store_true", help="Show tallies of the saved corpus")
    p.add_argument("--target", type=int, default=700,
                   help="Cap on Envato items; GitHub queries always run")
    p.add_argument("--delay", type=float, default=1.2, help="Seconds between requests")
    p.add_argument("--offline", action="store_true", help="Fixtures only, no network")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--force", action="store_true",
                   help="Overwrite an existing corpus even if the new one is much smaller")
    args = p.parse_args()

    if args.stats and not args.build:
        return show_stats(args.out)
    if not args.build:
        p.print_help()
        return 1

    data = build(args.target, args.delay, args.offline)

    # A corpus this size costs ~20 minutes of throttled requests. `--offline`
    # (fixtures only) or a network hiccup can quietly shrink it to a handful of
    # items — measured against myself: a stray `--offline` test run overwrote
    # 866 real items with 6 fixtures, no warning. Below half the existing size,
    # refuse unless the caller means it.
    if not args.force and args.out.exists():
        try:
            existing = len(json.loads(args.out.read_text(encoding="utf-8")).get("items", []))
        except (json.JSONDecodeError, OSError, AttributeError):
            # AttributeError: valid JSON that is not a dict (e.g. a bare list).
            # A corrupt target must not crash the guard that protects it —
            # treat it as no corpus and let the build overwrite it.
            existing = 0
        if existing and data["counts"]["total"] < existing / 2:
            raise SystemExit(
                f"{args.out} ha {existing} item; questa build ne produce solo "
                f"{data['counts']['total']} (--offline? target basso? rete a metà?). "
                "Rifiuto di sovrascrivere silenziosamente — usa --force se è intenzionale."
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"corpus: {data['counts']['total']} item → {args.out}")
    if data["gaps"]:
        print("gap dichiarati:")
        for g in data["gaps"]:
            print(f"  - {g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
