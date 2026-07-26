# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for hero_gallery.py — run: uv run scripts/tests/test-hero-gallery.py"""
import html
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "hero_gallery.py"


def load():
    spec = importlib.util.spec_from_file_location("hero_gallery", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["hero_gallery"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    fails = 0
    mod = load()
    catalog = mod.load()
    archetypes = catalog["archetypes"]
    axes = catalog["axes"]

    ids = [a["id"] for a in archetypes]
    if len(set(ids)) != len(ids):
        print("FAIL: id duplicati")
        fails += 1
    else:
        print(f"PASS: {len(ids)} archetipi con id unici")

    # Every axis value must be reachable: an unused value is a case nobody can pick.
    for axis in ("media", "placement", "panel"):
        unused = set(axes[axis]) - {a[axis] for a in archetypes}
        if unused:
            print(f"FAIL: {axis} senza archetipi: {sorted(unused)}")
            fails += 1
        else:
            print(f"PASS: ogni valore di {axis} ha almeno un archetipo")

    # The cases the owner asked for by name.
    required_media = {"still", "carousel", "video", "none"}
    missing = required_media - {a["media"] for a in archetypes}
    if missing:
        print(f"FAIL: media obbligatori mancanti: {sorted(missing)}")
        fails += 1
    else:
        print("PASS: foto singola, carosello, video e nessun media sono coperti")

    # placement × panel: opaque and transparent, left / right / center — the 6 hero_copy labels.
    labels = {a["hero_copy"] for a in archetypes if a.get("hero_copy")}
    expected = {
        "left-solid",
        "left-transparent",
        "right-solid",
        "right-transparent",
        "center-solid",
        "center-transparent",
    }
    if expected - labels:
        print(f"FAIL: hero_copy senza archetipo: {sorted(expected - labels)}")
        fails += 1
    else:
        print("PASS: tutte le 6 etichette hero_copy hanno un archetipo")

    if labels - expected:
        print(f"FAIL: hero_copy fuori dal pool di hero_copy.py: {sorted(labels - expected)}")
        fails += 1
    else:
        print("PASS: nessuna etichetta hero_copy inventata")

    # Placements beyond the six labels must declare hero_copy: null, not a guessed label.
    extra = [a["id"] for a in archetypes if a["placement"] not in ("left", "right", "center") and a["hero_copy"]]
    if extra:
        print(f"FAIL: placement extra con hero_copy forzato: {extra}")
        fails += 1
    else:
        print("PASS: i placement extra dichiarano hero_copy null")

    treatments = {a["treatment"] for a in archetypes}
    if len(treatments) < 8:
        print(f"FAIL: solo {len(treatments)} famiglie di hero_treatment: {sorted(treatments)}")
        fails += 1
    else:
        print(f"PASS: {len(treatments)} famiglie di hero_treatment nel catalogo")

    # Le schede del catalogo restano complete — `--show <id>` le stampa in chat —
    # ma la PAGINA non le riversa più sotto ogni miniatura: lì si guarda.
    thin = [a["id"] for a in archetypes if len(a["desc"]) < 60 or len(a["use"]) < 25 or len(a["watch"]) < 25]
    if thin:
        print(f"FAIL: descrizioni troppo magre: {thin}")
        fails += 1
    else:
        print("PASS: ogni archetipo ha descrizione, quando e attenzione")


    # A typo must not read like an honest empty result: both used to print zero
    # rows in silence, so you concluded "nothing matches" instead of "you typed
    # it wrong".
    for bad, why in ((["mdia=still"], "chiave"), (["media=nonesiste"], "valore")):
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
    if mod.parse_filters(["media=still"], catalog) != [("media", "still")]:
        print("FAIL: un filtro valido non passa più")
        fails += 1
    else:
        print("PASS: il filtro valido continua a passare")

    page = mod.render_html(catalog)
    missing_cards = [a["id"] for a in archetypes if f'data-id="{a["id"]}"' not in page]
    if missing_cards:
        print(f"FAIL: archetipi senza card in pagina: {missing_cards}")
        fails += 1
    else:
        print("PASS: la pagina rende una card per ogni archetipo")

    if 'name="viewport"' not in page:
        print("FAIL: viewport meta assente")
        fails += 1
    elif "http://" in page or "https://" in page:
        print("FAIL: la pagina chiama la rete")
        fails += 1
    else:
        print("PASS: nessuna risorsa remota, viewport meta presente")

    # Le miniature mostrano foto vere: ogni src sta in hero-media/ e il file esiste.
    srcs = set(re.findall(r'src="([^"]+)"', page)) | set(re.findall(r"url\('([^']+)'\)", page))
    media_dir = catalog["media_dir"]
    outside = sorted(s for s in srcs if not s.startswith(f"{media_dir}/"))
    absent = sorted(s for s in srcs if not (mod.ASSETS / s).exists())
    if outside:
        print(f"FAIL: riferimenti fuori da {media_dir}/: {outside}")
        fails += 1
    elif absent:
        print(f"FAIL: file mancanti: {absent}")
        fails += 1
    else:
        print(f"PASS: {len(srcs)} file di media, tutti locali e presenti")

    unused_media = {f"{media_dir}/{m['file']}" for m in catalog["media_pool"].values()} - srcs
    if unused_media:
        print(f"FAIL: media nel pool ma mai in pagina: {sorted(unused_media)}")
        fails += 1
    else:
        print(f"PASS: tutte le {len(catalog['media_pool'])} immagini del pool sono in pagina")

    # E testo vero: titolo, occhiello e CTA di ogni card compaiono in pagina.
    muti = []
    for a in archetypes:
        c = mod.copy_of(catalog, a)
        hidden = set(a["sketch"].get("copy_hide") or [])
        if any(html.escape(c[f]) not in page for f in ("eyebrow", "title", "sub", "cta") if f not in hidden):
            muti.append(a["id"])
    if muti:
        print(f"FAIL: card senza testo reale: {muti}")
        fails += 1
    else:
        print("PASS: ogni miniatura porta occhiello, titolo, sottotitolo e CTA veri")

    lorem = [k for k, m in catalog["media_pool"].items()
             if "lorem" in m["title"].lower() or "ipsum" in m["sub"].lower()]
    if lorem:
        print(f"FAIL: testo segnaposto nel pool: {lorem}")
        fails += 1
    else:
        print("PASS: nessun lorem ipsum — i campioni sono copy italiano vero")

    # Vocabolario del disegno: un chrome o un'area sconosciuti falliscono in build, non a schermo.
    broken = dict(catalog)
    broken["archetypes"] = [dict(archetypes[0], id="broken", sketch={"media_area": "nope", "chrome": []})]
    try:
        mod.validate(broken)
    except SystemExit:
        print("PASS: validate rifiuta una media_area sconosciuta")
    else:
        print("FAIL: validate ha accettato una media_area sconosciuta")
        fails += 1

    seed = "2026072520"
    a = [x["id"] for x in mod.suggest(archetypes, 6, seed, [])]
    b = [x["id"] for x in mod.suggest(archetypes, 6, seed, [])]
    c = [x["id"] for x in mod.suggest(archetypes, 6, "2026072521", [])]
    if a != b:
        print("FAIL: suggest non deterministico a parità di seed")
        fails += 1
    elif a == c:
        print("FAIL: l'ora successiva non muove la shortlist")
        fails += 1
    elif len({x.split("-")[0] for x in a}) < 4:
        print(f"FAIL: shortlist poco diversa: {a}")
        fails += 1
    else:
        print("PASS: shortlist deterministica per seed, diversa l'ora dopo")

    picked = mod.suggest(archetypes, 6, seed, [])
    excluded = mod.suggest(archetypes, 6, seed, [picked[0]["id"], picked[1]["treatment"]])
    if any(x["id"] == picked[0]["id"] for x in excluded):
        print("FAIL: esclusione per id ignorata")
        fails += 1
    elif any(x["treatment"] == picked[1]["treatment"] for x in excluded):
        print("FAIL: esclusione per hero_treatment ignorata")
        fails += 1
    else:
        print("PASS: le esclusioni da MEMORY escono dal pool")

    if len({x["media"] for x in picked}) != len(picked):
        print(f"FAIL: shortlist con media ripetuti: {[x['media'] for x in picked]}")
        fails += 1
    else:
        print("PASS: la shortlist non ripete media né placement")

    r = subprocess.run([sys.executable, str(SCRIPT), "--check"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAIL: assets/hero-gallery.html non è in sync col catalogo — esegui --build ({r.stdout.strip()})")
        fails += 1
    else:
        print("PASS: la pagina committata è in sync col catalogo")

    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--filter", "media=carousel", "--format", "json"],
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(r.stdout)
    except json.JSONDecodeError as e:
        print(f"FAIL: json CLI non parseabile: {e}")
        fails += 1
    else:
        if not payload or any(x["media"] != "carousel" for x in payload):
            print("FAIL: il filtro non ha filtrato")
            fails += 1
        else:
            print(f"PASS: filtro CLI ({len(payload)} caroselli)")

    r = subprocess.run([sys.executable, str(SCRIPT), "--show", ids[0]], capture_output=True, text=True)
    if r.returncode != 0 or "hero_treatment" not in r.stdout:
        print("FAIL: --show non stampa il dettaglio")
        fails += 1
    else:
        print("PASS: --show stampa gli assi dell'archetipo")

    r = subprocess.run([sys.executable, str(SCRIPT), "--show", "non-esiste"], capture_output=True, text=True)
    if r.returncode == 0:
        print("FAIL: --show su id inesistente esce 0")
        fails += 1
    else:
        print("PASS: --show su id inesistente fallisce")

    fails += check_in_browser(mod, catalog)
    return 1 if fails else 0


def check_in_browser(mod, catalog) -> int:
    """Il filtro davvero cliccato: ogni chip contro il catalogo, unione, intersezione, ricerca."""
    if importlib.util.find_spec("playwright") is None:
        print("SKIP: playwright assente — filtro non verificato nel browser")
        return 0
    from playwright.sync_api import sync_playwright  # noqa: PLC0415

    archetypes = catalog["archetypes"]
    problems: list[str] = []
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(channel="chrome")
        except Exception as e:  # nessun browser installato: non è un difetto della pagina
            print(f"SKIP: browser non avviabile ({type(e).__name__}) — filtro non verificato")
            return 0
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(f"file://{mod.PAGE}")
        page.wait_for_selector(".card")

        def shown():
            return set(page.eval_on_selector_all(".card:not([hidden])", "e => e.map(c => c.dataset.id)"))

        def check(name, got, want):
            if got != want:
                problems.append(name)

        check("stato iniziale", shown(), {a["id"] for a in archetypes})
        # Un filtro solo, quello sul media: testo e pannello si vedono guardando
        # la miniatura, e ventitré pulsanti sopra gli esempi erano più da leggere
        # che da usare.
        for value in catalog["axes"]["media"]:
            page.click("#reset")
            page.click(f'.chip[data-group="media"][data-value="{value}"]')
            check(f"media={value}", shown(), {a["id"] for a in archetypes if a["media"] == value})
        check("nessun filtro oltre al media", page.locator('.chip').count(),
              len(catalog["axes"]["media"]))
        page.click("#reset")
        page.click('.chip[data-group="media"][data-value="video"]')
        page.click('.chip[data-group="media"][data-value="carousel"]')
        check("unione nello stesso filtro", shown(),
              {a["id"] for a in archetypes if a["media"] in ("video", "carousel")})
        page.click('.chip[data-group="media"][data-value="carousel"]')
        check("secondo click spegne il chip", shown(),
              {a["id"] for a in archetypes if a["media"] == "video"})
        page.click("#reset")
        page.fill("#q", "prima neve")
        check("ricerca sul testo della miniatura", shown(),
              {a["id"] for a in archetypes if a["photo"] == "snow"})
        page.click("#reset")
        check("azzera", (shown(), page.input_value("#q")), ({a["id"] for a in archetypes}, ""))

        page.evaluate("document.querySelectorAll('img').forEach(i => { i.loading = 'eager'; })")
        page.wait_for_function("Array.from(document.images).every(i => i.complete)", timeout=15000)
        broken = page.evaluate(
            "Array.from(document.images).filter(i => i.naturalWidth === 0).map(i => i.src)")
        if broken:
            problems.append(f"immagini non caricate: {len(broken)}")
        browser.close()

    if problems:
        print(f"FAIL: filtro/immagini nel browser: {problems}")
        return 1
    print("PASS: filtro verificato nel browser (ogni chip, unione, intersezione, ricerca, azzera)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
