#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Il check di chiusura, in un comando solo — e con una traccia.

Perché esiste, misurato. Le regole di chiusura c'erano già: colore verificato,
responsive provato, nessun segnaposto, `dati_verosimili` nel DESIGN. Erano
quattro cose sparse, e l'ultima riga di `apply-frontend.md` le elencava tutte
insieme — il punto del documento che si legge quando il contesto è più lungo e
la pagina sembra finita. Su cinque pagine prodotte negli eval, **tre uscivano
con `repeat_guard` a 1**: `#395058` croma 12.2, `#273139` croma 7.1,
`#1d5b62` croma 27.1, tutte su fasce a piena larghezza. Non perché la regola
mancasse: perché nessuno aveva eseguito il controllo prima di consegnare.

Cinque controlli da ricordare diventano un comando da eseguire. E l'esito non
resta in chat: `--design` lo scrive nel DESIGN.md, così «ho chiuso la pagina» è
una cosa che si può verificare dopo, invece di una cosa che si dichiara.

Cosa controlla:
  1. colore      — repeat_guard: croma dello scuro, settore dominante, serie,
                   quota della famiglia, i tre hard-reject
  1b. caratteri  — display/body/mono risolti anche attraverso le variabili, con
                   le stesse due regole del colore: di fila e di quota
  2. responsive  — viewport meta, griglie che collassano, niente larghezze fisse
  3. finito      — nessun TODO / lorem ipsum / «da sostituire» nel consegnato
  4. traccia     — `dati_verosimili:` nel DESIGN.md quando i testi non erano dati
  5. consiglio   — `docs/consiglio/<slug>.md` con almeno una seduta registrata:
                   il consiglio decide tutto senza interpellare l'owner, e senza
                   quel file non resta scritto da nessuna parte chi c'era
  6. dashboard   — solo con `--surface dashboard`: profilo e logout sempre; ogni
                   tabella con paginazione e filtro con autocomplete; il DESIGN
                   dichiara `paginazione:` e `filtro:` (server side, strategia,
                   requisiti per il back end)

Usage:
    uv run scripts/close_check.py apps/<slug>/index.html
    uv run scripts/close_check.py apps/<slug>/index.html --ledger _bmad/memory/agent-frontend-taste/craft-ledger.json
    uv run scripts/close_check.py apps/<slug>/index.html --design apps/<slug>/DESIGN.md
    uv run scripts/close_check.py apps/<slug>/index.html --council docs/consiglio/<slug>.md
    uv run scripts/close_check.py apps/<slug>/*.html --surface dashboard --design apps/<slug>/DESIGN.md
    uv run scripts/close_check.py apps/<slug>/*.html --format json

Exit: 0 si consegna · 1 c'è da correggere · 2 non misurabile (non è un pass).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _repeat_guard():
    """Il guard è il motore del colore: si importa, non si riscrive."""
    spec = importlib.util.spec_from_file_location("repeat_guard", HERE / "repeat_guard.py")
    if not spec or not spec.loader:
        raise SystemExit("repeat_guard.py non trovato accanto a close_check.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("repeat_guard", mod)
    spec.loader.exec_module(mod)
    return mod


VIEWPORT_RE = re.compile(r"<meta[^>]+name=[\"']viewport[\"'][^>]*width=device-width", re.I)
MEDIA_RE = re.compile(r"@media[^{]*\(", re.I)
FLUID_GRID_RE = re.compile(r"auto-fit|auto-fill|minmax\(|flex-wrap|grid-template-columns:\s*1fr", re.I)
FIXED_WIDTH_RE = re.compile(r"(?:^|[^-\w])width\s*:\s*(\d{4,})px", re.I)

# I marcatori che un lavoro consegnato non contiene mai. `\bTODO\b` con i
# confini di parola, o «Metodo» conta come segnaposto — successo davvero,
# durante la review di questo skill.
PLACEHOLDER_RE = re.compile(
    r"\bTODO\b|\bFIXME\b|\bXXX\b|lorem ipsum|\[INSERIRE|da sostituire|"
    r"testo di esempio|your headline here|placeholder text", re.I)

# Un contatto vero, non un carattere che gli somiglia: cercare `@` da solo
# faceva scattare `@media` — la stessa trappola di `TODO` dentro «Metodo».
DATA_HINT_RE = re.compile(
    r"[\w.+-]+@[\w-]+\.[a-z]{2,}"          # email
    r"|\+39[\s./-]?\d[\s./-]?\d{2,}"       # telefono con prefisso
    r"|\b0\d{1,3}[\s./-]?\d{5,}\b"         # fisso italiano
    r"|€\s?\d|\d+[.,]\d{2}\s?€"            # prezzi
    r"|\b\d{1,2}[:.]\d{2}\s?[–-]\s?\d{1,2}[:.]\d{2}\b",   # fasce orarie
    re.I)


def check_responsive(text: str) -> tuple[bool, list[str]]:
    problems = []
    if not VIEWPORT_RE.search(text):
        problems.append("manca il `<meta name=\"viewport\" content=\"width=device-width…\">`: "
                        "sul telefono la pagina esce rimpicciolita")
    if not (MEDIA_RE.search(text) or FLUID_GRID_RE.search(text)):
        problems.append("nessuna media query e nessuna griglia fluida: il layout non collassa")
    fixed = [m.group(1) for m in FIXED_WIDTH_RE.finditer(text) if int(m.group(1)) >= 1000]
    if fixed:
        problems.append(f"larghezza fissa di {fixed[0]}px: sotto quella misura la pagina sfora")
    return not problems, problems


def check_finished(text: str) -> tuple[bool, list[str]]:
    found = sorted({m.group(0).lower() for m in PLACEHOLDER_RE.finditer(text)})
    return (not found), ([f"segnaposto nel file consegnato: {', '.join(found)}"] if found else [])


def check_design(design: Path | None, page_text: str) -> tuple[bool, list[str]]:
    """`dati_verosimili` serve quando la pagina espone contatti, prezzi, orari."""
    if not DATA_HINT_RE.search(page_text):
        return True, []
    if design is None or not design.is_file():
        return False, ["la pagina espone contatti/prezzi/orari ma non c'è un DESIGN.md: "
                       "l'elenco di cosa è inventato deve restare scritto (la chat sparisce, "
                       "il sito no)"]
    if "dati_verosimili" not in design.read_text(encoding="utf-8", errors="replace"):
        return False, [f"`{design.name}` non dichiara `dati_verosimili:`: senza, fra sei mesi "
                       "nessuno sa quale numero di telefono era inventato"]
    return True, []


# Le pagine di servizio che gli script generano dentro `apps/<slug>/` —
# `palette.html`, il catalogo hero — non sono lavoro consegnato: contengono di
# proposito più palette in un file solo, e misurarle come una pagina vera dà un
# fallimento garantito. Si riconoscono dalla firma che chi le genera ci mette.
GENERATED_RE = re.compile(r"<html[^>]+data-generated-by=[\"']([^\"']+)", re.I)

# --- Tabelle di dashboard: paginazione e filtro non si ricordano, si misurano.
# Marcatori volutamente larghi: qui un falso allarme costa una riga di markup,
# un falso via libera costa una tabella che regge solo i dati finti.
TABLE_RE = re.compile(r"<table\b|role=[\"']grid[\"']|role=[\"']table[\"']", re.I)
PAGING_RE = re.compile(r"class=[\"'][^\"']*(?:pagin|pager)|aria-label=[\"'][^\"']*pagin"
                       r"|aria-current=[\"']page|data-page\b|rel=[\"']next[\"']", re.I)
FILTER_RE = re.compile(r"type=[\"']search[\"']|class=[\"'][^\"']*filtr?|"
                       r"aria-label=[\"'][^\"']*filtr?|<form[^>]*\bfilter", re.I)
AUTOCOMPLETE_RE = re.compile(r"role=[\"']combobox[\"']|aria-autocomplete|<datalist\b", re.I)
LOGOUT_RE = re.compile(r"logout|log-out|sign.?out|esci\b|disconnett", re.I)
PROFILE_RE = re.compile(r"profil|account|/me\b|mio-account|impostazioni account", re.I)


def check_dashboard(text: str, design: Path | None) -> tuple[bool, list[str]]:
    """Solo su `--surface dashboard`. Le tabelle si controllano se ci sono; profilo
    e logout no: un'area riservata da cui non si esce non è consegnabile."""
    problems = []
    if not LOGOUT_RE.search(text):
        problems.append("nessun logout: da un'area riservata si deve poter uscire, "
                        "e l'uscita chiude la sessione **sul server** "
                        "(`dashboard-rules.md` → Account)")
    if not PROFILE_RE.search(text):
        problems.append("nessun profilo: è il posto del cambio password, e il cambio "
                        "chiede la password attuale")
    if not TABLE_RE.search(text):
        return not problems, problems
    if not PAGING_RE.search(text):
        problems.append("tabella senza paginazione: regge finché i dati sono finti "
                        "(`dashboard-rules.md` → Tabelle)")
    if not FILTER_RE.search(text):
        problems.append("tabella senza filtro: il default è multicampo e server side, "
                        "non una casella di ricerca e nemmeno niente")
    elif not AUTOCOMPLETE_RE.search(text):
        problems.append("filtro senza autocomplete (`role=\"combobox\"`, `aria-autocomplete` "
                        "o `<datalist>`): manca il pezzo che lo rende usabile")
    # La forma si vede nel markup; server side e requisiti di backend no —
    # quelli esistono solo se qualcuno li ha scritti.
    if design is None or not design.is_file():
        problems.append("nessun DESIGN.md: `paginazione:` e `filtro:` (modo, campi, "
                        "strategia, requisiti backend) non sono dichiarati da nessuna parte")
    else:
        d = design.read_text(encoding="utf-8", errors="replace")
        missing = [k for k in ("paginazione:", "filtro:") if k not in d]
        if missing:
            names = " e ".join(f"`{k.rstrip(':')}`" for k in missing)
            problems.append(f"`{design.name}` non dichiara {names}: "
                            "server side, strategia e requisiti per il back end non si "
                            "leggono dal markup — o si scrivono, o nessuno li ha decisi")
    return not problems, problems


COUNCIL_ENTRY_RE = re.compile(r"^- \*\*\d{4}-\d{2}-\d{2}", re.M)


def check_council(council: Path | None) -> tuple[bool, list[str]]:
    """Il registro delle sedute: chi c'era, in una riga per seduta.

    Il motore è `council_log.py`; qui si verifica solo che il registro esista e
    non sia vuoto — perché è l'ultimo momento in cui qualcuno guarda.
    """
    if council is None:
        return False, ["nessun `--council`: passa `docs/consiglio/<slug>.md`. "
                       "Il consiglio ha deciso tutto senza chiedere niente all'owner; "
                       "se non resta scritto chi c'era, non resta niente"]
    if not council.is_file():
        return False, [f"`{council}` non esiste: le sedute del consiglio non sono state "
                       "registrate. Una riga per seduta, con `council_log.py`"]
    if not COUNCIL_ENTRY_RE.search(council.read_text(encoding="utf-8", errors="replace")):
        return False, [f"`{council.name}` non ha nemmeno una seduta registrata: "
                       "è un titolo senza registro"]
    return True, []


def check_colour(pg, text: str, last: list[str], ledger: Path | None,
                 page: Path) -> tuple[int, dict, list[str]]:
    """(stato, report, problemi) — stato 0 ok, 1 violazioni, 2 non misurabile."""
    pairs, painted, small, ok = pg.measured_pairs(text)
    if not ok or not pairs:
        return 2, {}, [pg.unmeasurable_note(text)]
    report = pg.analyse(pairs, painted, small)
    report["typefaces"] = pg.typefaces(text)
    report["layout"] = pg.layout_signature(text)
    rejects = pg.hard_rejects(text, pg.palette_colours(text, report["colours"]))
    entries, last_fonts = [], []
    if ledger:
        entries = pg.ledger_load(ledger)
        last_fonts = pg.ledger_fonts(entries)
        if not any(s.strip() for s in last):
            last = pg.ledger_sectors(entries)
    problems = pg.violations(report, last, last_fonts) + rejects
    if ledger:
        pg.ledger_record(ledger, entries, str(page.resolve()), report)
    return (1 if problems else 0), report, problems


def design_lines(report: dict) -> list[str]:
    ink = report.get("ink") or {}
    return [
        "```yaml",
        f"hue_sector: {report.get('dominant_sector')}",
        f"ink_family: {report.get('ink_family')}"
        + (f"   # {ink.get('hex')} croma {ink.get('chroma')}" if ink else ""),
        "close_check: passato",
        "```",
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description="Check di chiusura di una pagina consegnata")
    ap.add_argument("pages", nargs="+", help="file HTML consegnati")
    ap.add_argument("--design", help="DESIGN.md di accompagnamento")
    ap.add_argument("--council", help="registro del consiglio, docs/consiglio/<slug>.md")
    ap.add_argument("--surface", choices=("marketing", "dashboard", "mobile"),
                    help="dashboard → controlla anche paginazione e filtro delle tabelle")
    ap.add_argument("--ledger", help="registro dei settori di tinta "
                    "(default: quello condiviso fra progetti)")
    ap.add_argument("--no-ledger", action="store_true",
                    help="non leggere né scrivere il registro condiviso")
    ap.add_argument("--last", default="", help="settori recenti, il più recente per primo")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    args = ap.parse_args()

    pg = _repeat_guard()
    design = Path(args.design) if args.design else None
    council = Path(args.council) if args.council else None
    ledger = (Path(args.ledger) if args.ledger
              else (None if args.no_ledger else pg.default_ledger()))
    last = args.last.split(",")

    worst, out, blocks, reports = 0, [], [], []
    skipped: list[tuple[Path, str]] = []
    for raw in args.pages:
        page = Path(raw)
        if not page.is_file():
            raise SystemExit(f"file inesistente: {page}")
        text = page.read_text(encoding="utf-8", errors="replace")

        gen = GENERATED_RE.search(text)
        if gen:
            skipped.append((page, gen.group(1)))
            continue

        colour_state, report, colour_problems = check_colour(pg, text, last, ledger, page)
        resp_ok, resp_problems = check_responsive(text)
        fin_ok, fin_problems = check_finished(text)
        des_ok, des_problems = check_design(design, text)
        cou_ok, cou_problems = check_council(council)
        dash_ok, dash_problems = (check_dashboard(text, design)
                                  if args.surface == "dashboard" else (True, []))

        problems = (colour_problems + resp_problems + fin_problems
                    + des_problems + cou_problems + dash_problems)
        state = 2 if colour_state == 2 else (1 if problems else 0)
        worst = max(worst, state)
        if report:
            reports.append(report)
        out.append({
            "page": str(page), "state": state,
            "colour": {"dominant_sector": report.get("dominant_sector"),
                       "ink_family": report.get("ink_family")} if report else None,
            "problems": problems,
        })

        lines = [f"## {page}", ""]
        mark = {0: "OK", 1: "DA CORREGGERE", 2: "NON MISURABILE"}[state]
        lines.append(f"**{mark}**")
        if report:
            ink = report.get("ink") or {}
            lines.append(f"- colore: settore **{report['dominant_sector']}** · "
                         f"`ink_family: {report['ink_family']}`"
                         + (f" ({ink.get('hex')}, croma {ink.get('chroma')})" if ink else ""))
        faces = (report or {}).get("typefaces") or {}
        if faces:
            lines.append("- caratteri: " + " · ".join(f"{k} **{v}**" for k, v in faces.items()))
        lay = (report or {}).get("layout") or {}
        if lay:
            lines.append("- impaginazione: " + " · ".join(f"{k.split('_')[0]} **{v}**"
                                                          for k, v in lay.items()))
        lines.append(f"- responsive: {'ok' if resp_ok else 'da correggere'}")
        lines.append(f"- finito: {'nessun segnaposto' if fin_ok else 'da correggere'}")
        lines.append(f"- traccia: {'ok' if des_ok else 'da correggere'}")
        lines.append(f"- consiglio: {'registrato' if cou_ok else 'da correggere'}")
        if args.surface == "dashboard":
            lines.append(f"- dashboard: {'profilo, uscita, tabelle' if dash_ok else 'da correggere'}")
        if problems:
            lines.append("")
            lines.extend(f"  - {p}" for p in problems)
        blocks.append("\n".join(lines))

    if not out and skipped:
        print("Solo pagine generate, nessun lavoro consegnato da misurare: "
              + ", ".join(f"{p} ({by})" for p, by in skipped), file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps({"pages": out, "state": worst,
                          "skipped": [{"page": str(p), "generated_by": by} for p, by in skipped]},
                         ensure_ascii=False, indent=1))
        return worst

    print("# Check di chiusura\n")
    print("\n\n".join(blocks))
    print()
    for p, by in skipped:
        print(f"_Saltata `{p}`: la genera `{by}`, non è lavoro consegnato._")
    if skipped:
        print()
    if worst == 0:
        print("Si consegna. Nel `DESIGN.md` va la traccia di ciò che è stato misurato "
              "— così «l'ho controllato» resta verificabile anche fra sei mesi:\n")
        print("\n".join(design_lines(reports[0] if reports else {})))
    elif worst == 1:
        print("**Non si consegna così:** correggi i punti qui sopra e rilancia. "
              "Un difetto trovato adesso costa una riga; trovato dal cliente costa la pagina.")
    else:
        print("**Non è un pass:** la palette non è leggibile da questo file. Misura il file "
              "che dichiara i colori, o passa la palette a `repeat_guard.py --hex`. "
              "Finché non è misurata, non si dichiara «pulita».")
    return worst


if __name__ == "__main__":
    sys.exit(main())
