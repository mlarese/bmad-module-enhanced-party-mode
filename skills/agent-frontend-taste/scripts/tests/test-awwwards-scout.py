# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for awwwards-scout.py — run: uv run scripts/tests/test-awwwards-scout.py"""
import importlib.util
import sys
from pathlib import Path

SCOUT = Path(__file__).resolve().parents[1] / "awwwards-scout.py"

FIXTURE = """
<html><body>
<a href="/sites/artem-shcherbakov/">x</a>
<h3 class="avatar-name__title">SALT AND PEPPER</h3>
<a href="/sites/spotify-wrapped-party">y</a>
<span class="avatar-name__title">Active Theory</span>
<a href="/sites/artem-shcherbakov/">dup</a>
</body></html>
"""


def load_scout():
    spec = importlib.util.spec_from_file_location("awwwards_scout", SCOUT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["awwwards_scout"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    fails = 0
    mod = load_scout()
    cards = mod.parse_list(FIXTURE)
    if len(cards) != 2:
        print("FAIL: expected 2 unique cards, got", len(cards), cards)
        fails += 1
    else:
        print("PASS: unique site cards")

    by_slug = {c.slug: c for c in cards}
    if by_slug["artem-shcherbakov"].label != "SALT AND PEPPER":
        print("FAIL: label near first slug", by_slug["artem-shcherbakov"].label)
        fails += 1
    else:
        print("PASS: labeled card")

    title, desc, live = mod.parse_site(
        '<title>Foo - Awwwards</title><meta property="og:description" content="Bar &amp; Baz">'
        '<a rel="nofollow" href="https://studio-foo.com/">site of the day</a>',
        "foo",
    )
    if title != "Foo - Awwwards" or desc != "Bar & Baz":
        print("FAIL: parse_site", title, desc)
        fails += 1
    elif live != "https://studio-foo.com/":
        print("FAIL: parse_site live url", live)
        fails += 1
    else:
        print("PASS: parse_site title/desc/live url")

    # CLI usage
    import subprocess

    r = subprocess.run([sys.executable, str(SCOUT)], capture_output=True, text=True)
    if r.returncode == 0:
        print("FAIL: expected non-zero without args")
        fails += 1
    else:
        print("PASS: CLI requires --list or --site")

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
