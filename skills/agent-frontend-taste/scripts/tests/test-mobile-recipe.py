# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for mobile_recipe.py + mobile_corpus.py — run:
uv run scripts/tests/test-mobile-recipe.py"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "mobile_recipe.py"
CORPUS_PY = ROOT / "mobile_corpus.py"
RULES = ROOT.parent / "references" / "mobile-rules.md"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def run(path: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(path), *args], capture_output=True, text=True)


class Args:
    """Stand-in for argparse output."""

    def __init__(self, **kw):
        self.seed = "2026072609"
        self.domain = None
        self.activity = None
        self.refs = 0
        self.last_palette: list[str] = []
        self.last_radius: list[str] = []
        self.last_type: list[str] = []
        self.last_shell: list[str] = []
        self.last_splash: list[str] = []
        self.last_background: list[str] = []
        self.__dict__.update(kw)


def main() -> int:
    fails = 0
    m = load(RECIPE, "mobile_recipe")
    c = load(CORPUS_PY, "mobile_corpus")

    def check(label: str, got, want) -> None:
        nonlocal fails
        if got == want:
            print(f"PASS: {label}")
        else:
            print(f"FAIL: {label}\n  atteso: {want}\n  ottenuto: {got}")
            fails += 1

    # --- axes ------------------------------------------------------------
    keys = [k for k, _t, _p in m.AXIS_ORDER]
    check("assi con chiavi uniche", len(set(keys)), len(keys))
    graphic = {"splash", "app_background", "brand_mark", "onboarding", "illustration", "depth"}
    check("i sei assi grafici ci sono", graphic - set(keys), set())
    # 3 is the floor: below that an axis cannot rotate. `density` legitimately
    # has exactly three (airy / balanced / dense) — that is the whole taxonomy.
    thin = [k for k, _t, pool in m.AXIS_ORDER if len(pool) < 3]
    check("nessun pool troppo piccolo per ruotare", thin, [])
    undescribed = [
        f"{k}.{v}" for k, _t, pool in m.AXIS_ORDER for v, desc in pool.items() if len(desc) < 20
    ]
    check("ogni valore dice come si fa", undescribed, [])

    # Conflicts must reference axes and values that exist, or they never fire.
    multi = {"extras": m.EXTRAS, "motion": m.MOTION_TECHNIQUES}
    bad = []
    for a_key, a_val, b_key, b_val, _why in m.CONFLICTS + m.DISSONANCES:
        pool_a = m.POOLS.get(a_key) or multi.get(a_key)
        pool_b = m.POOLS.get(b_key) or multi.get(b_key)
        if not pool_a or a_val not in pool_a:
            bad.append(f"{a_key}={a_val}")
        if not pool_b or b_val not in pool_b:
            bad.append(f"{b_key}={b_val}")
    check("i conflitti puntano ad assi e valori reali", bad, [])

    # --- determinism -----------------------------------------------------
    a = m.build(Args())
    b = m.build(Args())
    check("stesso seed → stessa ricetta", a["choice"], b["choice"])
    later = m.build(Args(seed="2026072610"))
    if a["choice"] == later["choice"]:
        print("FAIL: l'ora dopo produce la stessa ricetta")
        fails += 1
    else:
        print("PASS: l'ora dopo produce una ricetta diversa")

    # A small pool must still rotate: one stream per axis exists to avoid runs.
    seen = {k: set() for k in ("splash", "app_background", "radius_family")}
    for h in range(24):
        ch = m.build(Args(seed=f"202607{h:02d}09"))["choice"]
        for k in seen:
            seen[k].add(ch[k])
    for k, vals in seen.items():
        got = len(vals)
        want = min(4, len(m.POOLS[k]))
        if got >= want:
            print(f"PASS: `{k}` copre {got}/{len(m.POOLS[k])} valori su 24 seed")
        else:
            print(f"FAIL: `{k}` fermo su {got} valori su 24 seed (atteso ≥{want})")
            fails += 1

    # --- MEMORY exclusions ----------------------------------------------
    spent = a["choice"]["splash"]
    out = m.build(Args(last_splash=[spent]))
    check("`--last-splash` esce dal pool", out["choice"]["splash"] != spent, True)
    bg = a["choice"]["app_background"]
    out = m.build(Args(last_background=[bg]))
    check("`--last-background` esce dal pool", out["choice"]["app_background"] != bg, True)
    # Draining a pool must not deadlock: it refills instead.
    drained = m.build(Args(last_splash=list(m.SPLASH)))
    check("pool svuotato → ripiega, non si blocca", drained["choice"]["splash"] in m.SPLASH, True)

    # --- conflicts actually resolve --------------------------------------
    forced = {k: pick for k, _t, pool in m.AXIS_ORDER for pick in [next(iter(pool))]}
    forced["splash"] = "gradient-wash"
    forced["app_background"] = "solid-texture"
    forced["motion"] = []
    forced["extras"] = []
    notes = m.resolve_conflicts(forced, "2026072609")
    check("lo splash a gradiente non convive con fondo pieno",
          forced["app_background"] != "solid-texture", True)
    check("il conflitto viene dichiarato", bool(notes), True)

    # Property, not example: no recipe may ship with a conflict still standing.
    # One pass used to leave ~1 in 200 — a second swap on `motion` could hand
    # back the technique the first swap had removed.
    residual: dict[str, int] = {}
    for i in range(1500):
        ch = m.build(Args(seed=f"probe{i}"))["choice"]
        for a_key, a_val, b_key, b_val, _why in m.CONFLICTS + m.DISSONANCES:
            if ch.get(a_key) != a_val:
                continue
            got = ch.get(b_key)
            live = b_val in got if isinstance(got, list) else got == b_val
            if live:
                key = f"{a_key}={a_val} & {b_key}~{b_val}"
                residual[key] = residual.get(key, 0) + 1
    check("nessun conflitto sopravvive, su 1500 seed", residual, {})

    # The swap must not change how many techniques/extras the recipe carries.
    before = m.build(Args(seed="2026072609"))["choice"]
    check("motion resta 2–4", 2 <= len(before["motion"]) <= 4, True)
    check("extras resta 3–4", 3 <= len(before["extras"]) <= 4, True)

    # --- domain weights ---------------------------------------------------
    # Weights bias the seeded draw toward what the vertical actually needs;
    # they never remove an option and `--flat` restores the uniform draw.
    boosted = {"sharp", "soft", "mixed-signal"}
    fin = [str(m.build(Args(seed=f"dw{i}", domain="fintech"))["choice"]["radius_family"])
           for i in range(300)]
    base = [str(m.build(Args(seed=f"dw{i}"))["choice"]["radius_family"])
            for i in range(300)]
    fin_share = sum(v in boosted for v in fin) / 300
    base_share = sum(v in boosted for v in base) / 300
    check("fintech spinge sharp/soft/mixed sopra il 60%", fin_share > 0.6, True)
    check("senza dominio la quota resta vicino a 3/5", 0.45 < base_share < 0.75, True)
    check("nessun valore eliminato dai pesi", set(fin) >= set(m.RADIUS_FAMILIES) - {"pill", "rounded"}, True)
    # --flat now disables BOTH domain weights and aesthetic affinities: two flat
    # builds must coincide regardless of domain, and carry no harmony notes.
    flat_dom = m.build(Args(seed="2026072612", domain="fintech", flat=True))["choice"]
    flat_none = m.build(Args(seed="2026072612", flat=True))["choice"]
    check("--flat: identico con e senza dominio", flat_dom, flat_none)
    check("--flat non porta note di armonia", "harmony" in flat_dom, False)
    check("stesso seed+dominio → stessa ricetta",
          m.build(Args(seed="dwx", domain="food"))["choice"],
          m.build(Args(seed="dwx", domain="food"))["choice"])
    weighted = m.build(Args(seed="2026072612", domain="fintech"))["choice"]
    check("gli assi pesati sono dichiarati nella ricetta",
          weighted.get("domain_weighted_axes"),
          sorted(m.DOMAIN_WEIGHTS["fintech"]))
    for dom, table in m.DOMAIN_WEIGHTS.items():
        for axis, vals in table.items():
            if axis not in m.POOLS:
                check(f"peso su asse inesistente: {dom}.{axis}", axis, "in POOLS")
            else:
                ghost = [v for v in vals if v not in m.POOLS[axis]]
                if ghost:
                    check(f"peso su valore inesistente: {dom}.{axis}", ghost, [])

    # --- aesthetic harmony -------------------------------------------------
    # Every affinity must point at real palettes, axes and values.
    ghost_aff = [
        f"{pal}.{ax}.{v}"
        for pal, table in m.AFFINITY.items()
        for ax, vals in table.items()
        for v in vals
        if pal not in m.PALETTE_FAMILIES or ax not in m.POOLS or v not in m.POOLS[ax]
    ]
    check("le affinità puntano a palette/assi/valori reali", ghost_aff, [])
    for a_key, a_val, b_key, b_val, _w in m.DISSONANCES:
        if a_val not in m.POOLS[a_key] or b_val not in m.POOLS[b_key]:
            check(f"dissonanza su valori inesistenti: {a_val}×{b_val}", False, True)

    # Baseline before this layer: 12.2% of recipes carried a jarring pairing.
    # With affinities the disfavoured pairs must be rare and the hard ones dead.
    jarring = hard = 0
    for i in range(600):
        ch = m.build(Args(seed=f"ae{i}"))["choice"]
        if ch["palette_family"] == "obsidian-champagne" and ch["radius_family"] in ("pill", "rounded"):
            jarring += 1
        for a_key, a_val, b_key, b_val, _w in m.DISSONANCES:
            if ch.get(a_key) == a_val and ch.get(b_key) == b_val:
                hard += 1
    check("dissonanze dure: zero su 600 seed", hard, 0)
    check("coppie sfavorite rare (<5% su 600 seed)", jarring < 30, True)
    harm = m.build(Args(seed="ae1"))["choice"]
    if "harmony" in harm:
        check("l'armonia è dichiarata come lista di assi accordati",
              all("←" in h for h in harm["harmony"]), True)
    r = run(RECIPE, "--seed", "2026072614", "--refs", "0")
    check("la ricetta stampa la riga Armonia quando attiva",
          "Armonia" in r.stdout or "harmony" not in m.build(Args(seed="2026072614"))["choice"],
          True)

    # --- batch -----------------------------------------------------------
    # Property: the conflict/dissonance re-pick must respect the siblings'
    # spent values. Before the fix, 63/800 batches broke mutual distinctness
    # exactly on the conflict-rewritten axes (app_background).
    bviol = 0
    for i in range(250):
        b4 = m.build_batch(Args(seed=f"bt{i}"), ["a", "b", "c", "d"])
        for axis in m.DISTINCT_AXES:
            vals = [str(r["choice"][axis]) for r in b4]
            if len(set(vals)) != len(vals):
                bviol += 1
    check("batch: distinzione mantenuta anche dopo i ripescaggi (250×4)", bviol, 0)

    batch = m.build_batch(Args(), ["a", "b", "c"])
    check("batch: una ricetta per etichetta", len(batch), 3)
    for axis in ("app_shell", "splash", "app_background", "palette_family"):
        vals = [r["choice"][axis] for r in batch]
        check(f"batch: `{axis}` mai ripetuto", len(set(vals)), 3)

    # --- corpus ----------------------------------------------------------
    check("`car` non timbra più `card`", c._matches("car", "shopping cart app"), False)
    check("`car` resta parola intera valida", c._matches("car", "car rental app"), True)
    check("`bank` prende `banking`", c._matches("bank", "mobile banking app"), True)
    check("`splash screen` non prende «Splashes»",
          c._matches("splash screen", "splashes creative agency"), False)
    untrusted = {s for s, (_b, _v, t) in c.ENV_CATALOGS.items() if not t}
    check("i cataloghi a fedeltà nulla non timbrano tratti",
          {"gradient", "splash-screen", "onboarding", "ionic"} - untrusted, set())
    _stack, _dom, graphic_traits = c.infer_traits("generic business template")
    check("un catalogo non affidabile non inventa un tratto", graphic_traits, [])

    if m.CORPUS.exists():
        corpus = m.load_corpus()
        items = corpus.get("items", [])
        check("corpus non vuoto", len(items) > 200, True)
        liars = [i for i in items if "gradient" in (i.get("graphic") or [])
                 and "gradient" not in i["label"].lower()]
        check("nessun item marcato `gradient` senza dirlo nel nome", liars, [])
        refs, stacks = m.sample_refs(corpus, "food", 10, "2026072609")
        check("i refs sul dominio arrivano dal dominio",
              all("food" in (r.get("domain") or []) for r in refs[:5]), True)
    else:
        print("SKIP: corpus assente — esegui mobile_corpus.py --build")

    # --- the viewport-height shell is an invariant, never a sorted axis ----
    inv = " ".join(m.INVARIANTS)
    for needle in ("100svh", "grid-template-rows", "position: fixed",
                   "safe-area-inset-bottom", "interactive-widget",
                   "non scorre come una pagina desktop"):
        check(f"invariante shell: «{needle}»", needle in inv, True)
    check("la barra sempre visibile non è sorteggiabile",
          any("barra" in v.lower() for pool in m.POOLS.values() for v in pool.values()
              if "sempre visibile" in v.lower()), False)

    # --- real images instead of placeholders, when there is no backend -----
    for needle in ("segnaposti muti", "immagine reale", "avatar senza foto",
                    "skeleton di caricamento", "illustrated-empty"):
        check(f"invariante immagini: «{needle}»", needle in inv, True)
    # The rule must not be sortable away either — it is not a graphic axis value.
    check("«mai segnaposti» non è un valore di un asse sorteggiabile",
          any("segnaposti muti" in v.lower() for pool in m.POOLS.values()
              for v in pool.values()), False)

    # An unknown --domain used to pass for research: the refs went generic while
    # the header still implied they were weighted.
    r = run(RECIPE, "--domain", "inesistente-xyz", "--refs", "3")
    check("dominio inesistente → avviso esplicito", "attenzione" in r.stdout, True)
    if m.CORPUS.exists():
        r = run(RECIPE, "--domain", "food", "--refs", "3")
        check("dominio valido → nessun falso allarme", "attenzione" in r.stdout, False)
        check("known_domains elenca i domini veri",
              "food" in m.known_domains(m.load_corpus()), True)
        check("`generic` non è un dominio proponibile",
              "generic" in m.known_domains(m.load_corpus()), False)

    # --- rules doc -------------------------------------------------------
    if RULES.exists():
        text = RULES.read_text(encoding="utf-8")
        for needle in ("Figma Community", "robots.txt", "anti-banding", "due estremi",
                       "background_color", "leva morta", "terza riga della griglia",
                       "overscroll-behavior", "solo web app",
                       "Contenuto senza dati reali", "tondo a tinta piena",
                       "non deve mai comportarsi così", "illustrated-empty",
                       "davvero zero"):
            check(f"mobile-rules.md dice «{needle}»", needle in text, True)
    else:
        print("FAIL: references/mobile-rules.md manca")
        fails += 1

    # --- CLI -------------------------------------------------------------
    r = run(RECIPE, "--seed", "2026072609", "--refs", "0")
    check("CLI md esce 0", r.returncode, 0)
    check("CLI stampa gli assi grafici", "**Splash**" in r.stdout, True)
    check("CLI stampa gli invarianti", "Invarianti" in r.stdout, True)

    r = run(RECIPE, "--seed", "2026072609", "--format", "json", "--refs", "0")
    payload = json.loads(r.stdout)
    check("json ha tutti gli assi", set(keys) - set(payload["choice"]), set())
    check("json porta gli invarianti", len(payload["invariants"]) >= 10, True)

    r = run(RECIPE, "--batch", "x,y", "--format", "json", "--refs", "0")
    check("json batch è una lista", len(json.loads(r.stdout)), 2)

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "corpus.json"
        r = run(CORPUS_PY, "--build", "--offline", "--out", str(out))
        check("corpus offline funziona senza rete", r.returncode, 0)
        check("corpus offline scrive un JSON valido",
              isinstance(json.loads(out.read_text(encoding="utf-8")).get("items"), list), True)

        # A stray --offline (or a low --target) must not silently wipe out a
        # corpus that cost real requests — this happened for real during
        # review, on the committed corpus, from an unrelated CLI probe with no
        # --out. The guard: refuse a shrink below half the existing size unless
        # --force says it is intentional.
        big = Path(tmp) / "big.json"
        big.write_text(json.dumps({
            "version": 1, "surface": "mobile", "built_at": "x",
            "counts": {"total": 100}, "gaps": [],
            "items": [{"source": "env", "key": f"K{i}", "label": f"item {i}",
                       "url": "u", "origin": "o", "stack": [], "domain": ["generic"],
                       "graphic": []} for i in range(100)],
        }), encoding="utf-8")

        r = run(CORPUS_PY, "--build", "--offline", "--out", str(big))
        check("sovrascrittura da 100 a poche unità rifiutata senza --force",
              r.returncode != 0, True)
        check("il rifiuto spiega perché",
              "Rifiuto di sovrascrivere" in (r.stdout + r.stderr), True)
        after = json.loads(big.read_text(encoding="utf-8"))
        check("la build rifiutata non tocca il file", len(after.get("items", [])), 100)

        r = run(CORPUS_PY, "--build", "--offline", "--out", str(big), "--force")
        check("--force scavalca la protezione di proposito", r.returncode, 0)

        # A corrupt target (valid JSON, but a list instead of a dict) must not
        # crash the guard that protects it: treat as no corpus, overwrite.
        broken = Path(tmp) / "broken.json"
        broken.write_text("[1, 2, 3]", encoding="utf-8")
        r = run(CORPUS_PY, "--build", "--offline", "--out", str(broken))
        check("guard su JSON non-dict: nessun crash", r.returncode, 0)
        check("guard su JSON non-dict: il file corrotto viene sovrascritto",
              isinstance(json.loads(broken.read_text(encoding="utf-8")).get("items"), list),
              True)

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
