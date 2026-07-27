#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""La pagina delle combinazioni: colori e caratteri, viste prima di sceglierli.

Perché esiste. La palette e i caratteri Vesper li decide da `locale + register +
activity` sul batch misurato, e li consegna applicati: è la legge — il craft non
si vota, e non si apre un catalogo in attesa di una scelta. Ma l'owner, la
combinazione applicata, la vede **solo dentro la pagina finita**, e le altre che
reggevano non le vede mai. Questa pagina gliele mostra: la scelta resta di
Vesper, l'alternativa smette di essere invisibile.

**Non è una domanda e non ferma niente.** Si genera *insieme* al lavoro
consegnato, con la combinazione scelta già applicata e marcata «in uso». Se
l'owner poi dice «metti la B», è lui che interviene di sua iniziativa — e allora
la sua parola vince: si aggiorna il DESIGN, si rifà la pagina, si rigenera
questa. Vedi `references/implementation-handoff.md` §10.1.

**Ogni combinazione mostrata è già legale.** Ognuna passa da `repeat_guard`
prima di comparire — croma dello scuro strutturale, settore dominante, serie del
ledger, i tre hard-reject. Una combinazione che l'owner non potrebbe scegliere
non si mostra: sarebbe un'offerta che si ritira dopo averla fatta.

Input: un JSON con le combinazioni derivate dal batch.

    {
      "project": "bellini", "surface": "marketing", "activity": "ortopedia",
      "register": "professionale", "locale": "Verona", "seed": "2026072616",
      "batch": {"count": 34, "source": "envato: medical, health"},
      "applied": "A",
      "combos": [
        {"id": "A", "name": "Pietra e ottone",
         "why": "lo scuro quasi-neutro regge il registro clinico; l'ottone…",
         "colours": {"ink": "#14181c", "paper": "#f6f2ec", "accent": "#8a6a3b"},
         "fonts": {
           "display": {"family": "Fraunces", "stack": "Georgia, serif",
                       "url": "https://fonts.googleapis.com/css2?family=Fraunces…"},
           "body":    {"family": "Inter Tight", "stack": "system-ui, sans-serif"}},
         "type": {"scale": "1.25", "tracking": "display -.02em · body 0"},
         "buttons": {"radius": "3px", "shape": "pieno + fantasma",
                     "pad": ".7em 1.4em", "case": "normale",
                     "fill": "#8a6a3b", "label": "#f6f2ec", "ghost": "#14181c"}}
      ]
    }

La forma dei pulsanti è un asse di craft, non una rifinitura: raggio, pieno o
contornato, respiro e maiuscoletto cambiano il registro quanto il carattere.
`fill`/`label`/`ghost` sono facoltativi — senza, il pieno usa l'accento sul
paper e il fantasma il contorno dell'inchiostro.

Usage:
    uv run scripts/palette_page.py combos.json --out apps/<slug>/palette.html
    uv run scripts/palette_page.py combos.json --out … --ledger …/craft-ledger.json
    uv run scripts/palette_page.py combos.json --out … --last verde,ambra

Exit: 0 pagina scritta · 1 una combinazione non è legale (si corregge e si
      rilancia: non si mostra ciò che non si può scegliere) · 2 input illeggibile.
"""

from __future__ import annotations

import argparse
import html as html_lib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROLES = ("ink", "paper", "accent")


def _repeat_guard():
    spec = importlib.util.spec_from_file_location("repeat_guard", HERE / "repeat_guard.py")
    if not spec or not spec.loader:
        raise SystemExit("repeat_guard.py non trovato accanto a palette_page.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("repeat_guard", mod)
    spec.loader.exec_module(mod)
    return mod


def combo_css(combo: dict) -> str:
    """Il CSS di una combinazione — lo stesso che il guard misurerà.

    `--accent` sta su `.spec__btn`: un accento su un bottone non è una
    superficie grande, e il guard lo classifica per il nome del selettore.
    """
    cid = combo["id"]
    col = combo["colours"]
    btn = combo.get("buttons") or {}
    extra = "".join(f"  --{k}: {v};\n" for k, v in col.items() if k not in ROLES)
    fill = btn.get("fill") or col["accent"]
    label = btn.get("label") or col["paper"]
    ghost = btn.get("ghost") or col["ink"]
    radius = btn.get("radius", "0")
    pad = btn.get("pad", ".7em 1.35em")
    case = "uppercase" if str(btn.get("case", "")).lower() in ("upper", "maiuscoletto") else "none"
    track = ".08em" if case == "uppercase" else "0"
    return (
        f'[data-combo="{cid}"] {{\n'
        f'  --ink: {col["ink"]};\n  --paper: {col["paper"]};\n'
        f'  --accent: {col["accent"]};\n'
        f'  --btn-fill: {fill};\n  --btn-label: {label};\n  --btn-ghost: {ghost};\n'
        f'  --btn-radius: {radius};\n  --btn-pad: {pad};\n{extra}}}\n'
        f'[data-combo="{cid}"] .spec__page {{ background: var(--paper); color: var(--ink); }}\n'
        f'[data-combo="{cid}"] .spec__band {{ background: var(--ink); color: var(--paper); }}\n'
        f'[data-combo="{cid}"] .spec__btn {{ background: var(--btn-fill); color: var(--btn-label);\n'
        f'  border-radius: var(--btn-radius); padding: var(--btn-pad);\n'
        f'  text-transform: {case}; letter-spacing: {track}; border: 1px solid var(--btn-fill); }}\n'
        f'[data-combo="{cid}"] .spec__btn--ghost {{ background: transparent; color: var(--btn-ghost);\n'
        f'  border: 1px solid var(--btn-ghost); }}\n'
    )


def judge(pg, combo: dict, last: list[str],
          last_fonts: list[dict] | None = None) -> tuple[dict, list[str]]:
    """(report, problemi) di una combinazione, misurata come una pagina vera."""
    css = combo_css(combo)
    pairs, painted, small, ok = pg.measured_pairs(css)
    if not ok or not pairs:
        return {}, ["la combinazione non è misurabile: servono ink, paper e accent in esadecimale"]
    report = pg.analyse(pairs, painted, small)
    # I caratteri della combinazione sono dichiarati nel JSON, non nel CSS del
    # provino: si passano al guard nella stessa forma in cui li legge dal ledger.
    report["typefaces"] = {r: (combo.get("fonts", {}).get(r) or {}).get("family")
                           for r in ("display", "body", "mono")
                           if (combo.get("fonts", {}).get(r) or {}).get("family")}
    problems = (pg.violations(report, last, last_fonts)
                + pg.hard_rejects(css, pg.palette_colours(css, report["colours"])))
    return report, problems


def font_decl(font: dict | None) -> str:
    if not font:
        return "inherit"
    fam = font.get("family", "").strip()
    stack = font.get("stack", "system-ui, sans-serif").strip()
    return f'"{fam}", {stack}' if fam else stack


def e(x) -> str:
    return html_lib.escape(str(x if x is not None else ""), quote=True)


def swatches(combo: dict, report: dict) -> str:
    measured = {c["hex"].lower(): c for c in report.get("colours", [])}
    out = []
    btn = combo.get("buttons") or {}
    roles = dict(combo["colours"])
    for key, name in (("fill", "pulsante"), ("label", "testo pulsante"), ("ghost", "pulsante contornato")):
        hx = btn.get(key)
        if hx and hx not in roles.values():
            roles[name] = hx
    for role, hx in roles.items():
        m = measured.get(hx.lower(), {})
        meta = " · ".join(x for x in (m.get("sector"),
                          f"croma {m['chroma']}" if m.get("chroma") is not None else None) if x)
        out.append(
            f'<li><span class="sw" style="background:{e(hx)}"></span>'
            f'<code>{e(hx)}</code><b>{e(role)}</b>'
            f'<i>{e(meta)}</i></li>')
    return "\n".join(out)


def buttons_line(combo: dict) -> str:
    """La forma del pulsante, detta a parole: è craft, e va letta senza aprire il CSS."""
    b = combo.get("buttons") or {}
    radius = str(b.get("radius", "0")).strip()
    shape = ("spigolo vivo" if radius in ("0", "0px", "")
             else "pillola" if radius in ("999px", "9999px", "50em", "100vmax")
             else f"raggio {radius}")
    given = (b.get("shape") or "pieno + fantasma").strip()
    # "pillola piena · pillola" è una ripetizione: il nome umano e il fatto
    # tecnico dicono la stessa cosa, e si tiene il nome.
    bits = [given] + ([] if shape.split()[0].lower() in given.lower() else [shape])
    if str(b.get("case", "")).lower() in ("upper", "maiuscoletto"):
        bits.append("maiuscoletto")
    if b.get("pad"):
        bits.append(f"respiro {b['pad']}")
    return " · ".join(bits)


def specimen(combo: dict, report: dict, applied: bool) -> str:
    cid, f = combo["id"], combo.get("fonts", {})
    disp, body = font_decl(f.get("display")), font_decl(f.get("body"))
    ty = combo.get("type", {})
    badge = '<span class="badge">in uso</span>' if applied else ""
    tr = " · ".join(x for x in (f"scala {ty['scale']}" if ty.get("scale") else None,
                                ty.get("tracking")) if x)
    return f"""
<section class="combo" data-combo="{e(cid)}" id="combo-{e(cid)}">
  <header class="combo__head">
    <h2><span class="id">{e(cid)}</span> {e(combo.get('name', ''))} {badge}</h2>
    <p class="why">{e(combo.get('why', ''))}</p>
  </header>
  <div class="spec spec__page">
    <div class="spec__band">
      <p class="spec__eyebrow" style="font-family:{e(body)}">{e(combo.get('eyebrow', 'anteprima'))}</p>
      <p class="spec__display" style="font-family:{e(disp)}">Aa — {e(combo.get('name', ''))}</p>
    </div>
    <div class="spec__body">
      <p style="font-family:{e(body)}">Il quadro di questa combinazione applicato a un
      paragrafo vero, perché una palette si giudica su un testo che si legge e non
      su tre quadratini in fila. Qui sotto l'accento, dove finisce davvero: su
      un'azione, non su una fascia.</p>
      <span class="spec__btn" style="font-family:{e(body)}">Prenota una visita</span>
      <span class="spec__btn spec__btn--ghost" style="font-family:{e(body)}">Scrivici</span>
    </div>
  </div>
  <ul class="tokens">{swatches(combo, report)}</ul>
  <dl class="meta">
    <dt>pulsanti</dt><dd>{e(buttons_line(combo))}</dd>
    <dt>caratteri</dt><dd><span data-font="{e(f.get('display',{}).get('family',''))}">{e(f.get('display',{}).get('family','—'))}</span>
      · <span data-font="{e(f.get('body',{}).get('family',''))}">{e(f.get('body',{}).get('family','—'))}</span></dd>
    <dt>tipografia</dt><dd>{e(tr or '—')}</dd>
    <dt>settore</dt><dd>{e(report.get('dominant_sector','—'))} · scuro {e(report.get('ink_family','—'))}</dd>
  </dl>
</section>"""


PAGE = """<!DOCTYPE html>
<html lang="it" data-generated-by="palette_page.py">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Colori e caratteri — {project}</title>
{links}
<style>
:root {{
  --paper: #f3f0ea; --ink: #171613; --ink-2: #4a463f; --rule: #c9c2b4; --accent: #8a3f1d;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--paper); color: var(--ink);
  font-family: var(--sans); line-height: 1.55; }}
.wrap {{ max-width: 74rem; margin: 0 auto; padding: clamp(1.5rem, 4vw, 3.5rem); }}
.kicker {{ font-family: var(--mono); font-size: .7rem; letter-spacing: .16em;
  text-transform: uppercase; color: var(--ink-2); margin: 0 0 .6rem; }}
h1 {{ font-size: clamp(1.7rem, 4vw, 2.6rem); line-height: 1.05; letter-spacing: -.03em; margin: 0 0 .5rem; }}
.lede {{ max-width: 62ch; color: var(--ink-2); margin: 0 0 .5rem; }}
.prov {{ font-family: var(--mono); font-size: .72rem; color: var(--ink-2);
  border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule);
  padding: .7rem 0; margin: 1.5rem 0 2.5rem; display: flex; flex-wrap: wrap; gap: .4rem 1.4rem; }}
.grid {{ display: grid; gap: 2.5rem; grid-template-columns: repeat(auto-fit, minmax(21rem, 1fr)); }}
.combo {{ border: 1px solid var(--rule); padding: 1.1rem; display: flex; flex-direction: column; gap: .9rem; }}
.combo__head h2 {{ font-size: 1.05rem; margin: 0 0 .3rem; display: flex; align-items: baseline; gap: .5rem; flex-wrap: wrap; }}
.id {{ font-family: var(--mono); border: 1px solid var(--rule); padding: 0 .4em; font-size: .8em; }}
.badge {{ font-family: var(--mono); font-size: .62rem; letter-spacing: .12em; text-transform: uppercase;
  background: var(--ink); color: var(--paper); padding: .15em .5em; }}
.why {{ margin: 0; font-size: .86rem; color: var(--ink-2); }}
.spec {{ border: 1px solid var(--rule); }}
.spec__band {{ padding: 2.2rem 1.2rem; }}
.spec__eyebrow {{ margin: 0 0 .5rem; font-size: .7rem; letter-spacing: .16em; text-transform: uppercase; opacity: .8; }}
.spec__display {{ margin: 0; font-size: clamp(1.8rem, 5vw, 2.6rem); line-height: 1; letter-spacing: -.03em; }}
.spec__body {{ padding: 1.2rem; }}
.spec__body p {{ margin: 0 0 1rem; font-size: .92rem; }}
.spec__btn {{ display: inline-block; padding: .6em 1.1em; font-size: .82rem;
  margin: 0 .5rem .4rem 0; }}
.tokens {{ list-style: none; margin: 0; padding: 0; display: grid; gap: .35rem; }}
.tokens li {{ display: flex; align-items: center; gap: .5rem; font-size: .74rem; font-family: var(--mono); }}
.tokens b {{ font-weight: 400; color: var(--ink-2); }}
.tokens i {{ margin-left: auto; font-style: normal; color: var(--ink-2); font-size: .68rem; }}
.sw {{ width: 1.15rem; height: 1.15rem; border: 1px solid var(--rule); flex: none; }}
.meta {{ display: grid; grid-template-columns: auto 1fr; gap: .2rem .8rem; margin: 0; font-size: .76rem; }}
.meta dt {{ font-family: var(--mono); font-size: .64rem; letter-spacing: .1em;
  text-transform: uppercase; color: var(--accent); }}
.meta dd {{ margin: 0; }}
.how {{ margin: 2.5rem 0 0; padding: 1rem 1.1rem; border: 1px dashed var(--rule); max-width: 62ch; font-size: .88rem; }}
#fontwarn {{ display: none; background: #7a1f12; color: #fff; padding: .8rem 1.1rem;
  font-size: .82rem; margin: 0 0 1.5rem; }}
#fontwarn.on {{ display: block; }}
@media (max-width: 34rem) {{ .prov {{ gap: .3rem .9rem; }} }}
</style>
</head>
<body>
<div class="wrap">
<p class="kicker">colori e caratteri</p>
<h1>{project}</h1>
<p class="lede">Le combinazioni che reggevano questo lavoro. Quella marcata
<b>in uso</b> è applicata alla pagina consegnata; le altre sono già legali —
sono passate dallo stesso controllo — e si possono chiedere.</p>
<p class="prov">{prov}</p>
<div id="fontwarn"></div>
<div class="grid">{combos}
</div>
<p class="how"><b>Per cambiare:</b> dimmi quale — «metti la B», o anche solo il
carattere o il colore che preferisci di un'altra. Aggiorno il <code>DESIGN.md</code>,
rifaccio la pagina con quella combinazione e rigenero questa. Non serve altro:
questa pagina non aspetta una risposta, è solo il modo di vedere cosa c'era.</p>
</div>
<script>
// Un provino reso con un carattere di ripiego è peggio di nessun provino:
// si sceglie una coppia che non si è mai vista. Se un font dichiarato non è
// disponibile, lo si dice forte invece di lasciarlo passare.
(function () {{
  var names = [], seen = {{}};
  document.querySelectorAll("[data-font]").forEach(function (n) {{
    var f = (n.getAttribute("data-font") || "").trim();
    if (f && !seen[f]) {{ seen[f] = 1; names.push(f); }}
  }});
  function check() {{
    var missing = names.filter(function (f) {{
      try {{ return !document.fonts.check('16px "' + f + '"'); }} catch (e) {{ return false; }}
    }});
    if (!missing.length) return;
    var box = document.getElementById("fontwarn");
    box.className = "on";
    box.textContent = "Attenzione: " + missing.join(", ") +
      (missing.length > 1 ? " non si sono caricati" : " non si è caricato") +
      ". Quello che vedi è un carattere di ripiego, non la combinazione: " +
      "non sceglierla da qui finché non si carica.";
  }}
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(check);
  else window.addEventListener("load", check);
}})();
</script>
</body>
</html>
"""


def build(data: dict, reports: dict[str, dict]) -> str:
    b = data.get("batch") or {}
    bits = [("progetto", data.get("project")), ("superficie", data.get("surface")),
            ("attività", data.get("activity")), ("register", data.get("register")),
            ("luogo", data.get("locale")), ("seed", data.get("seed")),
            ("batch", f"{b.get('count', '?')} riferimenti · {b.get('source', '—')}")]
    prov = " ".join(f"<span><b>{e(k)}</b> {e(v)}</span>" for k, v in bits if v)

    urls, links = [], []
    for c in data["combos"]:
        for f in (c.get("fonts") or {}).values():
            u = (f or {}).get("url")
            if u and u not in urls:
                urls.append(u)
    links = "\n".join(f'<link rel="stylesheet" href="{e(u)}">' for u in urls)

    applied = data.get("applied")
    blocks = "\n".join(specimen(c, reports[c["id"]], c["id"] == applied) for c in data["combos"])
    css = "\n".join(combo_css(c) for c in data["combos"])
    page = PAGE.format(project=e(data.get("project", "")), prov=prov,
                       combos=blocks, links=links)
    return page.replace("</style>", css + "</style>")


def main() -> int:
    ap = argparse.ArgumentParser(description="Pagina delle combinazioni colore/carattere")
    ap.add_argument("combos", help="JSON con le combinazioni (- per stdin)")
    ap.add_argument("--out", required=True, help="apps/<slug>/palette.html")
    ap.add_argument("--ledger", help="registro dei settori di tinta "
                    "(default: quello condiviso fra progetti)")
    ap.add_argument("--no-ledger", action="store_true", help="ignora il registro")
    ap.add_argument("--last", default="", help="settori recenti, il più recente per primo")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.combos == "-" else Path(args.combos).read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"JSON illeggibile: {exc}", file=sys.stderr)
        return 2
    combos = data.get("combos") or []
    if len(combos) < 2:
        print("servono almeno due combinazioni: una sola non è una combinazione, è la pagina",
              file=sys.stderr)
        return 2

    applied = data.get("applied")
    ids = [c.get("id") for c in combos]
    if applied and applied not in ids:
        print(f"`applied: {applied}` non e fra le combinazioni ({', '.join(map(str, ids))}): "
              "la pagina non marcherebbe niente come «in uso», e l'owner vedrebbe "
              "delle alternative senza sapere quale gli hai consegnato — cioe un menu.",
              file=sys.stderr)
        return 2
    if len(set(ids)) != len(ids):
        print(f"id ripetuti fra le combinazioni: {', '.join(map(str, ids))}", file=sys.stderr)
        return 2

    pg = _repeat_guard()

    # Le combinazioni devono differire **nell'accento**, o la pagina mostra
    # quattro volte la stessa proposta con quattro nomi. Misurato il 2026-07-27:
    # sulle cinque pagine consegnate l'accento era `rosso` su tre, e i quattro
    # esadecimali caldi stavano nella stessa zona terracotta. Il colore della CTA
    # e' l'unica tinta che l'occhio guarda per primo: se non varia lui, non varia
    # niente. Trenta zone in `accent_pool.py`.
    fam = {}
    for c in combos:
        acc = (c.get("colours") or {}).get("accent")
        if not acc:
            continue
        try:
            h, s_, l = pg.to_hsl(acc)
        except Exception:
            continue
        fam.setdefault(pg.family_of(pg.sector_of(h, s_, l)), []).append(c.get("id"))
    if len(fam) < min(2, len(combos)):
        dett = " · ".join(f"{k}: {', '.join(map(str, v))}" for k, v in fam.items())
        print("le combinazioni hanno l'accento nella stessa famiglia — "
              f"{dett or 'nessun accento cromatico'}. Non sono alternative: e' una "
              "proposta sola ripetuta, e la CTA e' il colore che l'owner guarda "
              "per primo. Prendi zone diverse: "
              "`uv run scripts/accent_pool.py --suggest 4 --seed <seed> --last <famiglie recenti>`.",
              file=sys.stderr)
        return 2
    last = [s for s in args.last.split(",") if s.strip()]
    last_fonts: list[dict] = []
    if not args.no_ledger:
        ledger = Path(args.ledger) if args.ledger else pg.default_ledger()
        entries = pg.ledger_load(ledger)
        last_fonts = pg.ledger_fonts(entries)
        if not last:
            last = pg.ledger_sectors(entries)

    reports, bad = {}, []
    for c in combos:
        missing = [r for r in ROLES if not (c.get("colours") or {}).get(r)]
        if missing or not c.get("id"):
            bad.append(f"{c.get('id', '?')}: manca {', '.join(missing) or 'id'}")
            reports[c.get("id", "?")] = {}
            continue
        report, problems = judge(pg, c, last, last_fonts)
        reports[c["id"]] = report
        bad += [f"{c['id']} — {p}" for p in problems]

    if bad:
        print("Queste combinazioni non si possono mostrare, perché non si potrebbero "
              "scegliere:\n", file=sys.stderr)
        for line in bad:
            print(f"  - {line}", file=sys.stderr)
        print("\nCorreggile e rilancia: una pagina che offre ciò che il guard rifiuta "
              "è un'offerta che si ritira dopo averla fatta.", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(data, reports), encoding="utf-8")
    print(f"{out} — {len(combos)} combinazioni, tutte legali"
          + (f", in uso: {applied}" if applied else ""))
    if not applied:
        print("nessuna marcata `applied`: la pagina non dice quale è stata consegnata")
    return 0


if __name__ == "__main__":
    sys.exit(main())
