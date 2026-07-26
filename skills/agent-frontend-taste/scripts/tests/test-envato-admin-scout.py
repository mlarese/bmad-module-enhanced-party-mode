# /// script
# requires-python = ">=3.10"
# ///
"""Tests for envato_admin_scout.py"""
import importlib.util
import subprocess
import sys
from pathlib import Path

SCOUT = Path(__file__).resolve().parents[1] / "envato_admin_scout.py"

FIXTURE = """
<a href="/admina-bootstrap-admin-dashboard-html-template-UPTPH7J">x</a>
<a href="/admina-bootstrap-admin-dashboard-html-template-UPTPH7J">dup</a>
<a href="/boron-admin-dashboard-template-5UY28VR">y</a>
<a href="/web-templates/admin-templates">skip</a>
"""


def load():
    spec = importlib.util.spec_from_file_location("envato_admin_scout", SCOUT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["envato_admin_scout"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    fails = 0
    mod = load()
    cards = mod.parse_catalog(FIXTURE, mod.CATALOGS[0])
    if len(cards) != 2:
        print("FAIL unique", len(cards), cards)
        fails += 1
    else:
        print("PASS: unique envato cards")

    if cards[0].code != "UPTPH7J":
        print("FAIL code", cards[0].code)
        fails += 1
    else:
        print("PASS: item code")

    sample = mod.sample_cards(mod.dry_run_pool(), 30, "2026072515")
    if len(sample) != 30:
        print("FAIL sample len", len(sample))
        fails += 1
    else:
        print("PASS: sample 30")

    r = subprocess.run(
        [sys.executable, str(SCOUT), "--dry-run", "--sample", "30", "--seed", "2026072515"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0 or "Mix mandate" not in r.stdout:
        print("FAIL dry-run", r.returncode, r.stdout[:300], r.stderr)
        fails += 1
    else:
        print("PASS: dry-run CLI")

    # Out-of-range input must fail BEFORE the pool is built: without --dry-run
    # that step spends real network requests. No --dry-run here on purpose —
    # if validation slid back below build_pool, this would hang on the network
    # instead of returning in milliseconds.
    import time
    for argv, what in ((["--sample", "0"], "--sample 0"),
                       (["--list", "--limit", "-3"], "--limit -3")):
        t0 = time.time()
        r = subprocess.run(
            [sys.executable, str(SCOUT), *argv],
            capture_output=True, text=True, timeout=10,
        )
        took = time.time() - t0
        if r.returncode != 1 or "deve essere ≥1" not in (r.stderr + r.stdout):
            print(f"FAIL: {what} non rifiutato con spiegazione", r.returncode)
            fails += 1
        elif took > 3:
            print(f"FAIL: {what} rifiutato ma dopo {took:.1f}s — validazione dopo la rete?")
            fails += 1
        else:
            print(f"PASS: {what} rifiutato subito ({took:.2f}s), prima della rete")

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
