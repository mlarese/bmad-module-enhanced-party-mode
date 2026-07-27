#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Italiano scritto contro italiano tradotto — misurato, non raccomandato.

Deciso in consiglio il 2026-07-27, sul rilievo dell'owner: «usi un italiano che
è la traduzione dall'inglese, il senso in italiano si perde».

Il primo dato ha cambiato la diagnosi. Il copy **fisso** del catalogo hero
regge — «Cento anni di carte, una stanza», «Quattro notti di musica in cava» —
mentre marcisce quello scritto a runtime. Non e' un difetto di lingua: e' un
difetto di **provenienza**. Il testo scritto guardando una cosa vera tiene; il
testo generato dal nulla scivola nel vocabolario internazionale della landing,
che in italiano non lo parla nessuno.

Due misure, e nessuna delle due giudica lo stile:

  1. **I marcatori** — formule che in italiano non esistono se non come calco:
     «scopri di piu'», «prenota la tua vacanza», «soluzioni su misura», «noi
     crediamo». Tarati contro le 75 stringhe di copy buono del catalogo, che
     devono passare **tutte** pulite: un marcatore che accusa «Cento anni di
     carte» e' un marcatore sbagliato, e si toglie.
  2. **Il lessico del dominio** — ogni titolo deve contenere almeno una parola
     che il mestiere usa davvero, raccolta *prima* di scrivere (`copy_lock.py`).
     Una headline che non ne contiene nessuna parla di niente: e' la traduzione
     di una landing che parlava d'altro.

Cio' che il consiglio ha **rifiutato** di misurare, e va lasciato stare: la
frase nominale come colpo finale, la domanda retorica, il periodo breve. Sono
italiano legittimo, e vietarli produce prosa impaurita — grigia, e peggiore del
calco perche' non la nota nessuno. La misura prende le formule importate, non
il ritmo.

Usage:
    uv run scripts/copy_check.py apps/<slug>/index.html
    uv run scripts/copy_check.py apps/<slug>/*.html --lessico apps/<slug>/copy-lock.json
    uv run scripts/copy_check.py --frase "Scopri di piu' sulla tua vacanza"

Exit: 0 pulito · 1 marcatori o titoli senza lessico di dominio.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- i marcatori
# (id, regex, cos'e' in inglese, cosa si scrive invece)
#
# Regola di ammissione: ogni marcatore deve lasciare pulito il copy buono del
# catalogo. Sono formule **importate**, non scelte di ritmo.
MARCATORI: list[tuple[str, str, str, str]] = [
    ("scopri-di-piu", r"\bscopri (?:di piu|come|tutto|subito)\b", "learn more",
     "il verbo del mestiere: «guarda le camere», «chiedi il preventivo»"),
    ("possessivo-cta", r"\b(?:prenota|trasforma|inizia|pianifica|crea|costruisci|"
                       r"scopri|vivi|scegli) (?:il tuo|la tua|i tuoi|le tue)\b",
     "book your / transform your", "l'articolo: «prenota le ferie», non «la tua vacanza»"),
    ("inizia-ora", r"\b(?:inizia|comincia|parti) (?:ora|oggi|subito)\b", "get started now",
     "cosa succede se clicca: «chiedi il preventivo», «chiama in reception»"),
    ("sblocca", r"\bsblocc(?:a|are|hi) (?:il|la|i|le|tutt[oaie])\b", "unlock",
     "il verbo concreto: «apri», «attiva», «accedi a»"),
    ("potenzia", r"\bpotenzi(?:a|are) (?:il|la|i|le|tuo|tua)\b", "boost / supercharge",
     "cosa migliora davvero, con un numero se c'e'"),
    ("soluzioni-su-misura", r"\bsoluzion[ei] (?:su misura|personalizzat)", "tailored solutions",
     "il servizio con il suo nome: «mezza pensione», «navetta dal centro»"),
    ("su-misura-per-te", r"\bsu misura per (?:te|voi|il tuo|la tua)\b", "tailored for you",
     "per chi, detto: «per chi arriva in treno», «per famiglie con bambini»"),
    ("senza-soluzione-continuita", r"\bsenza soluzione di continuit", "seamless",
     "«senza interruzioni», o meglio: si toglie e si dice cosa fa"),
    ("all-avanguardia", r"\b(?:all'|all )avanguardia\b", "cutting-edge",
     "l'anno, il modello, il numero — o niente"),
    ("partner-ideale", r"\b(?:il|la|tuo|tua) partner (?:ideale|di fiducia|perfetto)\b",
     "your trusted partner", "cosa fai, non cosa dici di essere"),
    ("leader-di-settore", r"\bleader (?:di settore|del settore|nel settore)\b",
     "industry leader", "un fatto verificabile, o si taglia"),
    ("esperienza-unica", r"\besperienz[ae] (?:unic|indimenticabil|indiment|su misura)",
     "unique experience", "cosa si vede, si mangia, si sente"),
    ("noi-ridondante", r"\bnoi (?:crediamo|offriamo|siamo convinti|pensiamo che)\b",
     "we believe / we offer", "l'italiano il soggetto lo omette: «crediamo che»"),
    ("che-tu-sia", r"\bche tu sia\b", "whether you're",
     "due frasi, o una sola che sceglie il destinatario"),
    ("ecco-perche", r"(?:^|[.!?»]\s+)ecco perch[eé]\b", "that's why",
     "«per questo», «cosi'» — o si lega la frase a quella prima"),
    ("non-si-tratta-di", r"\bnon si tratta (?:solo )?di .{2,40}?,? ma di\b",
     "it's not about X, it's about Y", "si dice la cosa e basta"),
    ("costruito-per", r"\b(?:costruit|progettat)[oaie] per (?:il tuo|la tua|te|offrirti)\b",
     "built for you", "«fatto per», o cosa fa e per chi"),
    ("alimentato-da", r"\balimentat[oaie] da\b", "powered by",
     "«con», «funziona con» — o si tace la tecnologia"),
    ("modo-migliore", r"\bil modo (?:migliore|piu semplice|piu veloce) per\b",
     "the best way to", "il vantaggio detto per intero"),
    ("nel-mondo-di-oggi", r"\bnel mondo di oggi\b|\boggi piu che mai\b",
     "in today's world / now more than ever", "si toglie: non aggiunge niente"),
    ("prossimo-livello", r"\b(?:al|il) (?:prossimo|next) livello\b", "to the next level",
     "cosa cambia in concreto"),
    ("scelta-giusta", r"\bla scelta (?:giusta|perfetta) per\b", "the right choice for",
     "il motivo, non l'etichetta"),
]

TAG_TESTO = re.compile(r"<(h1|h2|h3|button|a)\b[^>]*>(.*?)</\1>", re.I | re.S)
VIA_SCRIPT = re.compile(r"<(script|style|template)\b[^>]*>.*?</\1>", re.I | re.S)
VIA_TAG = re.compile(r"<[^>]+>")
VIA_ENTITA = re.compile(r"&[a-z]+;|&#\d+;", re.I)
PAROLA = re.compile(r"[a-zàèéìòóùü']{3,}", re.I)

# Le parole che non contano come lessico di dominio: ci sono in qualunque testo.
GRAMMATICALI = {
    "che", "con", "per", "del", "della", "dei", "delle", "dal", "dalla", "nel",
    "nella", "sul", "sulla", "una", "uno", "gli", "gliene", "non", "piu", "più",
    "come", "dove", "quando", "questo", "questa", "questi", "queste", "tutto",
    "tutta", "tutti", "tutte", "sono", "essere", "avere", "fare", "puo", "può",
    "anche", "solo", "ogni", "ogni", "loro", "nostro", "nostra", "vostro",
    "tuo", "tua", "tuoi", "tue", "suo", "sua", "sono", "siamo", "hai", "abbiamo",
    "qui", "cosi", "così", "senza", "sempre", "mai", "già", "gia", "dopo",
    "prima", "ancora", "molto", "poco", "bene", "meglio", "altro", "altra",
    "altri", "altre", "stesso", "stessa", "grazie", "info", "home", "contatti",
}


def testo_visibile(html: str) -> str:
    """Solo cio' che si legge: via script, style e marcatura."""
    t = VIA_SCRIPT.sub(" ", html)
    t = VIA_TAG.sub(" ", t)
    t = VIA_ENTITA.sub(" ", t)
    return re.sub(r"\s+", " ", t).strip()


def _senza_accenti(s: str) -> str:
    """`piu'` e `più` devono cadere sullo stesso marcatore."""
    tavola = {"à": "a", "è": "e", "é": "e", "ì": "i", "ò": "o", "ó": "o",
              "ù": "u", "ü": "u", "’": "'"}
    return "".join(tavola.get(c, c) for c in s.lower())


def marcatori(testo: str) -> list[dict]:
    """Le formule importate, con la riga in cui stanno."""
    piatto = _senza_accenti(testo)
    trovati = []
    for ident, pattern, inglese, invece in MARCATORI:
        for m in re.finditer(pattern, piatto, re.I):
            a, b = max(0, m.start() - 30), min(len(piatto), m.end() + 30)
            trovati.append({"id": ident, "trovato": testo[m.start():m.end()],
                            "contesto": "…" + piatto[a:b].strip() + "…",
                            "inglese": inglese, "invece": invece})
            break  # una volta per formula: il referto elenca difetti, non occorrenze
    return trovati


def titoli(html: str) -> list[tuple[str, str]]:
    """(tag, testo) di titoli e richiami — dove il lessico del dominio conta."""
    out = []
    for m in TAG_TESTO.finditer(html):
        t = testo_visibile(m.group(2))
        if t and len(t.split()) >= 2:
            out.append((m.group(1).lower(), t))
    return out


def elenco_parole(testo: str) -> list[str]:
    """Le occorrenze, in ordine — non l'insieme.

    `parole()` restituisce un set, e chi contava le frequenze sommando set
    contava **una volta per documento**: con un corpus di un file solo ogni
    parola usciva a 1, la soglia «chi ripete nomina il mestiere» non scattava
    mai e il lessico restava vuoto. Misurato il 2026-07-27.
    """
    return [p.lower().strip("'") for p in PAROLA.findall(_senza_accenti(testo))
            if p.lower().strip("'") not in GRAMMATICALI]


def parole(testo: str) -> set[str]:
    return set(elenco_parole(testo))


def copertura_lessico(html: str, lessico: list[str]) -> list[dict]:
    """Ogni titolo deve toccare il dominio almeno una volta.

    Non e' una regola di stile: un titolo che non contiene nessuna parola del
    mestiere e' un titolo che varrebbe per qualunque cliente — cioe' la
    traduzione di una landing che parlava di un'altra cosa.
    """
    vocab = {_senza_accenti(v).lower() for v in lessico if v}
    if not vocab:
        return []
    fuori = []
    for tag, t in titoli(html):
        if tag in ("a", "button"):
            continue  # le CTA sono corte per mestiere: il vincolo starebbe stretto
        if not (parole(t) & vocab):
            fuori.append({"tag": tag, "testo": t})
    return fuori


def problemi(html: str, lessico: list[str] | None = None) -> list[str]:
    """Le due misure, in righe pronte per il referto."""
    fuori = []
    for m in marcatori(testo_visibile(html)):
        fuori.append(f"copy: «{m['trovato']}» è {m['inglese']} tradotto "
                     f"({m['contesto']}) → {m['invece']}")
    for t in copertura_lessico(html, lessico or []):
        fuori.append(f"copy: «{t['testo']}» non contiene nessuna parola del "
                     "dominio — varrebbe per qualunque cliente")
    return fuori


def _lessico_da(path: Path | None) -> list[str]:
    if path is None:
        return []
    if not path.is_file():
        raise SystemExit(f"{path} non esiste: il lessico si raccoglie prima di scrivere "
                         "(`copy_lock.py`)")
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise SystemExit(f"{path.name} illeggibile: {exc}")
    if isinstance(d, dict):
        return list(d.get("lessico") or [])
    return list(d) if isinstance(d, list) else []


def main() -> int:
    ap = argparse.ArgumentParser(description="Italiano scritto contro italiano tradotto")
    ap.add_argument("pagine", nargs="*", help="file HTML da leggere")
    ap.add_argument("--lessico", help="apps/<slug>/copy-lock.json")
    ap.add_argument("--frase", help="prova una frase sola, senza file")
    ap.add_argument("--list", action="store_true", help="i marcatori, uno per riga")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    args = ap.parse_args()

    if args.list:
        print(f"# {len(MARCATORI)} formule importate\n")
        for ident, _, inglese, invece in MARCATORI:
            print(f"  {ident:28s} {inglese:34s} → {invece}")
        return 0

    if args.frase:
        trovati = marcatori(args.frase)
        if args.format == "json":
            print(json.dumps(trovati, ensure_ascii=False, indent=1))
        else:
            for m in trovati:
                print(f"  «{m['trovato']}» — {m['inglese']} → {m['invece']}")
            print("  pulita." if not trovati else "")
        return 1 if trovati else 0

    if not args.pagine:
        print("servono delle pagine, o --frase", file=sys.stderr)
        return 2

    lessico = _lessico_da(Path(args.lessico) if args.lessico else None)
    esito, guai = {}, 0
    for p in args.pagine:
        f = Path(p)
        if not f.is_file():
            print(f"  ! {p} non esiste", file=sys.stderr)
            continue
        righe = problemi(f.read_text(encoding="utf-8", errors="replace"), lessico)
        esito[str(f)] = righe
        guai += len(righe)

    if args.format == "json":
        print(json.dumps(esito, ensure_ascii=False, indent=1))
        return 1 if guai else 0

    for f, righe in esito.items():
        print(f"\n## {f}")
        for r in righe:
            print(f"  - {r}")
        if not righe:
            print("  italiano scritto, non tradotto.")
    return 1 if guai else 0


if __name__ == "__main__":
    sys.exit(main())
