# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for palette_guard.py — run: uv run scripts/tests/test-palette-guard.py"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "palette_guard.py"


def load():
    spec = importlib.util.spec_from_file_location("palette_guard", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["palette_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


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

    r_hex = run("--hex", "#15171A,#B8895A,#F5F3EF")
    check("modalità --hex funziona senza CSS", r_hex.returncode, 0)
    check("--hex senza violazioni su palette pulita", "Nessuna violazione" in r_hex.stdout)
    check("hex non valido rifiutato", run("--hex", "#zzz").returncode != 0)
    check("file inesistente rifiutato", run("--check", "/tmp/non-esiste-xyz.html").returncode != 0)

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
