# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for dashboard_recipe.py — run: uv run scripts/tests/test-dashboard-recipe.py"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "dashboard_recipe.py"


def load():
    spec = importlib.util.spec_from_file_location("dashboard_recipe", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dashboard_recipe"] = mod
    spec.loader.exec_module(mod)
    return mod


class Args:
    """Stand-in for argparse output."""

    def __init__(self, seed, **kw):
        self.seed = seed
        self.domain = kw.get("domain")
        self.activity = kw.get("activity")
        self.refs = kw.get("refs", 0)
        self.last_shell = kw.get("last_shell", [])
        self.last_palette = kw.get("last_palette", [])
        self.last_radius = kw.get("last_radius", [])
        self.last_type = kw.get("last_type", [])
        self.last_texture = kw.get("last_texture", [])


def main() -> int:
    fails = 0
    mod = load()

    a = mod.build(Args("2026072518"))["choice"]
    b = mod.build(Args("2026072518"))["choice"]
    if a != b:
        print("FAIL: same seed must give the same recipe")
        fails += 1
    else:
        print("PASS: deterministic per seed")

    c = mod.build(Args("2026072519"))["choice"]
    if a == c:
        print("FAIL: next hour should move the recipe")
        fails += 1
    else:
        print("PASS: seed change moves the recipe")

    # Small pools must not stall on 2 of 5 values across adjacent hours.
    seeds = [f"20260726{h:02d}" for h in range(24)] + [
        f"2026080{d}{h:02d}" for d in range(1, 5) for h in range(24)
    ]
    picks = {axis: set() for axis in ("shell", "radius_family", "kpi_style", "table_pattern")}
    for s in seeds:
        ch = mod.build(Args(s))["choice"]
        for axis in picks:
            picks[axis].add(ch[axis])
    for axis, seen in picks.items():
        pool = len(mod.POOLS[axis])
        if len(seen) < pool:
            print(f"FAIL: {axis} used only {len(seen)}/{pool} values over {len(seeds)} seeds")
            fails += 1
        else:
            print(f"PASS: {axis} spans all {pool} values")

    excluded = mod.build(Args("2026072518", last_palette=[a["palette_family"]]))["choice"]
    if excluded["palette_family"] == a["palette_family"]:
        print("FAIL: MEMORY exclusion ignored", a["palette_family"])
        fails += 1
    else:
        print("PASS: MEMORY exclusions drop a value from the pool")

    # Conflicting pairs must never survive: the second axis is re-picked.
    forced = {
        "shell": "split-master-detail",
        "detail_surface": "split-detail",
        "kpi_style": "card-sparkline",
        "dataviz": ["sparkline", "donut-ring"],
        "header_bar": "search-first",
        "extras": ["command-palette", "csv-export"],
        "table_pattern": "expandable-rows",
        "density": "operational",
        "filter_pattern": "chips-row",
    }
    notes = mod.resolve_conflicts(forced, "2026072518")
    if forced["detail_surface"] == "split-detail":
        print("FAIL: split shell kept a split detail surface")
        fails += 1
    elif "sparkline" in forced["dataviz"]:
        print("FAIL: sparkline KPI kept a sparkline chart", forced["dataviz"])
        fails += 1
    elif "command-palette" in forced["extras"]:
        print("FAIL: search-first header kept the command palette", forced["extras"])
        fails += 1
    elif forced["table_pattern"] == "expandable-rows":
        print("FAIL: split shell kept expandable rows")
        fails += 1
    elif len(notes) < 4:
        print("FAIL: conflicts resolved silently", notes)
        fails += 1
    elif len(forced["dataviz"]) != 2 or len(forced["extras"]) != 2:
        print("FAIL: swap changed the count", forced["dataviz"], forced["extras"])
        fails += 1
    else:
        print("PASS: conflicts are resolved and declared")

    # Property, not example: no recipe may ship with a conflict still standing.
    # A single resolution pass used to leave ~1 in 110 (three pairs write to
    # `filter_pattern`; the last one handed back what the first had banned).
    residual: dict[str, int] = {}
    for i in range(1500):
        ch = mod.build(Args(f"probe{i}"))["choice"]
        for a_key, a_val, b_key, b_val, _why in mod.CONFLICTS + mod.DISSONANCES:
            if ch.get(a_key) != a_val:
                continue
            got = ch.get(b_key)
            live = b_val in got if isinstance(got, list) else got == b_val
            if live:
                key = f"{a_key}={a_val} & {b_key}~{b_val}"
                residual[key] = residual.get(key, 0) + 1
    if residual:
        print(f"FAIL: conflitti residui su 1500 seed: {residual}")
        fails += 1
    else:
        print("PASS: nessun conflitto sopravvive, su 1500 seed")

    # Domain weights: bias declared, nothing removed, --flat restores uniform.
    pos = [mod.build(Args(f"dw{i}", domain="pos"))["choice"]["density"] for i in range(300)]
    base = [mod.build(Args(f"dw{i}"))["choice"]["density"] for i in range(300)]
    if pos.count("dense-pro") <= base.count("dense-pro"):
        print("FAIL: domain=pos non spinge dense-pro", pos.count("dense-pro"), base.count("dense-pro"))
        fails += 1
    elif "comfortable" not in pos:
        print("FAIL: i pesi hanno eliminato un valore invece di sfavorirlo")
        fails += 1
    else:
        print("PASS: domain=pos spinge la densità senza eliminare opzioni")
    # --flat disables domain weights AND aesthetic affinities: two flat builds
    # coincide regardless of domain, and carry no harmony notes.
    fa = Args("2026072612", domain="pos"); fa.flat = True
    fb = Args("2026072612"); fb.flat = True
    ca, cb = mod.build(fa)["choice"], mod.build(fb)["choice"]
    if ca != cb or "harmony" in ca:
        print("FAIL: --flat non uniforme", ca.get("harmony"))
        fails += 1
    else:
        print("PASS: --flat: identico con/senza dominio, senza armonia")
    ghost_aff = [
        f"{pal}.{ax}.{v}"
        for pal, table in mod.AFFINITY.items()
        for ax, vals in table.items()
        for v in vals
        if pal not in mod.PALETTE_FAMILIES or ax not in mod.POOLS or v not in mod.POOLS[ax]
    ]
    if ghost_aff:
        print("FAIL: affinità su palette/assi/valori inesistenti:", ghost_aff)
        fails += 1
    else:
        print("PASS: le affinità puntano a palette/assi/valori reali")
    hard = sum(
        1 for i in range(600)
        for a_key, a_val, b_key, b_val, _w in mod.DISSONANCES
        if (ch := mod.build(Args(f"ae{i}"))["choice"]).get(a_key) == a_val
        and ch.get(b_key) == b_val
    )
    if hard:
        print(f"FAIL: {hard} dissonanze dure su 600 seed")
        fails += 1
    else:
        print("PASS: dissonanze dure: zero su 600 seed")
    ghost = [
        f"{d}.{ax}.{v}"
        for d, table in mod.DOMAIN_WEIGHTS.items()
        for ax, vals in table.items()
        for v in vals
        if ax not in mod.POOLS or v not in mod.POOLS[ax]
    ]
    if ghost:
        print("FAIL: pesi su assi/valori inesistenti:", ghost)
        fails += 1
    else:
        print("PASS: ogni peso punta a un asse e un valore reali")

    # An unknown --domain used to pass for research.
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--domain", "inesistente-xyz", "--refs", "3"],
        capture_output=True, text=True)
    if "attenzione" not in r.stdout:
        print("FAIL: dominio inesistente non dichiarato")
        fails += 1
    else:
        print("PASS: dominio inesistente → avviso esplicito")

    # Property: conflict re-picks must respect sibling exclusions. Before the
    # fix, 100/800 batches broke distinctness on table_pattern.
    bviol = 0
    for i in range(250):
        b4 = mod.build_batch(Args(f"bt{i}"), ["a", "b", "c", "d"])
        for axis in mod.DISTINCT_AXES:
            vals = [str(r["choice"][axis]) for r in b4]
            if len(set(vals)) != len(vals):
                bviol += 1
    if bviol:
        print(f"FAIL: {bviol} batch con assi duplicati dopo i ripescaggi")
        fails += 1
    else:
        print("PASS: batch distinti anche dopo i ripescaggi (250×4)")

    labels = ["a", "b", "c", "d"]
    batch = mod.build_batch(Args("2026072518"), labels)
    if [r["label"] for r in batch] != labels:
        print("FAIL: batch labels", [r.get("label") for r in batch])
        fails += 1
    else:
        collisions = []
        for axis in mod.DISTINCT_AXES:
            values = [r["choice"][axis] for r in batch]
            if len(set(values)) != len(values):
                collisions.append((axis, values))
        if collisions:
            print("FAIL: sibling dashboards share a silhouette axis", collisions)
            fails += 1
        else:
            print("PASS: batch recipes are mutually distinct on every silhouette axis")

    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--seed", "2026072518", "--refs", "0"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print("FAIL: md CLI exit", r.returncode, r.stderr[:300])
        fails += 1
    elif "seed: `2026072518`" not in r.stdout or "Invarianti" not in r.stdout:
        print("FAIL: md CLI output missing seed or invariants", r.stdout[:300])
        fails += 1
    elif "Assi dichiarati" not in r.stdout or "Done quando" not in r.stdout:
        print("FAIL: md CLI missing sections")
        fails += 1
    else:
        print("PASS: md CLI renders seed, axes, invariants, done criteria")

    rj = subprocess.run(
        [sys.executable, str(SCRIPT), "--seed", "2026072518", "--refs", "0", "--format", "json"],
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(rj.stdout)
    except json.JSONDecodeError as e:
        print("FAIL: json CLI not parseable", e)
        fails += 1
    else:
        if payload.get("choice", {}).get("shell") != a["shell"]:
            print("FAIL: json CLI disagrees with build()", payload.get("choice", {}).get("shell"))
            fails += 1
        elif not payload.get("invariants"):
            print("FAIL: json CLI dropped invariants")
            fails += 1
        else:
            print("PASS: json CLI matches build() and carries invariants")

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
