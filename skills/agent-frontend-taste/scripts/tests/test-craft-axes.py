# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for craft_axes.py and hero_copy.py — the two seeded pickers that
had no coverage. Run: uv run scripts/tests/test-craft-axes.py"""
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AXES = ROOT / "craft_axes.py"
COPY = ROOT / "hero_copy.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def run(path: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(path), *args], capture_output=True, text=True)


def main() -> int:
    fails = 0
    a = load(AXES, "craft_axes")
    c = load(COPY, "hero_copy")

    def check(label: str, got, want) -> None:
        nonlocal fails
        if got == want:
            print(f"PASS: {label}")
        else:
            print(f"FAIL: {label}\n  atteso: {want}\n  ottenuto: {got}")
            fails += 1

    # --- craft_axes: determinism and shape -------------------------------
    check("stesso seed → stesso alignment_map",
          a.alignment_map(2026072609, 7), a.alignment_map(2026072609, 7))
    check("alignment_map ha una voce per sezione", len(a.alignment_map(2026072609, 7)), 7)
    check("surface_rhythm ha una voce per sezione", len(a.surface_rhythm(2026072609, 7)), 7)

    # The rule the axis exists for: no more than two centred sections, or the
    # page is a stack of centred blocks again.
    for seed in range(2026072600, 2026072624):
        centred = sum(1 for v in a.alignment_map(seed, 9) if "center" in v)
        if centred > 2:
            print(f"FAIL: seed {seed} produce {centred} sezioni centrate (max 2)")
            fails += 1
            break
    else:
        print("PASS: mai più di 2 sezioni centrate, su 24 seed")

    # Adjacent sections must not share a surface key, or the rhythm is invisible.
    bad = []
    for seed in range(2026072600, 2026072624):
        r = a.surface_rhythm(seed, 8)
        if any(x == y for x, y in zip(r, r[1:])):
            bad.append(seed)
    check("nessuna coppia adiacente uguale nel ritmo, su 24 seed", bad, [])

    # Loud keys are capped: a long page must not become a fair.
    capped = []
    for seed in range(2026072600, 2026072650):
        r = a.surface_rhythm(seed, 14)
        if r.count("media-bleed") > 2 or r.count("accent-band") > 2:
            capped.append(seed)
    check("media-bleed e accent-band mai oltre il cap, su 50 seed lunghi", capped, [])

    # Center placement: never adjacent, never on the hero.
    bad_center = []
    for seed in range(2026072600, 2026072700):
        m = a.alignment_map(seed, 9)
        cpos = [i for i, v in enumerate(m) if v == "center"]
        if any(y - x == 1 for x, y in zip(cpos, cpos[1:])) or (cpos and cpos[0] == 0):
            bad_center.append(seed)
    check("center mai adiacenti né sulla hero, su 100 seed", bad_center, [])

    # The reason this engine was rewritten: the multiplicative hash collapsed a
    # year of hourly seeds onto 112 joint recipes (0.3% of the space), 5
    # alignment maps and 5 of 27 type scales. These floors lock the repair.
    seeds = range(2026010100, 2026010100 + 400)
    check("type_scale copre tutte le 27 combinazioni",
          len({a.type_scale(s) for s in range(2026010100, 2026010100 + 600)}), 27)
    n_maps = len({tuple(a.alignment_map(s, 7)) for s in seeds})
    check("alignment_map: ≥50 mappe distinte su 400 seed (prima: 5 in totale)",
          n_maps >= 50, True)
    n_rhy = len({tuple(a.surface_rhythm(s, 7)) for s in seeds})
    check("surface_rhythm: ≥30 ritmi distinti su 400 seed (prima: 4 in totale)",
          n_rhy >= 30, True)
    # No lockstep on the real usage pattern: consecutive hours of one day.
    day = [(a._pick(list(a.SURFACE_TEXTURES), 2026072600 + h, 3),
            a._pick(list(a.THIRD_VOICES), 2026072600 + h, 4)) for h in range(24)]
    check("ore consecutive: assi decorrelati (≥12 coppie distinte su 24)",
          len(set(day)) >= 12, True)

    # Same clock, different hour → different composition (that is the point).
    same = a.alignment_map(2026072609, 7) == a.alignment_map(2026072610, 7)
    rhythm_same = a.surface_rhythm(2026072609, 7) == a.surface_rhythm(2026072610, 7)
    check("l'ora dopo cambia qualcosa", same and rhythm_same, False)

    # Exclusions from MEMORY must actually remove the value.
    pool = a.grid_pool(None, "marketing")
    spent = a._pick(pool, 2026072609, 1)
    check("`exclude` toglie il valore dal pool",
          a._pick(pool, 2026072609, 1, exclude=[spent]) != spent, True)
    check("pool svuotato → ripiega invece di bloccarsi",
          a._pick(pool, 2026072609, 1, exclude=list(pool)) in pool, True)

    # Not a ladder — three independent ratios. The craft rule they must satisfy:
    # the display breathes wider than the reading text (craft-rules, Tipografia §2).
    offenders = [
        s for s in range(2026072600, 2026072624)
        if not (lambda t: t[0] > t[1])(a.type_scale(s))
    ]
    check("display ratio sempre maggiore del body, su 24 seed", offenders, [])
    check("i ratio restano nell'intervallo dichiarato",
          [s for s in range(2026072600, 2026072624)
           if not (1.4 <= a.type_scale(s)[0] <= 1.6 and 1.15 <= a.type_scale(s)[1] <= 1.3)],
          [])

    # --- craft_axes: the range guard (a silent max(3, n) used to hide this) ---
    for n in ("0", "-5", "999"):
        r = run(AXES, "--seed", "2026072609", "--sections", n)
        if r.returncode == 0:
            print(f"FAIL: --sections {n} accettato in silenzio")
            fails += 1
        elif "fuori intervallo" not in (r.stderr + r.stdout):
            print(f"FAIL: --sections {n} rifiutato senza spiegare")
            fails += 1
        else:
            print(f"PASS: --sections {n} rifiutato e spiegato")
    for n in ("1", "7", "40"):
        check(f"--sections {n} accettato", run(AXES, "--sections", n).returncode, 0)

    # The third voice tunes to the texture: P(mono | rule-lines) must beat
    # P(mono | baseline-rule) by a wide margin over fixed seeds.
    mono_rule = mono_base = n_rule = n_base = 0
    for seed in range(2026010100, 2026010100 + 800):
        tex = a._pick(list(a.SURFACE_TEXTURES), seed, 3)
        voice = a._pick(list(a.THIRD_VOICES), seed, 4,
                        weights=a.TEXTURE_VOICE_AFFINITY.get(tex))
        if tex == "rule-lines":
            n_rule += 1
            mono_rule += voice == "mono"
        elif tex == "baseline-rule":
            n_base += 1
            mono_base += voice == "mono"
    check("voce accordata alla texture: mono domina su rule-lines",
          n_rule > 0 and mono_rule / n_rule > 0.45, True)
    check("…ma non su baseline-rule", n_base > 0 and mono_base / n_base < 0.40, True)
    ghost = [f"{t}.{v}" for t, vals in a.TEXTURE_VOICE_AFFINITY.items()
             for v in vals if t not in a.SURFACE_TEXTURES or v not in a.THIRD_VOICES]
    check("l'affinità texture→voce punta a valori reali", ghost, [])

    # --- hero_copy --------------------------------------------------------
    check("stesso seed → stessa scelta", c.pick(2026072609, []), c.pick(2026072609, []))
    check("ogni label ha i suoi metadati",
          [k for k in c.META if not all(x in c.META[k] for x in ("placement", "panel", "hint"))],
          [])
    spent = c.pick(2026072609, [])
    check("`--exclude` toglie la label", c.pick(2026072609, [spent]) != spent, True)
    check("escludere tutto non blocca", c.pick(2026072609, list(c.META)) in c.META, True)

    # The whole point of the axis: not always right + solid plate.
    picks = {c.pick(s, []) for s in range(2026072600, 2026072624)}
    if len(picks) < 3:
        print(f"FAIL: hero_copy fermo su {len(picks)} scelte in 24 ore: {picks}")
        fails += 1
    else:
        print(f"PASS: hero_copy copre {len(picks)}/{len(c.META)} scelte su 24 seed")

    r = run(COPY, "--seed", "2026072609")
    check("CLI hero_copy esce 0", r.returncode, 0)
    for field in ("hero_copy:", "hero_copy_placement:", "hero_copy_panel:"):
        check(f"CLI stampa `{field}`", field in r.stdout, True)

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
