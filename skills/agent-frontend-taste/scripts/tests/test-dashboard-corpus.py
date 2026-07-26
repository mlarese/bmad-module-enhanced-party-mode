# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for dashboard_corpus.py — run: uv run scripts/tests/test-dashboard-corpus.py"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "dashboard_corpus.py"


def load():
    spec = importlib.util.spec_from_file_location("dashboard_corpus", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dashboard_corpus"] = mod
    spec.loader.exec_module(mod)
    return mod


ENV_PAGE = """
<a href="/web-templates/admin-templates">catalogo</a>
<a href="/boron-admin-dashboard-template-5UY28VR">boron</a>
<a href="/tailwind-crm-admin-dark-NFKUHKU">tailwind crm</a>
<a href="/boron-admin-dashboard-template-5UY28VR">duplicato</a>
<a href="/graphic-templates/flyers-XYZABC1">scarta</a>
"""

GH_PAGE = json.dumps(
    {
        "items": [
            {
                "id": 42,
                "full_name": "acme/vue-hospital-dashboard",
                "description": "Vue medical admin panel",
                "topics": ["dashboard", "vue"],
                "html_url": "https://github.com/acme/vue-hospital-dashboard",
            }
        ]
    }
)


def main() -> int:
    fails = 0
    mod = load()

    stack, domain, style = mod.infer_traits("tailwind css crm admin dashboard dark")
    if "tailwind" not in stack or "crm" not in domain or "dark" not in style:
        print("FAIL: infer_traits", stack, domain, style)
        fails += 1
    else:
        print("PASS: infer_traits reads stack/domain/style from the label")

    _s, d_generic, _y = mod.infer_traits("boron admin template")
    if d_generic != ["generic"]:
        print("FAIL: expected generic domain fallback", d_generic)
        fails += 1
    else:
        print("PASS: unknown domain falls back to generic")

    # The catalog tag that produced the card is a trait too.
    _s2, d_hint, _y2 = mod.infer_traits("boron admin template", ("domain", "crm"))
    if "crm" not in d_hint or "generic" in d_hint:
        print("FAIL: tag hint not merged", d_hint)
        fails += 1
    else:
        print("PASS: catalog tag hint becomes a trait")

    cards = mod.parse_env(ENV_PAGE, "tag:crm", ("domain", "crm"))
    keys = [c.key for c in cards]
    if keys != ["5UY28VR", "NFKUHKU"]:
        print("FAIL: parse_env", keys)
        fails += 1
    elif any("crm" not in c.domain for c in cards):
        print("FAIL: parse_env dropped the hint", [c.domain for c in cards])
        fails += 1
    else:
        print("PASS: parse_env dedupes, skips category paths, keeps the hint")

    gh = mod.parse_github(GH_PAGE, "gh:test")
    if len(gh) != 1 or gh[0].source != "gh" or "medical" not in gh[0].domain:
        print("FAIL: parse_github", gh)
        fails += 1
    else:
        print("PASS: parse_github maps repos with traits")

    def fake_fetch(url):
        return GH_PAGE if "api.github.com" in url else ENV_PAGE

    pool, errors = mod.build_corpus(target=5, fetch_fn=fake_fetch, pause=0)
    if errors:
        print("FAIL: unexpected errors", errors)
        fails += 1
    elif len(pool) != 3:
        # 2 unique Envato items + 1 GitHub repo, deduped across every surface
        print("FAIL: expected 3 unique cards", len(pool), [c.key for c in pool])
        fails += 1
    else:
        print("PASS: build_corpus dedupes across surfaces")

    def failing_fetch(url):
        raise RuntimeError(f"HTTP 503 for {url}")

    pool2, errors2 = mod.build_corpus(target=5, fetch_fn=failing_fetch, pause=0)
    if pool2 or not errors2:
        print("FAIL: fetch failures should be declared, not swallowed", len(pool2), len(errors2))
        fails += 1
    else:
        print("PASS: fetch gaps are collected")

    payload = mod.corpus_payload(pool, errors)
    counts = payload.get("counts", {})
    if counts.get("total") != 3 or "by_domain" not in counts:
        print("FAIL: corpus_payload shape", counts)
        fails += 1
    else:
        print("PASS: corpus_payload carries tallies")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "corpus.json"
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--build", "--offline", "--out", str(out)],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            print("FAIL: offline CLI exit", r.returncode, r.stderr[:300])
            fails += 1
        elif not out.exists():
            print("FAIL: offline CLI wrote no corpus")
            fails += 1
        else:
            data = json.loads(out.read_text(encoding="utf-8"))
            if not data.get("items") or data["counts"]["total"] != len(data["items"]):
                print("FAIL: offline corpus inconsistent", data.get("counts"))
                fails += 1
            else:
                print("PASS: offline CLI writes a consistent corpus")
                stats = subprocess.run(
                    [sys.executable, str(SCRIPT), "--stats", "--out", str(out)],
                    capture_output=True,
                    text=True,
                )
                if stats.returncode != 0 or "Dashboard corpus" not in stats.stdout:
                    print("FAIL: --stats", stats.returncode, stats.stdout[:200])
                    fails += 1
                else:
                    print("PASS: --stats reads the stored corpus")

    # A stray --offline (or a low --target, or a network hiccup) must not
    # silently overwrite a corpus that cost real requests: this happened for
    # real during review — an unrelated CLI probe with no --out clobbered the
    # committed corpus. The guard: refuse below half the existing size, unless
    # --force says the shrink is intentional.
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "corpus.json"
        big = {
            "version": 1, "built_at": "x",
            "counts": {"total": 100}, "fetch_gaps": [],
            "items": [{"source": "env", "key": f"K{i}", "label": f"item {i}",
                       "url": "u", "origin": "o", "stack": [], "domain": ["generic"],
                       "style": []} for i in range(100)],
        }
        out.write_text(json.dumps(big), encoding="utf-8")

        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--build", "--offline", "--out", str(out)],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            print("FAIL: shrink from 100 to a handful accepted without --force")
            fails += 1
        elif "Rifiuto di sovrascrivere" not in (r.stdout + r.stderr):
            print("FAIL: refused without explaining why", r.stdout[-300:], r.stderr[-300:])
            fails += 1
        else:
            print("PASS: shrinking a real corpus is refused without --force")

        after = json.loads(out.read_text(encoding="utf-8"))
        if len(after.get("items", [])) != 100:
            print("FAIL: refused build still touched the file", len(after.get("items", [])))
            fails += 1
        else:
            print("PASS: the refused build left the file untouched")

        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--build", "--offline", "--out", str(out), "--force"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print("FAIL: --force did not override the guard", r.stderr[-300:])
            fails += 1
        else:
            print("PASS: --force overrides the guard on purpose")

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
