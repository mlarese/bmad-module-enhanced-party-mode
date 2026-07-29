# /// script
# requires-python = ">=3.10"
# ///
"""Il lock **è** l'esecuzione dei cataloghi — run: uv run scripts/tests/test-craft-lock-equivalenza.py

Perché esiste. Per tre file — `SKILL.md`, `apply-frontend.md`, `ciclo-rapido.md` —
la regola era «i cataloghi si eseguono, non si citano», e li elencava uno per
uno: `accent_pool --suggest`, `font_pool`, `shape_pool`, `hero_gallery --suggest`,
`effects_gallery`. Ma `craft_lock.py` **li importa e li chiama lui**
(righe 95, 121, 133): con lo stesso seed i due percorsi danno gli stessi identici
valori, e le cinque chiamate a parte erano cinque giri di andata e ritorno per
niente. In un ciclo che esiste per la rapidità.

Misurato il 2026-07-29, dopo che l'owner ha detto «il rapido ci mette tanto lo
stesso»: ~19 chiamate per una landing, cinque delle quali ridondanti.

Questo test è ciò che rende sicura la scorciatoia. Se un domani il lock smette di
usare i cataloghi — o li usa con un altro seed, o cambia l'ordine di sorteggio —
la scorciatoia diventa silenziosamente «decide il pregiudizio», che è esattamente
il difetto misurato (terracotta, pillola, `DM Mono`, griglia a rail) che i
cataloghi erano nati per impedire. Non lo si vedrebbe rileggendo il diff: si
vedrebbe solo confrontando i due percorsi, cioè qui.

Non verifica che il lock sia *bello*: verifica che sia **lo stesso**.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
LOCK = SCRIPTS / "craft_lock.py"


def carica(nome: str, dove: Path = SCRIPTS):
    spec = importlib.util.spec_from_file_location(nome, dove / f"{nome}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    fails = 0
    lk = carica("craft_lock")

    def check(label, got, want=True):
        nonlocal fails
        if got == want:
            print(f"PASS: {label}")
        else:
            print(f"FAIL: {label}\n  atteso: {want}\n  ottenuto: {got}")
            fails += 1

    seed, slug = "2026072914", "trattoria"

    def lock_da_cli(progetto: str, sem: str) -> dict:
        """Si passa dalla CLI: è il contratto vero, quello che i reference dicono
        di eseguire, e non si rinomina senza che qualcuno se ne accorga."""
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "craft-lock.json"
            r = subprocess.run([sys.executable, str(LOCK), "--project", progetto,
                                "--seed", sem, "--surface", "marketing",
                                "--out", str(out)], capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            return json.loads(out.read_text(encoding="utf-8"))

    lock = lock_da_cli(slug, seed)
    check("la CLI del lock produce un lock completo",
          all(k in lock for k in ("colore", "font", "forma", "hero", "effetti")))

    s = lk.semina(seed, slug)
    check("il seed porta lo slug", s.endswith(f"-{slug}"))

    # --- equivalenza, catalogo per catalogo ---------------------------------
    ap, fp, sp = carica("accent_pool"), carica("font_pool"), carica("shape_pool")

    colore = ap.come_colore(ap.scegli(s, []))
    check("colore: lock == accent_pool", lock["colore"]["id"], colore["id"])
    check("e lo stesso esadecimale", lock["colore"]["accent"], colore["accent"])
    check("e la stessa famiglia", lock["colore"]["famiglia"], colore["famiglia"])

    font = fp.suggerisci(1, s, [])[0]
    check("font: lock == font_pool", lock["font"]["id"], font["id"])
    check("e lo stesso display", lock["font"]["display"], font["display"]["family"])

    forma = sp.suggerisci(1, s, [])[0]
    check("forma: lock == shape_pool", lock["forma"]["id"], forma["id"])
    check("e lo stesso radius_family",
          lock["forma"]["radius_family"], forma["radius_family"])

    hg = carica("hero_gallery")
    arche = hg.load()["archetypes"]
    atteso = hg.suggest(arche, 1, s, [])[0]
    check("hero: lock == hero_gallery",
          lock["hero"]["id"], atteso.get("id") or atteso.get("n"))

    check("gli effetti ci sono", len(lock.get("effetti") or []) >= 1)

    # --- e non è un caso: cambiando seed cambia tutto, in tandem ------------
    # Se il lock ignorasse i cataloghi e restituisse costanti, i test sopra
    # passerebbero solo su questo seed. Con un seed diverso i due percorsi devono
    # cambiare **insieme**.
    seed2 = "2026081003"
    lock2 = lock_da_cli(slug, seed2)
    s2 = lk.semina(seed2, slug)
    check("seed diverso: colore ancora allineato",
          lock2["colore"]["id"], ap.come_colore(ap.scegli(s2, []))["id"])
    check("seed diverso: font ancora allineato",
          lock2["font"]["id"], fp.suggerisci(1, s2, [])[0]["id"])
    check("e qualcosa è davvero cambiato",
          (lock2["colore"]["id"], lock2["font"]["id"], lock2["forma"]["id"])
          != (lock["colore"]["id"], lock["font"]["id"], lock["forma"]["id"]))

    # --- lo slug entra nel sorteggio ----------------------------------------
    # Due progetti nella stessa ora non devono uscire identici: è il difetto per
    # cui il seed porta lo slug, e la scorciatoia non deve rimetterlo.
    lock3 = lock_da_cli("altro-progetto", seed)
    check("stesso seed, progetto diverso: non esce la stessa pagina",
          (lock3["colore"]["id"], lock3["font"]["id"], lock3["forma"]["id"])
          != (lock["colore"]["id"], lock["font"]["id"], lock["forma"]["id"]))

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
