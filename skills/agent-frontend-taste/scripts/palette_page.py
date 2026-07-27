#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Il selettore: trenta colori, trenta caratteri, trenta forme. Si clicca.

Perché è fatta così. La versione precedente mostrava da due a quattro
**combinazioni confezionate**, ognuna con nome, motivo, provino e note: l'owner
non vuole leggere, vuole vedere le possibilità e scegliere. E vuole sceglierle
su assi **indipendenti** — questo colore con quel carattere e quell'altra forma.

Trenta per asse, non tre: sotto quella soglia si torna a proporre sempre le
stesse cose. I trenta non si passano a mano, vengono dai cataloghi —
`accent_pool.py --as-colours`, `font_pool.py`, `shape_pool.py` — che esistono
perché la misura diceva il contrario del gusto: l'accento era `rosso` su 3
pagine su 5 (quattro CTA entro venti gradi di tinta), `DM Mono` il mono di 5 su
5, la pillola il raggio di 5 su 5.

**Niente prosa.** Ogni voce è un campione e un id. Nessun «perché», nessuna
nota, nessuna riga di aiuto: se serve una spiegazione per capire un colore, il
problema è il colore.

**La pagina non applica niente.** Si apre col doppio clic, non ha server, e
produce una riga da rimandare a Vesper — `colore=… · font=… · forma=…`.

Usage:
    uv run scripts/palette_page.py --out apps/<slug>/palette.html --seed 2026072712
    uv run scripts/palette_page.py meta.json --out … --no-ledger

Exit: 0 scritta · 1 un colore non è legale · 2 input illeggibile o accenti tutti
      imparentati.
"""

from __future__ import annotations

import argparse
import html as html_lib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _mod(nome: str):
    spec = importlib.util.spec_from_file_location(nome, HERE / f"{nome}.py")
    if not spec or not spec.loader:
        raise SystemExit(f"{nome}.py non trovato accanto a palette_page.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(nome, m)
    spec.loader.exec_module(m)
    return m


def e(x) -> str:
    return html_lib.escape(str(x if x is not None else ""), quote=True)


def dai_cataloghi() -> dict:
    """I tre elenchi da trenta, senza passare per la riga di comando."""
    ap, fp, sp = _mod("accent_pool"), _mod("font_pool"), _mod("shape_pool")
    return {"colours": [ap.come_colore(z) for z in ap.ZONE],
            "fonts": [fp.voce(t) for t in fp.COPPIE],
            "shapes": [sp.voce(t) for t in sp.FORME]}


# --- controlli ---------------------------------------------------------------

def colori_illegali(pg, colours: list[dict], last: list[str],
                    last_fonts: list[dict]) -> list[str]:
    """Nessun colore che il guard poi rifiuterebbe: offrirlo e ritirarlo è peggio."""
    guai = []
    for c in colours:
        css = (f'[data-c="{c["id"]}"] {{ --ink: {c["ink"]}; --paper: {c["paper"]};'
               f' --accent: {c["accent"]}; }}\n'
               f'[data-c="{c["id"]}"] .page {{ background: var(--paper); color: var(--ink); }}\n'
               f'[data-c="{c["id"]}"] .band {{ background: var(--ink); color: var(--paper); }}\n'
               f'[data-c="{c["id"]}"] .btn {{ background: var(--accent); color: var(--paper); }}\n')
        pairs, painted, small, ok = pg.measured_pairs(css)
        if not ok or not pairs:
            guai.append(f"{c['id']}: non misurabile")
            continue
        rep = pg.analyse(pairs, painted, small)
        for p in pg.hard_rejects(css, pg.palette_colours(css, rep["colours"])):
            guai.append(f"{c['id']} — {p}")
        for p in pg.violations(rep, last, last_fonts):
            if "predominante" in p or "ripetut" in p:
                continue          # la storia riguarda la consegna, non il catalogo
            guai.append(f"{c['id']} — {p}")
    return guai


def famiglie(pg, colours: list[dict]) -> dict:
    out: dict[str, list[str]] = {}
    for c in colours:
        try:
            h, s_, l = pg.to_hsl(c["accent"])
        except Exception:
            continue
        out.setdefault(pg.family_of(pg.sector_of(h, s_, l)), []).append(c["id"])
    return out


# --- pagina ------------------------------------------------------------------

CSS = """
:root{--paper:#f3f0ea;--ink:#171613;--ink2:#4a463f;--rule:#c9c2b4;
--mono:ui-monospace,Menlo,Consolas,monospace;--sans:system-ui,-apple-system,sans-serif}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.5}
.wrap{max-width:82rem;margin:0 auto;padding:clamp(1rem,3vw,2.5rem)}
h1{font-size:1.15rem;margin:0 0 .2rem;letter-spacing:-.01em}
.prov{font-family:var(--mono);font-size:.68rem;color:var(--ink2);
border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);
padding:.55rem 0;margin:.8rem 0 1.4rem;display:flex;flex-wrap:wrap;gap:.3rem 1.2rem}
h2{font-family:var(--mono);font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;
color:var(--ink2);margin:1.8rem 0 .7rem;font-weight:400}
.grid{display:grid;gap:.5rem;grid-template-columns:repeat(auto-fill,minmax(8.5rem,1fr))}
.opt{border:1px solid var(--rule);background:transparent;padding:0;cursor:pointer;
font:inherit;text-align:left;overflow:hidden;display:block;width:100%}
.opt:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.opt[aria-pressed="true"]{outline:2px solid var(--ink);outline-offset:-1px}
.opt .id{display:block;font-family:var(--mono);font-size:.6rem;color:var(--ink2);
padding:.3rem .4rem;border-top:1px solid var(--rule);white-space:nowrap;overflow:hidden;
text-overflow:ellipsis}
.sw{display:grid;grid-template-columns:1fr 1fr 1fr;height:2.6rem}
.tp{display:block;padding:.5rem .45rem .35rem;min-height:2.6rem}
.tp b{display:block;font-size:1.15rem;line-height:1.1;font-weight:500;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tp i{font-style:normal;font-size:.6rem;color:var(--ink2);display:block;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sh{display:grid;place-items:center;height:2.6rem}
.sh span{font-size:.6rem;border:1px solid currentColor;line-height:1;color:var(--ink)}
#prev{border:1px solid var(--rule)}
#prevBand{padding:2rem 1.2rem}
#prevBand p{margin:0}
#prevEye{font-size:.62rem;letter-spacing:.14em;text-transform:uppercase;opacity:.8;margin-bottom:.5rem}
#prevDisp{font-size:clamp(1.7rem,4.5vw,2.6rem);line-height:1;letter-spacing:-.03em}
#prevBody{padding:1.1rem 1.2rem}
#prevBody p{margin:0 0 .9rem;font-size:.92rem;max-width:60ch}
.pb{display:inline-block;margin:0 .5rem .4rem 0;border:1px solid transparent}
#out{margin:1rem 0 0;display:flex;gap:.6rem;align-items:center;flex-wrap:wrap}
#outLine{font-family:var(--mono);font-size:.76rem;border:1px solid var(--rule);
padding:.5rem .7rem;flex:1 1 22rem;min-width:0;overflow-x:auto;white-space:nowrap}
#copy{font-family:var(--mono);font-size:.68rem;padding:.5rem .9rem;border:1px solid var(--ink);
background:var(--ink);color:var(--paper);cursor:pointer}
#fontwarn{display:none;background:#7a1f12;color:#fff;padding:.7rem 1rem;font-size:.8rem;margin:0 0 1rem}
#fontwarn.on{display:block}
@media(max-width:34rem){.grid{grid-template-columns:repeat(auto-fill,minmax(7rem,1fr))}}
"""

JS = """
(function(){
 var C=window.__POOL_C,F=window.__POOL_F,S=window.__POOL_S;
 var sel={c:C[0],f:F[0],s:S[0]};
 function byId(a,i){for(var k=0;k<a.length;k++){if(a[k].id===i)return a[k]}return a[0]}
 function paint(){
  var c=sel.c,f=sel.f,s=sel.s;
  var p=document.getElementById('prev');
  p.style.background=c.paper;p.style.color=c.ink;
  var b=document.getElementById('prevBand');b.style.background=c.ink;b.style.color=c.paper;
  document.getElementById('prevDisp').style.fontFamily='"'+f.display.family+'",'+f.display.stack;
  document.getElementById('prevEye').style.fontFamily='"'+f.mono.family+'",'+f.mono.stack;
  var bodyF='"'+f.body.family+'",'+f.body.stack;
  document.getElementById('prevBody').style.fontFamily=bodyF;
  var up=(s.case==='maiuscoletto');
  [['pbFill',true],['pbGhost',false]].forEach(function(x){
   var el=document.getElementById(x[0]);
   el.style.borderRadius=s.radius;el.style.padding=s.pad;
   el.style.textTransform=up?'uppercase':'none';el.style.letterSpacing=up?'.08em':'0';
   el.style.fontFamily=bodyF;el.style.fontSize='.82rem';
   if(s.shape==='sottolineato'){el.style.background='transparent';el.style.color=c.accent;
    el.style.borderColor='transparent';el.style.textDecoration='underline';
    el.style.textUnderlineOffset='4px';}
   else if(x[1]){el.style.background=c.accent;el.style.color=c.paper;
    el.style.borderColor=c.accent;el.style.textDecoration='none';}
   else{el.style.background='transparent';el.style.color=c.ink;el.style.borderColor=c.ink;
    el.style.textDecoration='none';}
  });
  document.getElementById('outLine').textContent=
   'colore='+c.id+' \\u00b7 font='+f.id+' \\u00b7 forma='+s.id;
 }
 Array.prototype.forEach.call(document.querySelectorAll('.opt'),function(b){
  b.addEventListener('click',function(){
   var g=b.getAttribute('data-g'),i=b.getAttribute('data-i');
   Array.prototype.forEach.call(document.querySelectorAll('.opt[data-g="'+g+'"]'),function(o){
    o.setAttribute('aria-pressed',o===b?'true':'false');});
   sel[g]=byId(g==='c'?C:(g==='f'?F:S),i);paint();
  });
 });
 document.getElementById('copy').addEventListener('click',function(){
  var t=document.getElementById('outLine').textContent;
  if(navigator.clipboard){navigator.clipboard.writeText(t);}
  else{var r=document.createRange();r.selectNode(document.getElementById('outLine'));
   window.getSelection().removeAllRanges();window.getSelection().addRange(r);
   document.execCommand('copy');}
  var b=document.getElementById('copy'),o=b.textContent;b.textContent='copiato';
  setTimeout(function(){b.textContent=o;},1200);
 });
 paint();
 var nomi=[],visti={};
 F.forEach(function(f){['display','body','mono'].forEach(function(r){
  var n=f[r].family;if(!visti[n]){visti[n]=1;nomi.push(n);}});});
 function check(){
  var m=nomi.filter(function(n){
   try{return !document.fonts.check('16px "'+n+'"');}catch(e){return false;}});
  if(m.length<nomi.length*0.5)return;
  var w=document.getElementById('fontwarn');w.className='on';
  w.textContent='Non si sono caricati '+m.length+' caratteri su '+nomi.length+
   ': quello che vedi e un ripiego, non la scelta.';
 }
 if(document.fonts&&document.fonts.ready){document.fonts.ready.then(check);}
 else{window.addEventListener('load',check);}
})();
"""


def griglia_colori(cs: list[dict]) -> str:
    return "\n".join(
        f'<button class="opt" data-g="c" data-i="{e(c["id"])}" '
        f'aria-pressed="{"true" if i == 0 else "false"}">'
        f'<span class="sw"><span style="background:{e(c["ink"])}"></span>'
        f'<span style="background:{e(c["paper"])}"></span>'
        f'<span style="background:{e(c["accent"])}"></span></span>'
        f'<span class="id">{e(c["id"])}</span></button>'
        for i, c in enumerate(cs))


def griglia_font(fs: list[dict]) -> str:
    out = []
    for i, f in enumerate(fs):
        d, b = f["display"], f["body"]
        out.append(
            f'<button class="opt" data-g="f" data-i="{e(f["id"])}" '
            f'aria-pressed="{"true" if i == 0 else "false"}">'
            f'<span class="tp"><b style="font-family:&quot;{e(d["family"])}&quot;,{e(d["stack"])}">Aa</b>'
            f'<i style="font-family:&quot;{e(b["family"])}&quot;,{e(b["stack"])}">{e(b["family"])}</i></span>'
            f'<span class="id">{e(f["id"])}</span></button>')
    return "\n".join(out)


def griglia_forme(ss: list[dict]) -> str:
    out = []
    for i, s in enumerate(ss):
        up = "text-transform:uppercase;letter-spacing:.08em;" if s["case"] == "maiuscoletto" else ""
        stile = f'border-radius:{e(s["radius"])};padding:{e(s["pad"])};{up}'
        if s["shape"] == "sottolineato":
            stile += "border-color:transparent;text-decoration:underline;text-underline-offset:3px;"
        out.append(
            f'<button class="opt" data-g="s" data-i="{e(s["id"])}" '
            f'aria-pressed="{"true" if i == 0 else "false"}">'
            f'<span class="sh"><span style="{stile}">Aa</span></span>'
            f'<span class="id">{e(s["id"])}</span></button>')
    return "\n".join(out)


PAGINA = """<!DOCTYPE html>
<html lang="it" data-generated-by="palette_page.py">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITOLO__</title>
__LINKS__
<style>__CSS__</style>
</head>
<body>
<div class="wrap">
<h1>__TITOLO__</h1>
<p class="prov">__PROV__</p>
<div id="fontwarn"></div>

<div id="prev">
  <div id="prevBand"><p id="prevEye">Aa</p><p id="prevDisp">__TITOLO__</p></div>
  <div id="prevBody">
    <p>Il paragrafo di prova, col colore, il carattere e la forma scelti.</p>
    <span class="pb" id="pbFill">Chiedi disponibilità</span>
    <span class="pb" id="pbGhost">Scrivici</span>
  </div>
</div>

<div id="out">
  <div id="outLine">colore=__C0__ · font=__F0__ · forma=__S0__</div>
  <button id="copy">copia</button>
</div>

<h2>Colori</h2>
<div class="grid">__GC__</div>
<h2>Caratteri</h2>
<div class="grid">__GF__</div>
<h2>Forme</h2>
<div class="grid">__GS__</div>
</div>
<script>
window.__POOL_C=__JC__;window.__POOL_F=__JF__;window.__POOL_S=__JS__;
__JSCODE__
</script>
</body>
</html>
"""


def costruisci(dati: dict, pools: dict) -> str:
    b = dati.get("batch") or {}
    bits = [("progetto", dati.get("project")), ("superficie", dati.get("surface")),
            ("attività", dati.get("activity")), ("register", dati.get("register")),
            ("luogo", dati.get("locale")), ("seed", dati.get("seed")),
            ("batch", f"{b.get('count', '?')} · {b.get('source', '—')}" if b else None)]
    prov = " ".join(f"<span><b>{e(k)}</b> {e(v)}</span>" for k, v in bits if v)

    urls = []
    for f in pools["fonts"]:
        for r in ("display", "body", "mono"):
            u = (f.get(r) or {}).get("url")
            if u and u not in urls:
                urls.append(u)
    links = "\n".join(f'<link rel="stylesheet" href="{e(u)}">' for u in urls)

    t = PAGINA
    for k, v in (("__TITOLO__", e(dati.get("project", "Colori, caratteri, forme"))),
                 ("__LINKS__", links), ("__CSS__", CSS), ("__PROV__", prov),
                 ("__GC__", griglia_colori(pools["colours"])),
                 ("__GF__", griglia_font(pools["fonts"])),
                 ("__GS__", griglia_forme(pools["shapes"])),
                 ("__C0__", e(pools["colours"][0]["id"])),
                 ("__F0__", e(pools["fonts"][0]["id"])),
                 ("__S0__", e(pools["shapes"][0]["id"])),
                 ("__JC__", json.dumps(pools["colours"], ensure_ascii=False)),
                 ("__JF__", json.dumps(pools["fonts"], ensure_ascii=False)),
                 ("__JS__", json.dumps(pools["shapes"], ensure_ascii=False)),
                 ("__JSCODE__", JS)):
        t = t.replace(k, v)
    return t


def main() -> int:
    ap = argparse.ArgumentParser(description="Selettore: colori, caratteri, forme")
    ap.add_argument("dati", nargs="?", help="JSON coi metadati (- per stdin); "
                                            "gli elenchi vengono dai cataloghi")
    ap.add_argument("--out", required=True, help="apps/<slug>/palette.html")
    ap.add_argument("--seed", default="", help="seed YYYYMMDDHH")
    ap.add_argument("--ledger", help="registro dei settori (default: quello condiviso)")
    ap.add_argument("--no-ledger", action="store_true", help="ignora il registro")
    args = ap.parse_args()

    dati: dict = {}
    if args.dati:
        raw = sys.stdin.read() if args.dati == "-" else Path(args.dati).read_text(encoding="utf-8")
        try:
            dati = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(f"JSON illeggibile: {exc}", file=sys.stderr)
            return 2
    if args.seed:
        dati["seed"] = args.seed

    pools = dai_cataloghi()
    for k in ("colours", "fonts", "shapes"):
        if dati.get(k):
            pools[k] = dati[k]
        if not pools[k]:
            print(f"elenco `{k}` vuoto: quell'asse non comparirà", file=sys.stderr)

    pg = _mod("repeat_guard")
    last: list[str] = []
    last_fonts: list[dict] = []
    if not args.no_ledger:
        led = Path(args.ledger) if args.ledger else pg.default_ledger()
        voci = pg.ledger_load(led)
        last, last_fonts = pg.ledger_sectors(voci), pg.ledger_fonts(voci)

    fam = famiglie(pg, pools["colours"])
    if len(fam) < 2:
        print("i colori proposti hanno l'accento tutto nella stessa famiglia "
              f"({', '.join(fam) or 'nessuno cromatico'}): non sono alternative. "
              "`accent_pool.py --as-colours` ne dà trenta su sette famiglie.",
              file=sys.stderr)
        return 2

    guai = colori_illegali(pg, pools["colours"], last, last_fonts)
    if guai:
        print("colori che il guard rifiuterebbe — non si mostrano:", file=sys.stderr)
        for g in guai[:8]:
            print(f"  - {g}", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(costruisci(dati, pools), encoding="utf-8")
    print(f"{out} — {len(pools['colours'])} colori · {len(pools['fonts'])} caratteri "
          f"· {len(pools['shapes'])} forme · {len(fam)} famiglie di accento")
    return 0


if __name__ == "__main__":
    sys.exit(main())
