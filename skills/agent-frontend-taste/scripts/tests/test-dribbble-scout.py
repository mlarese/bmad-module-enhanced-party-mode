# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for dribbble-scout.py — run: uv run scripts/tests/test-dribbble-scout.py"""
import importlib.util
import subprocess
import sys
from pathlib import Path

SCOUT = Path(__file__).resolve().parents[1] / "dribbble-scout.py"

FIXTURE = """
<html><body>
<a href="/shots/27589145-Agio-Multi-Currency-Banking-Landing-Page">x</a>
<a href="/shots/27589145-Agio-Multi-Currency-Banking-Landing-Page">dup</a>
<a href="/shots/27589573-Akademi-eLearning-Landing-Page">y</a>
<a href="/shots/27589276-G-logo-mark">z</a>
</body></html>
"""


def load_scout():
    spec = importlib.util.spec_from_file_location("dribbble_scout", SCOUT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dribbble_scout"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    fails = 0
    mod = load_scout()
    cards = mod.parse_list(FIXTURE)
    if len(cards) != 3:
        print("FAIL: expected 3 unique shots, got", len(cards))
        fails += 1
    else:
        print("PASS: unique shots")

    if cards[0].label != "Agio Multi Currency Banking Landing Page":
        print("FAIL: label", cards[0].label)
        fails += 1
    else:
        print("PASS: slug-derived label")

    filtered = mod.prefer_web_ui(cards)
    labels = [c.label for c in filtered]
    if any("logo mark" in L.lower() for L in labels):
        print("FAIL: logo should be filtered out", labels)
        fails += 1
    elif len(filtered) != 2:
        print("FAIL: prefer_web_ui expected 2 UI shots", labels)
        fails += 1
    else:
        print("PASS: prefer_web_ui drops logo-only")

    if "website-template" not in mod.LISTS:
        print("FAIL: missing website-template list")
        fails += 1
    elif "q=website" not in mod.LISTS["website-template"]:
        print("FAIL: website-template URL not q= based", mod.LISTS["website-template"])
        fails += 1
    else:
        print("PASS: website-template maps to shots?q=")

    r = subprocess.run([sys.executable, str(SCOUT)], capture_output=True, text=True)
    if r.returncode == 0:
        print("FAIL: expected non-zero without args")
        fails += 1
    else:
        print("PASS: CLI requires --list or --shot")

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
