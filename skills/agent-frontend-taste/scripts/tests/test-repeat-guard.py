# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for repeat_guard.py — run: uv run scripts/tests/test-repeat-guard.py"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "repeat_guard.py"

# I test non toccano il registro vero: il default e condiviso e sta in $HOME,
# e senza questa riga una suite di unit test scrive 22 finte consegne nella
# storia di craft dell'owner. E successo: le abbiamo tolte a mano.
_ISO = tempfile.mkdtemp(prefix="guard-test-ledger-")
_ENV = {**os.environ, "VESPER_CRAFT_LEDGER": str(Path(_ISO) / "ledger.json")}



def load():
    spec = importlib.util.spec_from_file_location("repeat_guard", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["repeat_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, env=_ENV)


PAGE = """
<style>
:root{
  --paper:#F3F0EA;      /* fondo chiaro */
  --abete:#1A2A22;      /* verde scuro, dipinge la hero */
  --rame:#B8895A;       /* accento caldo */
  --muted:#5C6B62;
}
body{background:var(--paper);}
.hero{background:var(--abete);}
footer{background:var(--abete);}
.badge{border-color:var(--rame);}
</style>
"""


def main() -> int:
    fails = 0
    mod = load()

    def check(label, got, want=True):
        nonlocal fails
        if got == want:
            print(f"PASS: {label}")
        else:
            print(f"FAIL: {label}\n  atteso: {want}\n  ottenuto: {got}")
            fails += 1

    # --- hue sectors --------------------------------------------------------
    check("verde riconosciuto", mod.sector_of(*mod.to_hsl("#1A2A22")), "verde")
    check("teal riconosciuto", mod.sector_of(*mod.to_hsl("#0A1B22")), "teal")
    check("terra riconosciuta", mod.sector_of(*mod.to_hsl("#B8895A")), "terra")
    check("il rosso attraversa lo zero", mod.sector_of(2, 60), "rosso")
    check("grigio = neutro, non un settore", mod.sector_of(150, 3, 50), "neutro")
    check("il quasi-nero non è un settore di tinta",
          mod.sector_of(*mod.to_hsl("#0A0C0E")), "neutro")

    # --- chroma: saturation alone lies about darks -------------------------
    # #0A0C0E is S=17% but sits at L=5%: black, not blue. Judging it by
    # saturation flagged it; judging it by chroma does not.
    near_black = mod.chroma(*mod.to_hsl("#0A0C0E")[1:])
    mid_teal = mod.chroma(*mod.to_hsl("#12323a")[1:])
    check("il quasi-nero ha croma trascurabile", near_black < 3)
    check("il teal medio ha croma alto", mid_teal > 12)
    check("stessa saturazione, croma diverso secondo la luminosità",
          mod.chroma(50, 8) < mod.chroma(50, 45))
    check("ink quasi-nero → famiglia neutro",
          mod.ink_family(*mod.to_hsl("#0A0C0E")), "neutro")
    check("ink bruno → famiglia caldo",
          mod.ink_family(*mod.to_hsl("#2A1B10")), "caldo")

    # --- large areas are measured from the CSS, not guessed from the name ---
    painted = mod.large_area_tokens(PAGE)
    check("il token che dipinge la hero è area grande", "--abete" in painted)
    check("il fondo del body è area grande", "--paper" in painted)
    check("l'accento su un bordo non è area grande", "--rame" in painted, False)

    report = mod.analyse(mod.parse_colours(PAGE), painted)
    check("settore dominante dalle superfici, non dall'accento",
          report["dominant_sector"], "verde")
    check("lo scuro strutturale è quello dipinto",
          report["ink"]["token"], "--abete")

    # --- violations ---------------------------------------------------------
    v = mod.violations(report, [])
    check("scuro colorato su superficie grande segnalato",
          any("scuro strutturale colorato" in x for x in v))

    v_streak = mod.violations(report, ["verde", "verde", "teal"])
    check("due job di fila nello stesso settore → violazione",
          any("settore ripetuto" in x for x in v_streak))
    v_ok = mod.violations(report, ["terra", "verde"])
    check("settore diverso dall'ultimo → nessuna violazione di ripetizione",
          any("settore ripetuto" in x for x in v_ok), False)

    # a compliant palette: neutral dark, accent elsewhere
    good = "<style>:root{--paper:#F5F3EF;--ink:#15171A;--brass:#B8895A;}body{background:var(--paper);}.hero{background:var(--ink);}</style>"
    gp = mod.large_area_tokens(good)
    gr = mod.analyse(mod.parse_colours(good), gp)
    check("scuro quasi-neutro non è segnalato",
          any("scuro strutturale colorato" in x for x in mod.violations(gr, [])), False)

    # --- CLI ----------------------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "pagina.html"
        p.write_text(PAGE, encoding="utf-8")
        r = run("--check", str(p), "--format", "json")
        check("CLI json valido", json.loads(r.stdout)["dominant_sector"], "verde")
        check("exit non-zero quando ci sono violazioni", r.returncode != 0)
        r_md = run("--check", str(p))
        check("il report md nomina il settore", "settore dominante" in r_md.stdout)

    # --- regressioni misurate (adversarial review 2026-07-26) ---------------
    # Tre pagine che portavano #1A2A22 — il verde citato nella docstring — e
    # uscivano tutte con "nessuna violazione" ed exit 0.
    def measure(src: str) -> tuple[dict, list[str]]:
        pairs, big, small_, ok = mod.measured_pairs(src)
        assert ok, "sorgente non misurabile"
        rep = mod.analyse(pairs, big, small_)
        return rep, mod.violations(rep, [])

    dark = "--abete:#1A2A22"
    off_dict = ("<style>:root{--paper:#F3F0EA;" + dark + ";--rame:#C96F3A;}"
                "body{background:var(--paper);}.s-hero{background:var(--abete);}</style>")
    r1, v1 = measure(off_dict)
    check("classe fuori dizionario: la hero è area grande", r1["dominant_sector"], "verde")
    check("classe fuori dizionario: scuro colorato segnalato",
          any("scuro strutturale colorato" in x for x in v1))

    inline = ("<style>:root{--paper:#F3F0EA;--rame:#C96F3A;}"
              "body{background:var(--paper);}.hero{background:#1A2A22;}</style>")
    r2, v2 = measure(inline)
    check("hex inline nel background: misurato per intero",
          any(c["hex"].upper() == "#1A2A22" for c in r2["colours"]))
    check("hex inline: scuro colorato segnalato",
          any("scuro strutturale colorato" in x for x in v2))

    themed = ("<style>:root{--paper:#F3F0EA;" + dark + ";}"
              'body{background:var(--paper);}[data-theme="dark"]{background:var(--abete);}</style>')
    _r3, v3 = measure(themed)
    check("data-theme sulla sezione (pattern prescritto) è misurato",
          any("scuro strutturale colorato" in x for x in v3))

    small_only = ("<style>:root{--paper:#F3F0EA;--acid:#1A2A22;}"
                  "body{background:var(--paper);}.btn{background:var(--acid);}</style>")
    _r4, v4 = measure(small_only)
    check("un bottone non è una superficie",
          any("scuro strutturale colorato" in x for x in v4), False)

    # Utility-class stack: la palette sta nella mappa di tema, non in --var.
    tw = ("<script>theme={colors:{abete:'#1A2A22',paper:'#F3F0EA'}}</script>"
          '<body class="bg-paper"><section class="bg-abete"></section>'
          '<svg><path fill="#8B5CF6"/></svg>')
    r5, v5 = measure(tw)
    check("utility class: settore dominante dalla mappa, non dall'icona SVG",
          r5["dominant_sector"], "verde")
    check("utility class: scuro colorato segnalato",
          any("scuro strutturale colorato" in x for x in v5))

    # Niente da misurare → si dichiara, non si inventa un dominante.
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "utility.html"
        p.write_text('<div class="bg-slate-900 text-white">x</div>', encoding="utf-8")
        r = run("--check", str(p))
        check("pagina non misurabile → exit 2", r.returncode, 2)
        check("pagina non misurabile → lo dice", "NON MISURABILE" in r.stderr)

    # --- hard-rejects -------------------------------------------------------
    purple = ("<style>:root{--paper:#FAFAFA;--ink:#151719;--brand:#8B5CF6;}"
              "body{background:var(--paper);}.hero{background:var(--ink);}</style>")
    pr, pbig, psmall, _ = mod.measured_pairs(purple)
    prep = mod.analyse(pr, pbig, psmall)
    check("purple-indigo AI rifiutato",
          any("purple-indigo" in x
              for x in mod.hard_rejects(purple, mod.palette_colours(purple, prep["colours"]))))

    inter = ("<style>:root{--paper:#FAFAFA;--ink:#151719;}body{background:var(--paper);}"
             ".hero{background:var(--ink);}.hero-title{font-family:Inter,system-ui,sans-serif}</style>")
    ir, ibig, ismall, _ = mod.measured_pairs(inter)
    irep = mod.analyse(ir, ibig, ismall)
    check("Inter come display rifiutato",
          any("Inter/system" in x
              for x in mod.hard_rejects(inter, mod.palette_colours(inter, irep["colours"]))))
    check("sans-serif non conta come serif", bool(mod.SERIF_HINT_RE.search("sans-serif")), False)

    cream = ("<style>:root{--paper:#F4F1EA;--ink:#151719;--terra:#C96F3A;}"
             "body{background:var(--paper);}.hero{background:var(--ink);}"
             "h1{font-family:'Playfair Display',serif}</style>")
    cr, cbig, csmall, _ = mod.measured_pairs(cream)
    crep = mod.analyse(cr, cbig, csmall)
    check("cream+serif+terracotta rifiutato",
          any("cream+serif+terracotta" in x
              for x in mod.hard_rejects(cream, mod.palette_colours(cream, crep["colours"]))))

    # --- ledger: lo streak è un fatto registrato, non da ricordare -----------
    with tempfile.TemporaryDirectory() as td:
        led = Path(td) / "craft-ledger.json"
        for i in range(3):
            p = Path(td) / f"job{i}.html"
            p.write_text(off_dict, encoding="utf-8")
            r = run("--check", str(p), "--ledger", str(led))
        check("terzo job nello stesso settore → violazione dal ledger",
              "settore ripetuto" in r.stdout)
        entries = json.loads(led.read_text(encoding="utf-8"))
        check("il ledger registra un record per file", len(entries), 3)
        check("il ledger registra il settore misurato",
              entries[-1]["dominant_sector"], "verde")
        # Una pagina corretta sostituisce la propria lettura precedente.
        (Path(td) / "job2.html").write_text(
            "<style>:root{--paper:#F5F3EF;--ink:#15171A;}body{background:var(--paper);}"
            ".hero{background:var(--ink);}</style>", encoding="utf-8")
        run("--check", str(Path(td) / "job2.html"), "--ledger", str(led))
        entries2 = json.loads(led.read_text(encoding="utf-8"))
        check("un file corretto non lascia due record", len(entries2), 3)
        check("il record aggiornato riflette la correzione",
              entries2[-1]["dominant_sector"], "neutro")

    r_hex = run("--hex", "#15171A,#B8895A,#F5F3EF")
    check("modalità --hex funziona senza CSS", r_hex.returncode, 0)
    check("--hex senza violazioni su palette pulita", "Nessuna violazione" in r_hex.stdout)
    check("hex non valido rifiutato", run("--hex", "#zzz").returncode != 0)
    check("file inesistente rifiutato", run("--check", "/tmp/non-esiste-xyz.html").returncode != 0)

    # --- deroghe: ogni messaggio deve appartenere a un asse ------------------
    # Il difetto che questo test esiste per prendere: la regola di fila dice
    # «come display», quella di quota «è il display di», e le hint conoscevano
    # solo la prima. `--deroga display:…` zittiva la ripetizione e lasciava
    # passare la predominanza: una via d'uscita che funziona a meta e peggio di
    # una che non c'e, perche nessuno la verifica.
    mod = load()
    tutti = mod.font_violations({"display": "X", "body": "Y", "mono": "Z"},
                                [{"display": "X", "body": "Y", "mono": "Z"}] * 6)
    tutti += mod.layout_violations(
        {"grid_system": "rail", "radius_family": "pill", "hero_shape": "foto-piena"},
        [{"grid_system": "rail", "radius_family": "pill", "hero_shape": "foto-piena"}] * 6)
    check("i generatori producono messaggi da derogare", len(tutti) > 0, True)
    coperti = mod.apply_deroghe(tutti, {a: "motivo" for a in mod.AXES}, {})
    check("ogni violazione di ripetizione è attribuita a un asse",
          [m for m in coperti if not m.startswith("[deroga")], [])
    check("le deroghe non bloccano", mod.only_blocking(coperti), [])
    check("senza deroga invece bloccano", len(mod.only_blocking(tutti)), len(tutti))

    # --- l'accento: il colore della CTA, che nessuno contava -----------------
    # Misurato sulle cinque pagine consegnate: `rosso` su 3 su 5, e i quattro
    # esadecimali caldi nella stessa zona terracotta. Il ledger registrava il
    # settore dominante — fatto di fondo e scuro, quasi sempre neutri — e mai
    # l'accento, che e' l'unica tinta che l'occhio guarda per prima.
    rep = {"colours": [
        {"hex": "#f6f2ec", "sector": "neutro", "chroma": 3, "large_area": True},
        {"hex": "#14181c", "sector": "neutro", "chroma": 2, "large_area": True},
        {"hex": "#B7502F", "sector": "rosso", "chroma": 53, "large_area": False},
        {"hex": "#63734D", "sector": "verde", "chroma": 18, "large_area": False}]}
    a = mod.accent_of(rep)
    check("l'accento e il piu cromatico fuori dalle superfici grandi", a["hex"], "#B7502F")
    check("con la sua famiglia", a["famiglia"], "rosso")
    check("una pagina senza accento cromatico non ne inventa uno",
          mod.accent_of({"colours": [{"hex": "#111", "sector": "neutro",
                                      "chroma": 1, "large_area": True}]}), {})

    tre = [{"accent_family": "rosso"}] * 3
    check("tre CTA di fila nella stessa famiglia → violazione",
          len(mod.accent_violations(a, tre)) >= 1, True)
    check("e cambiando zona si torna puliti",
          mod.accent_violations({"famiglia": "blu"}, tre), [])

    # il pool: trenta zone, e la shortlist non le prende imparentate
    pool = SCRIPT.parent / "accent_pool.py"
    check("il catalogo esiste", pool.is_file(), True)
    spec2 = importlib.util.spec_from_file_location("accent_pool", pool)
    ap = importlib.util.module_from_spec(spec2)
    sys.modules["accent_pool"] = ap
    spec2.loader.exec_module(ap)
    check("trenta zone", len(ap.ZONE), 30)
    check("che coprono tutta la ruota, non solo il caldo",
          len({ap.settore(z["hue"]) for z in ap.ZONE}), 8)
    scelte = ap.suggerisci(4, "2026072712", [])
    check("la shortlist ha una zona per famiglia",
          len({z["famiglia"] for z in scelte}), len(scelte))
    check("e le esclusioni tolgono davvero la zona calda",
          all(z["famiglia"] not in ("rosso", "terra")
              for z in ap.suggerisci(4, "2026072712", ["rosso", "terra"])), True)

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
