#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Il lock: le decisioni di craft materializzate **prima** che la pagina esista.

Deciso in consiglio il 2026-07-27, su una diagnosi che nessuno aveva formulato
così: il problema non era l'inventario, era **l'esecuzione**, e il buco stava
esattamente dove il lavoro accade.

    cataloghi (decidono prima)  →  [ qui si scrive la pagina ]  →  guard (dopo)
                                          ^ niente

I cataloghi si potevano ignorare senza che nessuno se ne accorgesse, perché
nessuno confrontava il consegnato con ciò che il catalogo aveva detto. E i guard
sono **statistici**: guardano lo storico, che era quasi vuoto (`accent_family` su
2 voci su 11) e arriva comunque tardi — quando scattano, la pagina è già scritta
e correggere costa un rifacimento. Un controllo che costa un rifacimento è un
controllo che si impara a saltare.

Il lock chiude il buco. Le scelte si sorteggiano dal seed **col progetto dentro**,
si scrivono su disco, e `close_check` confronta la pagina **con il lock** invece
che con la storia: «il lock diceva `salvia`, la pagina è `#db7055`» non lascia
margine di interpretazione e non ha bisogno di nessun campione.

Due condizioni poste al tavolo, e rispettate qui:

  · **Senza lock non si consegna** (Murat): se fosse opzionale, in tre giorni
    nessuno lo scriverebbe più.
  · **Il lock contiene *cosa*, non *perché*** (Vesper): le motivazioni stanno nel
    DESIGN, o torna a essere il verbale che il registro del consiglio ha già
    sostituito.

Il craft resta di Vesper: il lock lo produce il suo seed, non un voto. Smette
solo di essere una cosa che si *dice* di aver fatto.

Usage:
    uv run scripts/craft_lock.py --project hotel-mare --seed 2026072715 \\
        --out apps/hotel-mare/craft-lock.json
    uv run scripts/craft_lock.py --project … --seed … --out … --pick colore=salvia
    uv run scripts/craft_lock.py --show apps/hotel-mare/craft-lock.json

Exit: 0 scritto · 1 una scelta chiesta non esiste · 2 argomenti mancanti.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERA = HERE.parent.parent / "agent-web-animations" / "scripts"


def _mod(nome: str, base: Path = HERE):
    spec = importlib.util.spec_from_file_location(nome, base / f"{nome}.py")
    if not spec or not spec.loader:
        raise SystemExit(f"{nome}.py non trovato in {base}")
    m = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(nome, m)
    spec.loader.exec_module(m)
    return m


def semina(seed: str, slug: str) -> str:
    """Ora **e** progetto. Con la sola ora due landing fatte nello stesso momento
    ricevevano accento, carattere, forma, hero e motion identici — misurato.

    Il confronto e' sul **suffisso esatto**, non `slug in s`: con la sottostringa
    `--project hotel --seed 2026072715-hotel-mare` vedeva «hotel» dentro il seed,
    non aggiungeva niente, e i progetti `hotel` e `hotel-mare` ricevevano lo
    stesso identico seed — cioe' la collisione che questo file esiste per
    chiudere, rientrata dalla finestra. Misurato il 2026-07-27.
    """
    s = (seed or "").strip()
    if not s:
        raise SystemExit("manca --seed (YYYYMMDDHH)")
    slug = (slug or "").strip()
    if not slug:
        raise SystemExit("manca --project: il seed senza slug e' l'ora, e due "
                         "lavori nella stessa ora escono identici")
    return s if s == slug or s.endswith(f"-{slug}") else f"{s}-{slug}"


def costruisci(slug: str, seed: str, escluse: dict, surface: str = "marketing") -> dict:
    """`surface` non e' un dettaglio: la tenda obbligatoria e l'hero sono regole
    da **landing**. Imporle a un back office significa bocciare una dashboard
    perche' non ha una tenda — un falso positivo generato dal controllo stesso,
    che e' il modo piu' rapido di insegnare a ignorarlo. Misurato il 2026-07-27:
    `backoffice` riceveva `curtain-left` e un hero `magazine-cover-xl`.
    """
    ap, fp, sp = _mod("accent_pool"), _mod("font_pool"), _mod("shape_pool")
    s = semina(seed, slug)

    colore = ap.come_colore(ap.scegli(s, escluse.get("colore", [])))
    font = fp.suggerisci(1, s, escluse.get("font", []))[0]
    forma = sp.suggerisci(1, s, escluse.get("forma", []))[0]

    lock = {
        "project": slug,
        "seed": s,
        "surface": surface,
        "colore": {"id": colore["id"], "famiglia": colore["famiglia"],
                   "accent": colore["accent"], "paper": colore["paper"],
                   "ink": colore["ink"]},
        "font": {"id": font["id"], "display": font["display"]["family"],
                 "body": font["body"]["family"], "mono": font["mono"]["family"]},
        "forma": {"id": forma["id"], "radius": forma["radius"],
                  "radius_family": forma["radius_family"], "shape": forma["shape"],
                  "case": forma["case"]},
    }

    # hero ed effetti: se i cataloghi ci sono si sorteggiano, altrimenti si
    # dichiara l'assenza invece di inventare un valore.
    try:
        if surface != "marketing":
            raise StopIteration  # una dashboard non ha un archetipo hero
        hg = _mod("hero_gallery")
        arche = hg.load()["archetypes"] if hasattr(hg, "load") else []
        if arche:
            h = hg.suggest(arche, 1, s, escluse.get("hero", []))[0]
            lock["hero"] = {"id": h.get("id") or h.get("n"), "media": h.get("media"),
                            "placement": h.get("placement"), "panel": h.get("panel")}
    except StopIteration:
        pass
    except Exception as exc:
        lock["hero"] = {"non_sorteggiato": str(exc)[:80]}

    try:
        fx = _mod("effects_gallery", VERA)
        eff = fx.load()["effects"]
        scelti = fx.suggest(eff, 3, s, escluse.get("effetti", []))
        tende = [e for e in eff if e["id"].startswith("curtain")]
        if surface == "marketing" and tende and not any(
                e["id"].startswith("curtain") for e in scelti):
            # Regola dell'owner: su una **landing** almeno una tenda, sempre.
            import random
            scelti[-1] = random.Random(f"{s}|curtain").choice(tende)
        lock["effetti"] = [e["id"] for e in scelti]
    except Exception as exc:
        lock["effetti"] = {"non_sorteggiati": str(exc)[:80]}

    return lock


def applica_scelte(lock: dict, scelte: list[str]) -> dict:
    """Il clic dell'owner atterra qui: una cosa sola con due sorgenti.

    Senza questo, la riga `colore=… · font=… · forma=…` che il selettore produce
    e' un clic che muore — l'ha detto Sally, ed era l'unica sua riga.
    """
    ap, fp, sp = _mod("accent_pool"), _mod("font_pool"), _mod("shape_pool")
    visti: set[str] = set()
    for raw in scelte or []:
        asse, _, valore = raw.partition("=")
        # Minuscolo su entrambi: la riga la copia l'owner dal selettore, e un
        # `colore=Cobalto` rifiutato per la maiuscola sembra un catalogo bucato.
        asse, valore = asse.strip().lower(), valore.strip().lower()
        if not valore:
            raise SystemExit(f"scelta malformata: '{raw}'. Serve `asse=id`.")
        if asse in visti:
            # Due valori per lo stesso asse: uno dei due si perdeva in silenzio.
            raise SystemExit(f"`{asse}` scelto due volte: dimmi quale vale.")
        visti.add(asse)
        if asse == "colore":
            z = [x for x in ap.ZONE if x["id"] == valore]
            if not z:
                raise SystemExit(f"colore sconosciuto: {valore}")
            c = ap.come_colore(z[0])
            lock["colore"] = {"id": c["id"], "famiglia": c["famiglia"], "accent": c["accent"],
                              "paper": c["paper"], "ink": c["ink"], "scelto_da": "owner"}
        elif asse == "font":
            t = [x for x in fp.COPPIE if x[0] == valore]
            if not t:
                raise SystemExit(f"font sconosciuto: {valore}")
            v = fp.voce(t[0])
            lock["font"] = {"id": v["id"], "display": v["display"]["family"],
                            "body": v["body"]["family"], "mono": v["mono"]["family"],
                            "scelto_da": "owner"}
        elif asse == "forma":
            t = [x for x in sp.FORME if x[0] == valore]
            if not t:
                raise SystemExit(f"forma sconosciuta: {valore}")
            v = sp.voce(t[0])
            lock["forma"] = {**{k: v[k] for k in ("id", "radius", "radius_family",
                                                  "shape", "case")}, "scelto_da": "owner"}
        else:
            raise SystemExit(f"asse sconosciuto: {asse}. Sono colore, font, forma.")
    return lock


TINTA_TOLLERATA = 15.0  # gradi: schiarite e hover si', un altro colore no


def _distanza_tinta(a: str, b: str) -> float | None:
    """Quanti gradi separano due tinte. None se una delle due non si misura."""
    try:
        pg = _mod("repeat_guard")
        ha, hb = pg.to_hsl(a)[0], pg.to_hsl(b)[0]
    except Exception:
        return None
    d = abs(ha - hb) % 360
    return min(d, 360 - d)


def _accento_presente(atteso: str, text: str) -> bool:
    """Il valore del lock compare nella pagina, comunque sia scritto.

    Senza `text` non si puo' dire: si torna alla misura per tinta invece di
    accusare una pagina che non abbiamo letto.
    """
    if not text:
        return True
    h = (atteso or "").strip().lstrip("#").lower()
    if len(h) != 6:
        return True
    basso = text.lower()
    if f"#{h}" in basso:
        return True
    try:
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return True
    import re as _re
    return bool(_re.search(rf"rgba?\(\s*{r}\s*,\s*{g}\s*,\s*{b}\b", basso))


def scostamenti(lock: dict, report: dict, text: str = "") -> list[str]:
    """Il confronto: cosa dice il lock, cosa dice la pagina consegnata.

    Esatto, non statistico. E' la differenza fra «rosso su 3 delle ultime 5,
    cambia famiglia» e «il lock diceva salvia, la pagina e' #db7055».

    Tre cose che la prima versione lasciava passare, misurate il 2026-07-27:

      · **confrontava il genere, non la scelta**: lock `lacca` `#b7502f`, pagina
        `#db7055` — due rossi diversi, zero scostamenti. Il lock nomina UN
        colore, non una famiglia;
      · **il silenzio passava**: una pagina che non dichiarava display, accento
        e raggio non produceva scostamenti, cioe' il modo piu' semplice di
        superare il cancello era non dire niente;
      · **effetti e hero erano decorativi**: scritti nel lock e controllati da
        nessuno — la stessa classe di difetto di `--prefer`, codice inerte che
        sembra funzionare perche' l'output e' plausibile.

    Con `report` vuoto tace: la pagina non e' misurabile e lo dice gia' un
    altro controllo. Due voci per lo stesso guaio insegnano a ignorarle.
    """
    if not report:
        return []
    out = []

    acc = report.get("accent") or {}
    col = lock.get("colore") or {}
    if col.get("famiglia"):
        if not acc.get("hex"):
            out.append(f"accento: il lock dice `{col['id']}`, la pagina non ne "
                       "dichiara nessuno")
        elif acc.get("famiglia") and acc["famiglia"] != col["famiglia"]:
            out.append(f"accento: il lock dice `{col['id']}` ({col['famiglia']}), "
                       f"la pagina ha {acc['hex']} ({acc['famiglia']})")
        elif (col.get("accent")
              and acc["hex"].strip().lower() != col["accent"].strip().lower()
              and not _accento_presente(col["accent"], text)):
            # Il colore misurato non e' quello del lock **e** il valore non
            # compare nella pagina. La prima condizione da sola non basta a
            # accusare: una pagina che scrive `hsl(15 59% 45%)` porta lo stesso
            # identico colore, e il referto diceva «il lock dice #b7502f, la
            # pagina ha #b7502f» — il falso positivo nella sua forma peggiore,
            # quella che si contraddice da sola.
            # La seconda da sola non basta a assolvere: la tinta non separa
            # basta a dirlo: `zafferano` e `sabbia` distano 2°, `senape` e
            # `grano` 1.9° — sono zone diverse del catalogo che la sola misura
            # angolare non separa. Il valore esatto le separa tutte.
            d = _distanza_tinta(col["accent"], acc["hex"])
            quanto = (f" — {d:.0f}° di distanza" if d is not None and d > TINTA_TOLLERATA
                      else "")
            out.append(f"accento: il lock dice `{col['id']}` {col['accent']}, "
                       f"la pagina ha {acc['hex']}{quanto}")

    faces = report.get("typefaces") or {}
    for ruolo in ("display", "body", "mono"):
        voluto = (lock.get("font") or {}).get(ruolo)
        if not voluto:
            continue
        if not isinstance(voluto, str):
            out.append(f"{ruolo}: il lock non dice un nome di carattere ma "
                       f"{type(voluto).__name__} — lock da rifare")
            continue
        avuto = faces.get(ruolo)
        if not isinstance(avuto, str):
            avuto = ""
        if not avuto:
            # Il mono e' la terza voce: una landing puo' legittimamente non
            # usarlo. Display e testo no — se non ci sono, non c'e' la pagina.
            if ruolo != "mono":
                out.append(f"{ruolo}: il lock dice `{voluto}`, la pagina non "
                           "dichiara nessun carattere")
        elif voluto.lower() != avuto.lower():
            out.append(f"{ruolo}: il lock dice `{voluto}`, la pagina ha `{avuto}`")

    lay = report.get("layout") or {}
    forma = lock.get("forma") or {}
    if forma.get("radius_family"):
        avuto = lay.get("radius_family")
        if not avuto:
            out.append(f"raggio: il lock dice `{forma['id']}`, la pagina non "
                       "dichiara nessun raggio")
        elif avuto != forma["radius_family"]:
            out.append(f"raggio: il lock dice `{forma['id']}` "
                       f"({forma['radius_family']}), la pagina ha {avuto}")

    out += scostamenti_motion(lock, text)
    return out


def _token(ident: str, text: str) -> bool:
    """L'id come **token**, non come sottostringa.

    Con `in` nudo il lock che dice `pin` si accontentava di uno `spinner`, e
    `rive` di `scroll-driven`: dieci id del catalogo sono contenuti in un altro.
    Il confine e' su lettere e cifre, non sul trattino — cosi' `.fx-curtain-up`
    vale per `curtain-up`, mentre `spinner` non vale per `pin`.
    """
    import re as _re
    return bool(_re.search(rf"(?<![a-z0-9]){_re.escape(ident.lower())}(?![a-z0-9])",
                           text.lower()))


def scostamenti_motion(lock: dict, text: str) -> list[str]:
    """Effetti e hero: senza questo il lock li scriveva e nessuno li leggeva.

    Si cercano per **id** — la convenzione con cui il catalogo di Vera li
    genera (`.fx-curtain-up`, `@keyframes k-curtain-up`, `data-fx="curtain-up"`)
    e con cui l'hero si firma (`data-hero="…"`). Senza `text` tace: non e'
    una pagina, e' una chiamata che non puo' sapere.
    """
    if not text:
        return []
    out = []
    eff = lock.get("effetti")
    # Quando il catalogo manca, `costruisci` scrive `{"non_sorteggiati": …}`:
    # iterarci sopra dava le CHIAVI, e il referto accusava la pagina di non
    # contenere un effetto chiamato «non_sorteggiati». Un falso positivo su un
    # lock legittimo — e i falsi positivi sono la ragione per cui i controlli
    # smettono di essere letti.
    mancanti = ([e for e in eff if isinstance(e, str) and not _token(e, text)]
                if isinstance(eff, list) else [])
    if mancanti:
        elenco = ", ".join(f"`{e}`" for e in mancanti)
        verbo = "non si trova" if len(mancanti) == 1 else "non si trovano"
        out.append(f"motion: il lock dice {elenco}, ma nella pagina {verbo}")

    hero = lock.get("hero") or {}
    hid = hero.get("id") if isinstance(hero, dict) else None
    if hid is not None and f'data-hero="{hid}"' not in text:
        out.append(f"hero: il lock dice l'archetipo `{hid}`, la pagina non lo "
                   f'firma — serve `data-hero="{hid}"` sulla sezione hero, o '
                   "l'hero nel lock e' una decisione che nessuno puo' verificare")
    return out


def main() -> int:
    ap_ = argparse.ArgumentParser(description="Il lock delle decisioni di craft")
    ap_.add_argument("--project", help="slug del progetto")
    ap_.add_argument("--seed", default="", help="YYYYMMDDHH (lo slug lo aggiunge lui)")
    ap_.add_argument("--out", help="apps/<slug>/craft-lock.json")
    ap_.add_argument("--surface", choices=("marketing", "dashboard", "app"),
                     default="marketing",
                     help="landing o back office: la tenda e l'hero sono regole "
                          "da landing")
    ap_.add_argument("--pick", action="append", metavar="ASSE=ID",
                     help="la scelta dell'owner: colore=… font=… forma=…")
    ap_.add_argument("--last", action="append", metavar="ASSE=v,v",
                     help="esclusioni per asse")
    ap_.add_argument("--show", metavar="FILE", help="stampa un lock esistente")
    args = ap_.parse_args()

    if args.show:
        p = Path(args.show)
        if not p.is_file():
            print(f"nessun lock in {p}", file=sys.stderr)
            return 1
        try:
            print(json.dumps(json.loads(p.read_text(encoding="utf-8")),
                             ensure_ascii=False, indent=1))
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            print(f"{p} non e' leggibile come lock: {exc}", file=sys.stderr)
            return 1
        return 0

    if not args.project or not args.out:
        print("servono --project e --out (o --show)", file=sys.stderr)
        return 2

    escluse: dict[str, list[str]] = {}
    for raw in args.last or []:
        a, _, v = raw.partition("=")
        escluse[a.strip().lower()] = [x.strip() for x in v.split(",") if x.strip()]

    lock = applica_scelte(
        costruisci(args.project, args.seed, escluse, args.surface), args.pick)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(lock, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    c, f, s = lock["colore"], lock["font"], lock["forma"]
    print(f"{out}")
    print(f"  colore  {c['id']:12s} {c['accent']}  ({c['famiglia']})"
          + ("  ← owner" if c.get("scelto_da") else ""))
    print(f"  font    {f['id']:12s} {f['display']} + {f['body']} + {f['mono']}"
          + ("  ← owner" if f.get("scelto_da") else ""))
    print(f"  forma   {s['id']:12s} raggio {s['radius']} · {s['shape']}"
          + ("  ← owner" if s.get("scelto_da") else ""))
    if isinstance(lock.get("effetti"), list):
        print(f"  effetti {', '.join(lock['effetti'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
