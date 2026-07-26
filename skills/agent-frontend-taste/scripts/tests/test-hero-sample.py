# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for hero_sample.py — run: uv run scripts/tests/test-hero-sample.py"""
import importlib.util
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCOUT = Path(__file__).resolve().parents[1] / "hero_sample.py"


def load():
    spec = importlib.util.spec_from_file_location("hero_sample", SCOUT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["hero_sample"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    fails = 0
    mod = load()

    seed = mod.hour_seed(datetime(2026, 7, 25, 13, 42))
    if seed != "2026072513":
        print("FAIL: hour_seed", seed)
        fails += 1
    else:
        print("PASS: hour_seed buckets to hour")

    # Same seed → same sample; different hour → different order/group
    pool = mod.dry_run_pool()
    a = [c.key for c in mod.sample_group(pool, 30, "2026072513")]
    b = [c.key for c in mod.sample_group(pool, 30, "2026072513")]
    c = [c.key for c in mod.sample_group(pool, 30, "2026072514")]
    if a != b:
        print("FAIL: sample not deterministic for same seed")
        fails += 1
    else:
        print("PASS: deterministic sample")
    if a == c:
        print("FAIL: different hour should reshuffle", a[:5], c[:5])
        fails += 1
    else:
        print("PASS: hour change reshuffles group")

    if len(a) != 30:
        print("FAIL: expected 30", len(a))
        fails += 1
    else:
        print("PASS: count 30")

    mixed = mod.sample_group(pool, 30, "2026072513")
    sources = {c.source for c in mixed}
    if sources != {"aww", "drb"}:
        print("FAIL: expected mixed sources", sources)
        fails += 1
    else:
        print("PASS: stratified aww+drb mix")

    g0 = mod.group_index("2026072512", 4)
    g1 = mod.group_index("2026072513", 4)
    if g0 == g1:
        # consecutive hours can collide on % 4 — that's ok; check wider span
        g2 = mod.group_index("2026072516", 4)
        if g0 == g2:
            print("FAIL: group_index stuck", g0)
            fails += 1
        else:
            print("PASS: group_index rotates across hours")
    else:
        print("PASS: group_index differs for adjacent hours")

    # dry-run CLI
    r = subprocess.run(
        [sys.executable, str(SCOUT), "--dry-run", "--seed", "2026072513", "--count", "30"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print("FAIL: dry-run exit", r.returncode, r.stderr)
        fails += 1
    elif "Seed (YYYYMMDDHH): `2026072513`" not in r.stdout:
        print("FAIL: dry-run missing seed line")
        fails += 1
    elif "evaluating: 30" not in r.stdout:
        print("FAIL: dry-run missing count", r.stdout[:400])
        fails += 1
    else:
        print("PASS: dry-run CLI")

    rd = subprocess.run(
        [
            sys.executable,
            str(SCOUT),
            "--dry-run",
            "--surface",
            "dashboard",
            "--seed",
            "2026072514",
            "--count",
            "30",
        ],
        capture_output=True,
        text=True,
    )
    if rd.returncode != 0:
        print("FAIL: dashboard dry-run", rd.returncode, rd.stderr)
        fails += 1
    elif "Surface: `dashboard`" not in rd.stdout:
        print("FAIL: missing dashboard surface", rd.stdout[:300])
        fails += 1
    elif "Envato admin" not in rd.stdout and "[Envato]" not in rd.stdout:
        print("FAIL: missing Envato in dashboard batch", rd.stdout[:500])
        fails += 1
    elif "mix the best concepts" not in rd.stdout.lower() and "Mix" not in rd.stdout:
        print("FAIL: missing mix mandate", rd.stdout[-400:])
        fails += 1
    else:
        print("PASS: dashboard surface dry-run")

    dpool = mod.dry_run_pool("dashboard")
    ds = mod.sample_group(dpool, 30, "2026072515", surface="dashboard")
    env_n = sum(1 for x in ds if x.source == "env")
    if env_n < 15:
        print("FAIL: expected Envato majority", env_n)
        fails += 1
    else:
        print("PASS: dashboard Envato majority", env_n)

    if not hasattr(mod, "SOURCE_GROUPS_DASHBOARD"):
        print("FAIL: missing SOURCE_GROUPS_DASHBOARD")
        fails += 1
    elif not any(k == "env" for g in mod.SOURCE_GROUPS_DASHBOARD for k, _ in g):
        print("FAIL: dashboard groups missing env")
        fails += 1
    else:
        print("PASS: dashboard source groups include Envato")

    # activity normalization + Envato category map
    if mod.normalize_activity("restaurant") != "ristorante":
        print("FAIL: alias restaurant→ristorante", mod.normalize_activity("restaurant"))
        fails += 1
    else:
        print("PASS: activity alias")

    groups_act, _fillers_act = mod.surface_groups("marketing", "ristorante")
    env_urls = [u for g in groups_act for k, u in g if k == "env"]
    if not any("restaurant" in u for u in env_urls):
        print("FAIL: activity groups missing restaurant catalog", env_urls[:4])
        fails += 1
    else:
        print("PASS: activity marketing uses Envato restaurant")

    apool = mod.dry_run_pool("marketing", "ristorante")
    asample = mod.sample_group(
        apool, 30, "2026072516", surface="marketing", activity="ristorante"
    )
    env_a = sum(1 for x in asample if x.source == "env")
    if env_a < 15:
        print("FAIL: activity sample should prefer Envato", env_a)
        fails += 1
    else:
        print("PASS: activity Envato majority", env_a)

    if not hasattr(mod, "SOURCE_GROUPS_MOBILE"):
        print("FAIL: missing SOURCE_GROUPS_MOBILE")
        fails += 1
    else:
        print("PASS: mobile source groups exist")

    mpool = mod.dry_run_pool("mobile")
    msample = mod.sample_group(mpool, 30, "2026072517", surface="mobile")
    env_m = sum(1 for x in msample if x.source == "env")
    if env_m < 15:
        print("FAIL: mobile Envato majority", env_m)
        fails += 1
    else:
        print("PASS: mobile Envato majority", env_m)

    rm = subprocess.run(
        [
            sys.executable,
            str(SCOUT),
            "--dry-run",
            "--surface",
            "mobile",
            "--activity",
            "hotel",
            "--seed",
            "2026072518",
            "--count",
            "30",
        ],
        capture_output=True,
        text=True,
    )
    if rm.returncode != 0:
        print("FAIL: mobile+activity dry-run", rm.returncode, rm.stderr)
        fails += 1
    elif "Surface: `mobile`" not in rm.stdout:
        print("FAIL: missing mobile surface", rm.stdout[:300])
        fails += 1
    elif "Activity: `hotel`" not in rm.stdout:
        print("FAIL: missing activity hotel", rm.stdout[:400])
        fails += 1
    elif "Mobile web-app" not in rm.stdout:
        print("FAIL: missing mobile title", rm.stdout[:400])
        fails += 1
    else:
        print("PASS: mobile+activity dry-run CLI")

    ra = subprocess.run(
        [
            sys.executable,
            str(SCOUT),
            "--dry-run",
            "--activity",
            "ristorante",
            "--seed",
            "2026072519",
            "--count",
            "40",
        ],
        capture_output=True,
        text=True,
    )
    if ra.returncode != 0:
        print("FAIL: activity dry-run", ra.returncode, ra.stderr)
        fails += 1
    elif "Activity: `ristorante`" not in ra.stdout:
        print("FAIL: missing activity in marketing dry-run", ra.stdout[:400])
        fails += 1
    elif "evaluating: 40" not in ra.stdout:
        print("FAIL: count 40", ra.stdout[:300])
        fails += 1
    else:
        print("PASS: marketing+activity dry-run")

    fails += test_unknown_activity(mod)

    return 1 if fails else 0


def test_unknown_activity(mod) -> int:
    """A typo'd vertical falls back to the generic landing catalogs — say so.

    Silently it looked like a typed batch: the header listed `landing-page,
    responsive` and nothing told you the vertical had not been recognised.
    """
    bad = 0
    if mod.is_known_activity("ristorante") is not True:
        print("FAIL: 'ristorante' dovrebbe essere una vertical nota")
        bad += 1
    if mod.is_known_activity("inesistente-xyz") is not False:
        print("FAIL: una vertical inventata risulta nota")
        bad += 1
    if mod.is_known_activity(None) is not False:
        print("FAIL: activity assente trattata come nota")
        bad += 1

    out = subprocess.run(
        [sys.executable, str(SCOUT), "--dry-run", "--activity", "inesistente-xyz"],
        capture_output=True, text=True).stdout
    if "attenzione" not in out:
        print("FAIL: il batch non dichiara la vertical sconosciuta")
        bad += 1
    good = subprocess.run(
        [sys.executable, str(SCOUT), "--dry-run", "--activity", "ristorante"],
        capture_output=True, text=True).stdout
    if "attenzione" in good:
        print("FAIL: falso allarme su una vertical valida")
        bad += 1

    if not bad:
        print("PASS: vertical sconosciuta dichiarata, valida senza falsi allarmi")
    return bad


if __name__ == "__main__":
    raise SystemExit(main())
