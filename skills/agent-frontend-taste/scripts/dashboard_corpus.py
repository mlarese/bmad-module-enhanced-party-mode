#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Build a few-hundred-item corpus of dashboard/admin templates, with traits.

Why: `hero_sample.py --surface dashboard` samples ~30 refs per hour but keeps no
memory of the field. The corpus is the persistent layer under it: hundreds of
real admin templates, tagged by stack / domain / style, so `dashboard_recipe.py`
can weight its random picks against what the field actually does.

Sources (public HTML / public API, stdlib only):
  env  Envato Elements admin catalogs + `all-items?terms=` searches
  gh   GitHub repository search (dashboard templates / admin UI kits)

Envato `?page=N` does not change the SSR item set — breadth comes from rotating
catalogs, tag paths and search terms instead.

Usage:
    uv run scripts/dashboard_corpus.py --build
    uv run scripts/dashboard_corpus.py --build --target 400 --out assets/dashboard-corpus.json
    uv run scripts/dashboard_corpus.py --stats
    uv run scripts/dashboard_corpus.py --build --offline     # fixtures, no network
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

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "assets" / "dashboard-corpus.json"
CORPUS_VERSION = 1

ENV_CATALOGS = [
    f"{ENV_BASE}/web-templates/admin-templates",
    f"{ENV_BASE}/web-templates/dashboard",
    f"{ENV_BASE}/web-templates/admin-dashboards",
]

# Tag paths under admin-templates are the breadth lever: 48 SSR cards each and
# largely disjoint (measured 2026-07-25: 22 tags -> 560 unique items). The tag
# itself is also a reliable trait, better than guessing from a short slug.
# `all-items?terms=` is NOT a lever: the term is ignored server-side (same 110
# cards for any query), so it is fetched once as generic filler.
ENV_TAGS: dict[str, tuple[str, str]] = {
    "bootstrap": ("stack", "bootstrap"),
    "tailwind": ("stack", "tailwind"),
    "react": ("stack", "react"),
    "vue": ("stack", "vue"),
    "angular": ("stack", "angular"),
    "svelte": ("stack", "svelte"),
    "nextjs": ("stack", "next"),
    "nuxt": ("stack", "nuxt"),
    "laravel": ("stack", "laravel"),
    "php": ("stack", "php"),
    "jquery": ("stack", "jquery"),
    "html": ("stack", "html"),
    "typescript": ("stack", "typescript"),
    "material-design": ("style", "material"),
    "dark": ("style", "dark"),
    "minimal": ("style", "minimal"),
    "responsive": ("style", "responsive"),
    "multipurpose": ("style", "multipurpose"),
    "crm": ("domain", "crm"),
    "analytics": ("domain", "analytics"),
    "ecommerce": ("domain", "ecommerce"),
    "saas": ("domain", "saas"),
}

GH_QUERIES = [
    "admin dashboard template",
    "dashboard ui kit",
    "admin panel template html",
    "tailwind admin dashboard",
    "react admin dashboard template",
    "bootstrap admin template",
]

ENV_ITEM_HREF = re.compile(r'href="(/([a-z0-9-]+)-([A-Z0-9]{6,}))"')
ENV_SKIP_PREFIX = (
    "/web-templates",
    "/graphic-templates",
    "/presentation",
    "/wordpress",
    "/all-items",
)

# label keyword -> trait. Order irrelevant; all matches are kept.
STACK_TAGS: dict[str, tuple[str, ...]] = {
    "bootstrap": ("bootstrap", "bs5", "bootstrap5"),
    "tailwind": ("tailwind", "tailwindcss"),
    "react": ("react", "reactjs"),
    "next": ("next", "nextjs"),
    "vue": ("vue", "vuejs"),
    "nuxt": ("nuxt",),
    "angular": ("angular",),
    "svelte": ("svelte", "sveltekit"),
    "laravel": ("laravel",),
    "django": ("django",),
    "dotnet": ("asp", "blazor", "net core", "netcore", "mvc"),
    "material": ("material", "mui"),
    "html": ("html", "html5", "static"),
}

DOMAIN_TAGS: dict[str, tuple[str, ...]] = {
    "crm": ("crm", "customer", "lead", "sales"),
    "hr": ("hr", "human resource", "payroll", "employee", "recruit"),
    "analytics": ("analytic", "analytics", "report", "bi ", "statistic", "metrics"),
    "saas": ("saas", "startup", "subscription"),
    "pos": ("pos", "point of sale", "cashier", "inventory", "stock"),
    "medical": ("medical", "hospital", "clinic", "health", "doctor", "patient"),
    "school": ("school", "lms", "course", "student", "education", "university"),
    "ecommerce": ("ecommerce", "e commerce", "shop", "store", "order", "product"),
    "crypto": ("crypto", "nft", "token", "wallet", "blockchain", "trading"),
    "logistics": ("logistic", "delivery", "fleet", "shipping", "transport", "courier"),
    "project": ("project", "task", "kanban", "agile", "team", "workflow"),
    "booking": ("booking", "rental", "reservation", "hotel", "travel", "ticket"),
    "iot": ("iot", "smart home", "device", "sensor", "energy", "monitor"),
    "finance": ("finance", "financial", "bank", "invoice", "accounting", "fintech", "billing"),
    "support": ("support", "helpdesk", "ticketing", "chat", "crm ticket"),
    "realestate": ("real estate", "property", "estate", "rent"),
    "restaurant": ("restaurant", "food", "cafe", "menu", "kitchen"),
    "fitness": ("fitness", "gym", "sport", "workout", "yoga"),
}

STYLE_TAGS: dict[str, tuple[str, ...]] = {
    "dark": ("dark",),
    "light": ("light",),
    "minimal": ("minimal", "clean", "simple"),
    "modern": ("modern", "creative", "premium"),
    "glass": ("glass", "glassmorph", "blur"),
    "neumorphic": ("neumorph", "soft ui"),
    "bento": ("bento", "grid"),
    "multipurpose": ("multipurpose", "multi purpose", "all in one", "bundle"),
    "corporate": ("corporate", "business", "enterprise"),
    "rtl": ("rtl", "arabic"),
    "responsive": ("responsive", "mobile"),
}


@dataclass(frozen=True)
class TemplateRef:
    source: str  # env | gh
    key: str
    label: str
    url: str
    origin: str  # which catalog / term / query produced it
    stack: list[str] = field(default_factory=list)
    domain: list[str] = field(default_factory=list)
    style: list[str] = field(default_factory=list)


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower())


def match_tags(label: str, table: dict[str, tuple[str, ...]]) -> list[str]:
    hay = f" {norm(label)} "
    return sorted({tag for tag, keys in table.items() if any(k in hay for k in keys)})


def infer_traits(
    label: str, hint: tuple[str, str] | None = None
) -> tuple[list[str], list[str], list[str]]:
    """Traits from the label, plus the catalog tag that produced the card."""
    stack = match_tags(label, STACK_TAGS)
    domain = match_tags(label, DOMAIN_TAGS)
    style = match_tags(label, STYLE_TAGS)
    if hint:
        kind, value = hint
        bucket = {"stack": stack, "domain": domain, "style": style}[kind]
        if value not in bucket:
            bucket.append(value)
    return sorted(stack), sorted(domain) or ["generic"], sorted(style)


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


def parse_env(
    page: str, origin: str, hint: tuple[str, str] | None = None
) -> list[TemplateRef]:
    out: list[TemplateRef] = []
    seen: set[str] = set()
    for path, slug, code in ENV_ITEM_HREF.findall(page):
        if code in seen or path.count("/") != 1:
            continue
        if any(bad in path for bad in ENV_SKIP_PREFIX):
            continue
        seen.add(code)
        label = slug.replace("-", " ").strip()
        stack, domain, style = infer_traits(label, hint)
        out.append(
            TemplateRef(
                source="env",
                key=code,
                label=label,
                url=f"{ENV_BASE}{path}",
                origin=origin,
                stack=stack,
                domain=domain,
                style=style,
            )
        )
    return out


def parse_github(payload: str, origin: str) -> list[TemplateRef]:
    data = json.loads(payload)
    out: list[TemplateRef] = []
    for repo in data.get("items", []):
        label = " ".join(
            filter(None, [repo.get("full_name", ""), repo.get("description") or ""])
        )
        topics = repo.get("topics") or []
        stack, domain, style = infer_traits(f"{label} {' '.join(topics)}")
        out.append(
            TemplateRef(
                source="gh",
                key=str(repo.get("id")),
                label=(repo.get("full_name") or "").strip(),
                url=repo.get("html_url", ""),
                origin=origin,
                stack=stack,
                domain=domain,
                style=style,
            )
        )
    return out


def merge_unique(pool: list[TemplateRef], more: list[TemplateRef]) -> int:
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


def surfaces() -> list[tuple[str, str, str, tuple[str, str] | None]]:
    """(kind, url, origin, trait_hint) queue — catalogs, tags, then GitHub."""
    q: list[tuple[str, str, str, tuple[str, str] | None]] = []
    for url in ENV_CATALOGS:
        q.append(("env", url, url.rsplit("/", 1)[-1], None))
    for tag, hint in ENV_TAGS.items():
        url = f"{ENV_BASE}/web-templates/admin-templates/{tag}"
        q.append(("env", url, f"tag:{tag}", hint))
    q.append(("env", f"{ENV_BASE}/all-items?terms=admin+dashboard", "all-items", None))
    for query in GH_QUERIES:
        url = (
            f"{GH_API}?q={urllib.parse.quote(query)}"
            "&per_page=100&sort=stars&order=desc"
        )
        q.append(("gh", url, f"gh:{query}", None))
    return q


def build_corpus(
    target: int,
    fetch_fn=fetch,
    pause: float = 0.7,
) -> tuple[list[TemplateRef], list[str]]:
    pool: list[TemplateRef] = []
    errors: list[str] = []
    for kind, url, origin, hint in surfaces():
        if len(pool) >= target:
            break
        try:
            page = fetch_fn(url)
        except RuntimeError as e:
            errors.append(str(e))
            continue
        try:
            cards = (
                parse_env(page, origin, hint)
                if kind == "env"
                else parse_github(page, origin)
            )
        except (ValueError, json.JSONDecodeError) as e:
            errors.append(f"Parse error for {url}: {e}")
            continue
        added = merge_unique(pool, cards)
        print(f"  +{added:4d} (pool {len(pool):4d})  {origin}", flush=True)
        if pause:
            time.sleep(pause)
    return pool, errors


def tally(items: list[TemplateRef], attr: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for it in items:
        for v in getattr(it, attr) or []:
            counts[v] = counts.get(v, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def corpus_payload(items: list[TemplateRef], errors: list[str]) -> dict:
    by_source: dict[str, int] = {}
    for it in items:
        by_source[it.source] = by_source.get(it.source, 0) + 1
    return {
        "version": CORPUS_VERSION,
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "counts": {
            "total": len(items),
            "by_source": by_source,
            "by_stack": tally(items, "stack"),
            "by_domain": tally(items, "domain"),
            "by_style": tally(items, "style"),
        },
        "fetch_gaps": errors,
        "items": [asdict(it) for it in items],
    }


def load_corpus(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def offline_pool() -> list[TemplateRef]:
    """Fixture corpus for tests — same shape, no network."""
    seeds = [
        ("bootstrap crm admin dashboard template", "env"),
        ("tailwind analytics dashboard dark", "env"),
        ("react saas admin panel minimal", "env"),
        ("vue hospital medical dashboard", "env"),
        ("laravel pos inventory admin", "gh"),
        ("angular logistics fleet dashboard", "gh"),
        ("html project management kanban admin", "env"),
        ("next finance banking dashboard modern", "gh"),
    ]
    out: list[TemplateRef] = []
    for i in range(1, 41):
        label_base, source = seeds[i % len(seeds)]
        label = f"{label_base} {i}"
        stack, domain, style = infer_traits(label)
        out.append(
            TemplateRef(
                source=source,
                key=f"FIX{i:04d}",
                label=label,
                url=f"https://example.invalid/{i}",
                origin="fixture",
                stack=stack,
                domain=domain,
                style=style,
            )
        )
    return out


def print_stats(payload: dict) -> None:
    counts = payload.get("counts", {})
    print(f"# Dashboard corpus — {counts.get('total', 0)} templates")
    print(f"built_at: {payload.get('built_at')}")
    print(f"by_source: {counts.get('by_source')}")
    print()
    for key, title in (
        ("by_domain", "Domini"),
        ("by_stack", "Stack"),
        ("by_style", "Stili dichiarati nel titolo"),
    ):
        table = counts.get(key, {})
        total = counts.get("total", 0) or 1
        print(f"## {title}")
        for name, n in list(table.items())[:14]:
            print(f"  {name:14s} {n:4d}  {100 * n / total:4.1f}%")
        print()
    gaps = payload.get("fetch_gaps") or []
    if gaps:
        print("## Fetch gaps")
        for g in gaps:
            print(f"- {g}")


def main() -> int:
    p = argparse.ArgumentParser(description="Build/inspect the dashboard template corpus")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--build", action="store_true", help="Fetch sources and write the corpus")
    g.add_argument("--stats", action="store_true", help="Print stats from the stored corpus")
    p.add_argument("--target", type=int, default=700, help="Stop once pool reaches N (default 700)")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Corpus JSON path")
    p.add_argument("--offline", action="store_true", help="Fixture pool, no network")
    p.add_argument("--force", action="store_true",
                   help="Overwrite an existing corpus even if the new one is much smaller")
    args = p.parse_args()

    if args.stats:
        if not args.out.exists():
            print(f"No corpus at {args.out} — run --build first.")
            return 1
        print_stats(load_corpus(args.out))
        return 0

    if args.offline:
        items, errors = offline_pool(), []
    else:
        print(f"Building corpus (target {args.target})…")
        items, errors = build_corpus(args.target)

    payload = corpus_payload(items, errors)

    # Same guard as mobile_corpus.py: a stray --offline or a low --target must
    # not silently wipe out a corpus that cost real requests to build.
    if not args.force and args.out.exists():
        try:
            existing = len(json.loads(args.out.read_text(encoding="utf-8")).get("items", []))
        except (json.JSONDecodeError, OSError, AttributeError):
            # AttributeError: valid JSON that is not a dict (e.g. a bare list).
            # A corrupt target must not crash the guard that protects it —
            # treat it as no corpus and let the build overwrite it.
            existing = 0
        if existing and len(items) < existing / 2:
            raise SystemExit(
                f"{args.out} ha {existing} item; questa build ne produce solo "
                f"{len(items)} (--offline? target basso? rete a metà?). "
                "Rifiuto di sovrascrivere silenziosamente — usa --force se è intenzionale."
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print()
    print_stats(payload)
    print()
    print(f"Written: {args.out}")
    return 0 if items else 1


if __name__ == "__main__":
    raise SystemExit(main())
