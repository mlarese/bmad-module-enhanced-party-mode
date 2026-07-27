# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for effects_gallery.py — run: uv run scripts/tests/test-effects-gallery.py"""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "effects_gallery.py"
CATALOG_MD = Path(__file__).resolve().parents[2] / "references" / "catalog.md"


def load():
    spec = importlib.util.spec_from_file_location("effects_gallery", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["effects_gallery"] = mod
    spec.loader.exec_module(mod)
    return mod


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def main() -> int:
    fails = 0
    mod = load()
    catalog = mod.load()
    effects = catalog["effects"]
    axes = catalog["axes"]

    def check(label: str, got, want) -> None:
        nonlocal fails
        if got == want:
            print(f"PASS: {label}")
        else:
            print(f"FAIL: {label}\n  atteso: {want}\n  ottenuto: {got}")
            fails += 1

    ids = [e["id"] for e in effects]
    check("id unici", len(set(ids)), len(ids))

    numbers = [e["n"] for e in effects]
    check("numerazione senza buchi", numbers, list(range(1, len(catalog["effects"]) + 1)))

    # The numbering is a promise: catalog.md is what people already cite.
    if CATALOG_MD.exists():
        rows = re.findall(r"^\|\s*(\d+)\s*\|", CATALOG_MD.read_text(encoding="utf-8"), re.M)
        check("stessa numerazione di references/catalog.md", sorted(int(r) for r in rows), numbers)

    # An axis value nobody uses is a filter chip that filters to nothing.
    for axis in ("cat", "cost"):
        used = {e[axis] for e in effects}
        unused = set(axes[axis]) - used
        check(f"ogni valore di '{axis}' è usato", unused, set())
    used_tech = {t for e in effects for t in e["tech"]}
    check("ogni tecnica dichiarata è usata", set(axes["tech"]) - used_tech, set())

    check("ogni effetto ha una fx propria", len({e["fx"] for e in effects}), len(effects))
    check("ogni stage è noto", {e["stage"] for e in effects} - mod.STAGES, set())

    missing_text = [e["id"] for e in effects if not (e["desc"] and e["use"] and e["watch"])]
    check("ogni effetto dice cos'è, quando e cosa guardare", missing_text, [])

    # Every effect must actually carry a rule, or the tile sits still and lies.
    css = mod._css()
    silent = [e["id"] for e in effects if f".fx--{e['fx']}" not in css]
    check("ogni effetto ha una regola CSS che lo anima", silent, [])

    animated = [e["id"] for e in effects
                if re.search(rf"\.fx--{re.escape(e['fx'])}\b[^{{]*{{[^}}]*animation", css)
                or re.search(rf"\.fx--{re.escape(e['fx'])}\b[^{{]*{{[^}}]*background", css)]
    check("nessuna regola vuota", len(animated), len(effects))

    heavy = {e["cost"] for e in effects if e["approx"]}
    check("gli effetti approssimati sono quelli che costano", heavy - {"heavy", "light"}, set())


    # A typo must not read like an honest empty result.
    for bad, why in ((["ct=scroll"], "chiave"), (["cost=nonesiste"], "valore")):
        try:
            mod.parse_filters(bad, catalog)
            print(f"FAIL: filtro con {why} sconosciuto accettato: {bad}")
            fails += 1
        except SystemExit as e:
            if "sconosciut" in str(e) or "non ha il valore" in str(e):
                print(f"PASS: filtro con {why} sconosciuto rifiutato e spiegato")
            else:
                print(f"FAIL: rifiutato senza spiegare: {e}")
                fails += 1
    check("il filtro valido continua a passare",
          mod.parse_filters(["cat=scroll"], catalog), [("cat", "scroll")])

    page = mod.render_html(catalog)
    check("una card per effetto", page.count('class="card"'), len(effects))
    check("nessuna risorsa remota", re.findall(r'(?:src|href)="(?:https?:)?//', page), [])
    check("viewport meta presente", 'name="viewport"' in page, True)
    check("reduced-motion rispettato", "prefers-reduced-motion" in page, True)
    check("si può mettere in pausa", 'id="motion"' in page and "is-paused" in page, True)

    # 117 stages share one markup: colliding SVG ids would break every textPath but one.
    svg_ids = re.findall(r'<path id="([^"]+)"', page)
    check("id SVG unici in pagina", len(set(svg_ids)), len(svg_ids))
    refs = set(re.findall(r'href="#([^"]+)"', page))
    check("nessun riferimento SVG rotto", refs - set(svg_ids), set())

    for kit in catalog["kits"]:
        unknown = [n for n in kit["effects"] if n not in set(numbers)]
        check(f"kit '{kit['id']}' coerente", unknown, [])

    # Determinism: same seed, same shortlist — and the hour after must differ.
    a = [e["id"] for e in mod.suggest(effects, 4, "2026072522", [])]
    b = [e["id"] for e in mod.suggest(effects, 4, "2026072522", [])]
    c = [e["id"] for e in mod.suggest(effects, 4, "2026072523", [])]
    check("shortlist deterministica per seed", a, b)
    if a == c:
        print("FAIL: shortlist identica a un'ora diversa")
        fails += 1
    else:
        print("PASS: shortlist diversa l'ora dopo")
    check("shortlist senza effetti pesanti", [x for x in a if x in {
        e["id"] for e in effects if e["cost"] == "heavy"}], [])
    dropped = a[0]
    check("le esclusioni escono dal pool", dropped in [
        e["id"] for e in mod.suggest(effects, 4, "2026072522", [dropped])], False)

    bad = dict(catalog)
    bad["effects"] = [dict(effects[0], stage="non-esiste")]
    try:
        mod.validate(bad)
        print("FAIL: validate accetta uno stage sconosciuto")
        fails += 1
    except SystemExit:
        print("PASS: validate rifiuta uno stage sconosciuto")

    r = run("--filter", "cat=scroll")
    want = sum(1 for e in effects if e["cat"] == "scroll")
    check("filtro CLI", r.stdout.count("| `"), want)

    r = run("--show", "27")
    check("--show accetta il numero", "Scrub timeline" in r.stdout, True)
    r = run("--show", "scrub")
    check("--show accetta l'id", "Scrub timeline" in r.stdout, True)
    r = run("--show", "non-esiste")
    check("--show su id inesistente fallisce", r.returncode, 1)

    r = run("--kit", "dashboard")
    check("--kit stampa il kit", "Dashboard o app" in r.stdout, True)
    r = run("--kit", "inventato")
    check("--kit inesistente fallisce", r.returncode, 1)

    r = run("--format", "json", "--filter", "cost=heavy")
    check("--format json è JSON valido", len(json.loads(r.stdout)),
          sum(1 for e in effects if e["cost"] == "heavy"))

    if mod.PAGE.exists():
        check("la pagina committata è in sync col catalogo",
              mod.PAGE.read_text(encoding="utf-8"), page)
    else:
        print("FAIL: assets/effects-gallery.html manca — esegui --build")
        fails += 1

    # --- i preferiti dell'owner: peso, non filtro -------------------------
    # Nato misurato: la prima versione leggeva `--prefer` e non lo passava a
    # `suggest()`, quindi la preferenza era attiva sempre e l'opzione era morta
    # — con e senza uscivano shortlist identiche, e sembrava tutto a posto.
    P = set(mod.PREFERRED)
    check("ogni preferito esiste nel catalogo", P <= {e["id"] for e in effects}, True)

    con = sen = 0
    for i in range(12):
        seed = f"20260726{i:02d}"
        con += sum(1 for e in mod.suggest(effects, 4, seed, [], P) if e["id"] in P)
        sen += sum(1 for e in mod.suggest(effects, 4, seed, [], set()) if e["id"] in P)
    check("il peso morde: la shortlist esce tutta dai preferiti", con, 48)
    check("senza peso si torna al tasso di base", sen < 24, True)

    resto = mod.suggest(effects, 3, "2026072623", sorted(P), P)
    check("esclusi tutti i preferiti, il catalogo resta raggiungibile", len(resto), 3)
    check("e quella shortlist non ne contiene", all(e["id"] not in P for e in resto), True)
    check("stesso seed → stessa shortlist",
          [e["id"] for e in mod.suggest(effects, 4, "2026072623", [], P)],
          [e["id"] for e in mod.suggest(effects, 4, "2026072623", [], P)])

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
