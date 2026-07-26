#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Seeded randomized creation rules for a mobile web app / PWA.

Same law as `dashboard_recipe.py` (one RNG stream per axis, MEMORY exclusions,
declared conflicts, mutually-distinct batch), applied to the surface where the
skill was thinnest: a mobile web app is not a narrow landing, and its **graphic**
craft — the splash, the brand background, the app mark, the onboarding — is the
part that reads first and was previously left to reflex.

Usage:
    uv run scripts/mobile_recipe.py --domain food --activity "consegna a domicilio"
    uv run scripts/mobile_recipe.py --seed 2026072609 --last-palette concrete-teal
    uv run scripts/mobile_recipe.py --batch "app-a,app-b" --out-dir _bmad-output/mobile-recipes
    uv run scripts/mobile_recipe.py --format json
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[1] / "assets" / "mobile-corpus.json"


APP_SHELLS: dict[str, str] = {
    "tab-bar": "3–5 voci in basso, etichette sempre visibili; la vista attiva non si nasconde",
    "fab-primary": "una azione flottante domina, la tab bar si riduce a contorno",
    "gesture-stack": "stack con swipe-back e header contestuale: poche voci fisse",
    "segmented-home": "una home con segmenti in cima, poche schermate profonde",
    "drawer-plus-tab": "tab per il primario, drawer per il resto — mai il contrario",
    "single-scroll": "una vista lunga con ancore: niente navigazione se non serve",
}

# The graphic axes this recipe exists for.
SPLASH: dict[str, str] = {
    "first-frame": "nessuna schermata dedicata: la shell si compone (header, tab, skeleton) mentre carica",
    "mark-draw": "il marchio si disegna in SVG (`stroke-dasharray`) e si ritira",
    "gradient-wash": "il fondo di marca entra pieno schermo e si ritrae dove vivrà nell'app",
    "type-lockup": "il nome per esteso, tipografico, sulla terza voce",
    "photo-fade": "immagine di marca che sfuma nel primo schermo vero",
    "mask-reveal": "la forma del marchio fa da maschera e si apre sull'app",
}

APP_BACKGROUNDS: dict[str, str] = {
    "mesh-gradient": "3–4 `radial-gradient` sfalsati sui colori di palette + grana anti-banding",
    "linear-brand": "lineare a 2–3 fermate sull'angolo di casa, una sola direzione in tutta l'app",
    "radial-glow": "fondo pieno + un alone radiale dietro il contenuto chiave (raggio dichiarato)",
    "duotone-fade": "due tinte di marca che si incontrano, il punto d'incontro è una scelta",
    "solid-texture": "pieno + la texture di casa — l'anti-gradiente, dichiarato non subito",
    "photo-blur": "foto di marca sfocata sotto un velo di colore (una sola, non per schermata)",
}

BRAND_MARKS: dict[str, str] = {
    "maskable-glyph": "glifo dentro la safe zone maskable: nessun ritaglio su Android",
    "monogram-tile": "monogramma su tile di colore pieno, leggibile a 48px",
    "mark-on-gradient": "marchio in negativo sul gradiente d'app, stesso angolo",
    "line-mark": "marchio a tratto con lo stesso peso ottico della tipografia",
}

ONBOARDINGS: dict[str, str] = {
    "none-declared": "nessun onboarding: l'app si spiega da sola — scelta dichiarata, non omissione",
    "three-cards": "tre schermate, una illustrazione e una frase ciascuna, saltabili",
    "progressive": "nessun tour: il suggerimento compare al primo uso di ogni area",
    "value-first": "una sola schermata con la promessa e l'azione, niente carosello",
    "permission-primer": "prima del permesso di sistema, una schermata che dice perché",
}

DEPTHS: dict[str, str] = {
    "flat-rules": "nessuna ombra: gerarchia con hairline e colore",
    "soft-elevation": "2–3 livelli di ombra come token nominati, non valori a occhio",
    "glass-layer": "`backdrop-filter` su **un solo** livello (sheet o header)",
    "stacked-cards": "profondità per sovrapposizione e scala, non per ombra",
}

ILLUSTRATIONS: dict[str, str] = {
    "geometric-shapes": "forme dalla palette, SVG inline, zero libreria",
    "line-art": "tratto coerente col marchio, stesso peso in tutta l'app",
    "photo-crop": "fotografia ritagliata nella forma di casa",
    "type-as-image": "la tipografia fa da illustrazione, nessun disegno",
    "none-icon-only": "solo icone di sistema — dichiarato, quindi coerente ovunque",
}

LIST_PATTERNS: dict[str, str] = {
    "row-avatar": "riga con avatar/thumb, due livelli di testo, chevron solo se apre",
    "card-stack": "card impilate a piena larghezza, una per elemento",
    "compact-data": "righe dense con cifre in `tabular-nums`, per liste lunghe",
    "timeline": "asse temporale con raggruppamento per giorno",
    "grid-tiles": "griglia 2 colonne per contenuti visivi",
    "swipe-actions": "azioni sotto la riga con swipe, sempre con equivalente tappabile",
}

SHEET_PATTERNS: dict[str, str] = {
    "bottom-sheet": "foglio dal basso con maniglia, chiude a trascinamento",
    "snap-points": "foglio a due altezze (anteprima / pieno)",
    "full-modal": "modale a pieno schermo con chiusura esplicita",
    "inline-expand": "il dettaglio si apre dentro la lista, senza cambiare schermata",
}

NAV_TRANSITIONS: dict[str, str] = {
    "shared-element": "un elemento continua fra le due viste (thumb → header)",
    "slide-stack": "la vista figlia entra da destra, la madre arretra",
    "fade-through": "dissolvenza con scala minima fra pari livello",
    "sheet-rise": "il dettaglio sale come foglio, la madre resta visibile",
    "none-instant": "cambio immediato — dichiarato, per app-strumento",
}

STATE_TREATMENTS: dict[str, str] = {
    "skeleton-shape": "lo skeleton ha la **forma** del contenuto vero, non barre generiche",
    "illustrated-empty": "vuoto con illustrazione di casa + una azione che lo riempie",
    "inline-retry": "errore dentro la lista con un `Riprova` che riprova davvero",
    "optimistic": "l'azione si vede subito e rientra se il server rifiuta",
}

INPUT_PATTERNS: dict[str, str] = {
    "single-field-step": "un campo per schermata nei flussi lunghi",
    "sticky-cta": "azione fissa sopra la safe area, il form scorre sotto",
    "inline-validation": "l'errore compare al blur del campo, non al submit",
    "native-first": "controlli nativi (`date`, `select`, `inputmode`) invece di widget finti",
    "numeric-keypad": "`inputmode=\"decimal\"` e tastiera giusta per ogni campo",
}

PALETTE_FAMILIES: dict[str, str] = {
    "graphite-signal": "grigi profondi + un accento saturo unico",
    "sea-foam": "acqua/schiuma, chiaro e arioso",
    "clay-ember": "terre calde con brace come accento",
    "pine-firn": "verde bosco e neve compatta",
    "obsidian-champagne": "notte con ottone caldo",
    "indigo-sand": "indaco profondo su sabbia",
    "moss-cream": "muschio e panna, naturale non nostalgico",
    "slate-citrus": "ardesia con agrume come segnale",
}

RADIUS_FAMILIES: dict[str, str] = {
    "sharp": "0–2px btn / 0–4px box — strumento, dichiarato",
    "soft": "8–14px btn / 10–16px box — prodotto",
    "rounded": "16–24px btn / 16–20px box — consumer caldo",
    "pill": "999px sui btn, box soft/rounded — consumer, non tutto pill",
    "mixed-signal": "CTA morbida su chrome rigoroso",
}

TYPE_TRIOS: dict[str, str] = {
    "grotesk-serif-mono": "grotesque UI + serif per i titoli + mono per dati e label",
    "humanist-mono": "sans umanista + mono come voce primaria di metriche",
    "display-neutral-italic": "display caratterizzato + neutra da lettura + corsivo dedicato",
    "condensed-wide": "condensata sui titoli + larga da lettura, contrasto di larghezza",
    "single-superfamily": "una superfamiglia su più assi variabili — dichiarata, non pigra",
}

DENSITIES: dict[str, str] = {
    "airy-consumer": "poche cose per schermata, respiro alto",
    "balanced": "densità media, la lista resta scorribile con una mano",
    "dense-utility": "molte righe visibili: app-strumento, cifre allineate",
}

MOTION_TECHNIQUES: dict[str, str] = {
    "sheet-spring": "foglio con molla corta, mai rimbalzo lungo",
    "shared-element": "continuità fra lista e dettaglio",
    "tab-morph": "l'indicatore di tab si sposta, non lampeggia",
    "press-scale": "feedback di pressione a 0.97 con ritorno rapido",
    "list-stagger": "ingresso scalato di 20–40ms per riga, solo al primo caricamento",
    "skeleton-shimmer": "attesa che si muove appena, mai un lampeggio",
    "pull-refresh": "trascinamento con soglia netta e ritorno elastico",
    "gradient-drift": "il fondo di marca deriva lentissimo — solo `transform`, mai `background-position`",
}

EXTRAS: dict[str, str] = {
    "install-prompt": "invito a installare al momento giusto, non al primo secondo",
    "offline-state": "schermo onesto quando la rete manca, con cosa resta usabile",
    "theme-color-sync": "`<meta name=\"theme-color\">` che segue la sezione: la barra di sistema entra nel design",
    "safe-area-art": "la grafica usa la safe area invece di subirla",
    "scroll-restore": "tornando indietro la lista è dove l'avevi lasciata",
    "share-target": "l'app riceve contenuti condivisi dal sistema",
    "haptic-cue": "vibrazione breve sulle conferme (dove supportata), mai su ogni tap",
    "skeleton-parity": "lo skeleton coincide col layout finale: zero salto al caricamento",
    "one-hand-check": "ogni azione primaria raggiungibile col pollice, verificato",
}

# Domain-aware weights: {domain: {axis: {value: weight}}}, default weight 1.
# Same contract as dashboard_recipe.DOMAIN_WEIGHTS: weights bias the seeded
# draw, never remove an option; `--flat` disables them. The knowledge is the
# craft-rules chrome table (rounded → consumer warm, sharp → tool) plus what
# each vertical's list actually holds (food shows dishes, fintech shows rows).
DOMAIN_WEIGHTS: dict[str, dict[str, dict[str, int]]] = {
    "fintech": {
        "radius_family": {"sharp": 3, "soft": 3, "mixed-signal": 3, "pill": 1, "rounded": 1},
        "density": {"dense-utility": 3, "balanced": 2},
        "list_pattern": {"compact-data": 3, "timeline": 2},
        "illustration": {"none-icon-only": 2, "geometric-shapes": 2},
    },
    "food": {
        "radius_family": {"rounded": 3, "pill": 2},
        "list_pattern": {"card-stack": 3, "grid-tiles": 3, "compact-data": 1},
        "density": {"airy-consumer": 3},
        "illustration": {"photo-crop": 3},
    },
    "fitness": {
        "radius_family": {"pill": 3, "rounded": 2},
        "list_pattern": {"timeline": 3, "card-stack": 2},
        "onboarding": {"permission-primer": 2},
    },
    "travel": {
        "radius_family": {"rounded": 3, "soft": 2},
        "list_pattern": {"grid-tiles": 3, "card-stack": 2},
        "illustration": {"photo-crop": 3},
        "density": {"airy-consumer": 3},
    },
    "ecommerce": {
        "list_pattern": {"grid-tiles": 3, "card-stack": 2},
        "radius_family": {"soft": 2, "rounded": 2},
        "sheet_pattern": {"bottom-sheet": 2, "snap-points": 2},
    },
    "productivity": {
        "density": {"dense-utility": 3, "balanced": 2},
        "list_pattern": {"compact-data": 3, "swipe-actions": 2},
        "radius_family": {"soft": 3, "sharp": 2},
        "illustration": {"none-icon-only": 2},
    },
    "health": {
        "radius_family": {"rounded": 3, "soft": 2},
        "illustration": {"line-art": 2, "geometric-shapes": 2},
        "onboarding": {"permission-primer": 3},
    },
    "mobility": {
        "app_shell": {"fab-primary": 2, "tab-bar": 2},
        "list_pattern": {"timeline": 2, "row-avatar": 2},
        "state_treatment": {"optimistic": 2},
    },
}

# Aesthetic affinities: the palette is the register anchor, and the visual axes
# are drawn in tune with it. {palette: {axis: {value: multiplier}}} — >1 favours,
# <1 disfavours, nothing is ever removed. Measured before adding this layer:
# 12.2% of recipes carried at least one jarring pairing (obsidian-champagne with
# pill buttons, clay-ember promising matter with icon-only illustration...).
# This is codified taste — one inspectable table, not an opaque score — sourced
# from the same knowledge as craft-rules' chrome table.
AFFINITY: dict[str, dict[str, dict[str, float]]] = {
    # notte + ottone, registro luxury: segno e spigolo, non morbidezze consumer
    "obsidian-champagne": {
        "radius_family": {"sharp": 3, "mixed-signal": 2, "pill": 0.3, "rounded": 0.4},
        "illustration": {"line-art": 2, "type-as-image": 2},
        "type_voices": {"display-neutral-italic": 2, "condensed-wide": 2},
        "depth": {"flat-rules": 2, "glass-layer": 2},
    },
    # terre calde materiche: rotondità e fotografia, non freddezza da tool
    "clay-ember": {
        "radius_family": {"rounded": 3, "soft": 2, "sharp": 0.5},
        "illustration": {"photo-crop": 3, "none-icon-only": 0.4},
        "depth": {"soft-elevation": 2},
    },
    "sea-foam": {
        "radius_family": {"rounded": 2, "pill": 2},
        "illustration": {"geometric-shapes": 2, "line-art": 2},
        "type_voices": {"humanist-mono": 2, "condensed-wide": 0.4},
        "depth": {"flat-rules": 2},
    },
    "graphite-signal": {
        "radius_family": {"soft": 2, "sharp": 2, "pill": 0.4},
        "illustration": {"none-icon-only": 2, "geometric-shapes": 2},
        "type_voices": {"humanist-mono": 2, "grotesk-serif-mono": 2},
    },
    "pine-firn": {
        "radius_family": {"soft": 2, "rounded": 2},
        "illustration": {"line-art": 2, "photo-crop": 2},
    },
    "indigo-sand": {
        "radius_family": {"sharp": 2, "mixed-signal": 2},
        "type_voices": {"condensed-wide": 2},
    },
    "moss-cream": {
        "radius_family": {"rounded": 2, "soft": 2},
        "illustration": {"line-art": 2},
        "depth": {"soft-elevation": 2},
    },
    "slate-citrus": {
        "radius_family": {"mixed-signal": 2, "pill": 2},
        "illustration": {"geometric-shapes": 2},
    },
}

# Hard aesthetic clashes: resolved like conflicts (re-pick, declared). Few and
# defensible — the soft multipliers above handle everything else.
DISSONANCES: list[tuple[str, str, str, str, str]] = [
    ("palette_family", "obsidian-champagne", "radius_family", "pill",
     "lusso notturno con bottoni pillola consumer: registro rotto"),
    ("palette_family", "clay-ember", "illustration", "none-icon-only",
     "terre materiche con sole icone di sistema: la palette promette materia che l'app non mostra"),
]

# Pairs that would say the same thing twice, contradict each other, or cost twice.
CONFLICTS: list[tuple[str, str, str, str, str]] = [
    ("splash", "gradient-wash", "app_background", "solid-texture",
     "lo splash promette un gradiente che l'app non ha"),
    ("splash", "first-frame", "onboarding", "three-cards",
     "«nessuna schermata sprecata» e poi tre schermate"),
    ("app_background", "photo-blur", "depth", "glass-layer",
     "due sfocature sovrapposte: costo GPU doppio su telefono"),
    ("depth", "glass-layer", "app_background", "solid-texture",
     "un backdrop-filter su un fondo piatto non sfoca niente: il vetro non si vede"),
    ("illustration", "none-icon-only", "state_treatment", "illustrated-empty",
     "vuoto illustrato senza un linguaggio di illustrazione"),
    ("app_shell", "fab-primary", "input_pattern", "sticky-cta",
     "due bottoni flottanti nello stesso angolo"),
    ("app_shell", "single-scroll", "nav_transition", "slide-stack",
     "non c'è stack da far scorrere"),
    ("app_shell", "gesture-stack", "sheet_pattern", "full-modal",
     "due modi diversi di uscire dalla stessa profondità"),
    ("nav_transition", "none-instant", "motion", "shared-element",
     "transizione dichiarata assente e poi un elemento condiviso"),
    ("depth", "flat-rules", "motion", "press-scale",
     "nessuna elevazione ma feedback di elevazione"),
    ("app_background", "mesh-gradient", "extras", "safe-area-art",
     "il fondo è già la grafica: la safe area non aggiunge un secondo tema"),
]

INVARIANTS: list[str] = [
    "**shell ad altezza viewport — la barra in basso è sempre visibile, il contenuto "
    "non scorre come una pagina desktop**: contenitore `height: 100svh` (`100dvh` se deve "
    "seguire la barra del browser) + `overflow: hidden` + `grid-template-rows: auto 1fr auto` "
    "→ **scorre il `main`, non la pagina**. Header e barra restano fermi fra loro: solo il "
    "contenuto in mezzo scorre. La barra di navigazione è la **terza riga della griglia, non "
    "`position: fixed`**: così non serve compensare con padding, non copre l'ultimo elemento "
    "della lista e non salta con la tastiera aperta. `overscroll-behavior: contain` sul "
    "`main`. Vale **solo per la web app**: su una landing la pagina scorre normalmente",
    "**tastiera virtuale**: `interactive-widget=resizes-content` nel meta viewport; al focus di "
    "un campo la barra può ritirarsi, ma non deve mai coprire l'input attivo",
    "**`viewport-fit=cover` + `env(safe-area-inset-*)`** su header, tab bar e CTA fisse: niente contenuto sotto la tacca o la barra gesti — la barra include `padding-bottom: env(safe-area-inset-bottom)` nella propria altezza",
    "**altezze in `dvh`/`svh`**, mai `100vh`: la barra del browser mobile cambia altezza durante lo scroll",
    "**target ≥44px** e azione primaria nel terzo basso dello schermo (thumb zone); nessun hover come unica via",
    "**manifest.json**: `name` · `short_name` · `start_url` · `display: standalone` · `theme_color` · icone 192/512 **e** una `maskable`; `background_color` **identico** al fondo dello splash — se differisce, il lampo bianco all'avvio è garantito",
    "**splash solo in `display-mode: standalone`**: in scheda browser è una schermata di attesa regalata all'utente",
    "**gradiente — contrasto sui due estremi**, non nel punto medio: il testo sopra regge AA sia sulla fermata chiara sia sulla scura, o cambia il testo, non il gradiente",
    "**gradiente — grana anti-banding**: un `feTurbulence` o un noise data-URI a bassa opacità, o su schermo mobile le fasce si vedono",
    "**gradiente animato solo su `transform`/`opacity`**: animare `background-position` o i color-stop ridipinge ogni frame a schermo intero",
    "**input a `font-size: 16px`** (o più): sotto, iOS zooma al focus e il layout salta; `inputmode` e `autocomplete` corretti su ogni campo",
    "**empty + skeleton + errore** per ogni lista, con lo skeleton della forma giusta",
    "**mai segnaposti muti senza backend**: ogni contenuto visivo (foto prodotto, "
    "copertina, thumbnail, sfondo card) è un'immagine reale mirata al dominio "
    "(`--domain`), non un rettangolo grigio o un'icona IMG — l'unica eccezione è "
    "l'avatar senza foto, dove l'iniziale su un tondo di palette è lo stato "
    "corretto, non un buco coperto. Diverso dallo skeleton di caricamento e da "
    "`illustrated-empty`: quelli sono attesa vera o zero risultati veri, qui la "
    "card esiste ed è piena — deve mostrare un prodotto, non fingerne l'assenza",
    "**nessun overflow-x di pagina** e nessuna gesture rubata al sistema (swipe-back, pull-to-refresh nativo)",
    "**a11y**: `:focus-visible` visibile, contrasto AA sul fondo reale, `prefers-reduced-motion` ferma anche il fondo animato",
    "**motion repeat** dove ha senso, mai `data-anim-once` di riflesso",
    "**hard-reject palette**: purple-indigo AI · cream+serif+terracotta · Inter/system come display",
]

AXIS_ORDER: list[tuple[str, str, dict[str, str]]] = [
    ("app_shell", "Shell dell'app", APP_SHELLS),
    ("splash", "Splash", SPLASH),
    ("app_background", "Fondo d'app", APP_BACKGROUNDS),
    ("brand_mark", "Marchio", BRAND_MARKS),
    ("onboarding", "Onboarding", ONBOARDINGS),
    ("depth", "Profondità", DEPTHS),
    ("illustration", "Illustrazione", ILLUSTRATIONS),
    ("list_pattern", "Liste", LIST_PATTERNS),
    ("sheet_pattern", "Fogli e dettaglio", SHEET_PATTERNS),
    ("nav_transition", "Transizione", NAV_TRANSITIONS),
    ("state_treatment", "Stati", STATE_TREATMENTS),
    ("input_pattern", "Input", INPUT_PATTERNS),
    ("palette_family", "Palette family", PALETTE_FAMILIES),
    ("radius_family", "Radius family", RADIUS_FAMILIES),
    ("type_voices", "Voci tipografiche", TYPE_TRIOS),
    ("density", "Densità", DENSITIES),
]

POOLS: dict[str, dict[str, str]] = {name: pool for name, _title, pool in AXIS_ORDER}


def rng_for(seed: str, axis: str) -> random.Random:
    """One independent stream per axis — adjacent hours must not correlate."""
    return random.Random(f"{seed}|{axis}")


def pick(
    pool: dict[str, str],
    seed: str,
    axis: str,
    exclude: list[str] | None = None,
    weights: dict[str, float] | None = None,
) -> str:
    excluded = {e.strip() for e in (exclude or []) if e.strip()}
    candidates = [k for k in pool if k not in excluded] or list(pool)
    if weights:
        # Weighted path only when a table applies: recipes without a domain
        # keep their historical output per seed (choices ≠ choice in RNG use).
        return rng_for(seed, axis).choices(
            candidates, weights=[weights.get(k, 1) for k in candidates]
        )[0]
    return rng_for(seed, axis).choice(candidates)


def pick_many(
    pool: dict[str, str], seed: str, axis: str, n: int, exclude: list[str] | None = None
) -> list[str]:
    excluded = {e.strip() for e in (exclude or []) if e.strip()}
    candidates = [k for k in pool if k not in excluded] or list(pool)
    return rng_for(seed, axis).sample(candidates, min(n, len(candidates)))


def resolve_conflicts(
    choice: dict[str, object], seed: str, taken: dict[str, list[str]] | None = None
) -> list[str]:
    """Re-pick the second axis of any conflicting pair; return the notes.

    Two things a single pass gets wrong, both measured on 2000 seeds:

    - a later pair can re-introduce a value an earlier pair had just banned
      (the re-pick only excluded the value it was replacing);
    - on a multi-value axis the spare pool was computed from the *current* list,
      so a second swap could hand back the item the first swap removed.

    So: keep a per-axis ban list for the whole resolution, and iterate to a fixed
    point. `taken` carries the batch siblings' spent values: a re-pick that
    ignored them could hand a sibling's axis back to this recipe — measured
    before the fix, 63/800 mobile batches and 100/800 dashboard batches broke
    the mutual-distinctness promise exactly on the conflict-rewritten axes. Both are cheap and turn "usually consistent" into "consistent".
    """
    notes: list[str] = []
    taken = taken or {}
    multi_pools = {"extras": EXTRAS, "motion": MOTION_TECHNIQUES}
    banned: dict[str, set[str]] = {}
    clashes = CONFLICTS + DISSONANCES

    for sweep in range(len(clashes) + 1):
        changed = False
        for a_key, a_val, b_key, b_val, why in clashes:
            if choice.get(a_key) != a_val:
                continue
            if b_key in multi_pools:
                chosen = choice.get(b_key) or []
                if not isinstance(chosen, list) or b_val not in chosen:
                    continue
                banned.setdefault(b_key, set()).add(b_val)
                kept = [v for v in chosen if v != b_val]
                spare = [
                    k for k in multi_pools[b_key]
                    if k not in kept and k not in banned[b_key]
                ]
                if spare:
                    kept.append(rng_for(seed, f"{b_key}-swap-{sweep}").choice(spare))
                choice[b_key] = kept
                notes.append(f"`{b_key}` — `{b_val}` sostituito ({why})")
                changed = True
                continue
            if choice.get(b_key) == b_val:
                banned.setdefault(b_key, set()).add(b_val)
                choice[b_key] = pick(
                    POOLS[b_key], seed, f"{b_key}-swap-{sweep}",
                    exclude=sorted(banned[b_key] | set(taken.get(b_key, []))),
                )
                notes.append(f"`{b_key}` — ripescato, `{b_val}` in conflitto ({why})")
                changed = True
        if not changed:
            break
    return notes


def load_corpus() -> dict | None:
    if not CORPUS.exists():
        return None
    with CORPUS.open(encoding="utf-8") as fh:
        return json.load(fh)


def sample_refs(
    corpus: dict, domain: str | None, count: int, seed: str
) -> tuple[list[dict], dict[str, int]]:
    """Domain-matching refs first, then filler. Seeded shuffle.

    Deliberately NOT weighted on the graphic axes. Measured 2026-07-26 on 866
    items: zero carry an honest `splash` or `gradient` trait, because Envato's
    own `/splash-screen` and `/gradient` catalogs return generic templates (6%
    and 0% theme fidelity). Weighting on a trait nothing has would dress up a
    generic sample as research. The recipe declares that gap in the refs header.
    """
    items = corpus.get("items", [])
    rng = random.Random(seed)
    if domain:
        matched = [i for i in items if domain in (i.get("domain") or [])]
        rest = [i for i in items if domain not in (i.get("domain") or [])]
    else:
        matched, rest = [], list(items)
    rng.shuffle(matched)
    rng.shuffle(rest)
    picked = (matched + rest)[:count]

    tally: dict[str, int] = {}
    for it in picked:
        for s in it.get("stack") or []:
            tally[s] = tally.get(s, 0) + 1
    return picked, dict(sorted(tally.items(), key=lambda kv: (-kv[1], kv[0])))


def known_domains(corpus: dict | None) -> list[str]:
    """Domains the corpus can actually weight on."""
    if not corpus:
        return []
    out: set[str] = set()
    for i in corpus.get("items", []):
        out.update(d for d in (i.get("domain") or []) if d != "generic")
    return sorted(out)


ANCHOR = "palette_family"  # the register anchor: everything visual tunes to it


def build(args, seed: str | None = None, taken: dict[str, list[str]] | None = None) -> dict:
    """One recipe. `taken` holds values already spent by siblings in a batch."""
    seed = seed or args.seed
    taken = taken or {}
    flat = getattr(args, "flat", False)
    domain_w: dict[str, dict[str, int]] = {}
    if args.domain and not flat:
        domain_w = DOMAIN_WEIGHTS.get(args.domain, {})
    exclusions = {
        "palette_family": args.last_palette,
        "radius_family": args.last_radius,
        "type_voices": args.last_type,
        "app_shell": args.last_shell,
        "splash": args.last_splash,
        "app_background": args.last_background,
    }
    choice: dict[str, object] = {}
    harmony: list[str] = []
    # The anchor is drawn first so the visual axes can tune to it. Per-axis RNG
    # streams make the order harmless for every unweighted axis.
    order = [ANCHOR] + [k for k, _t, _p in AXIS_ORDER if k != ANCHOR]
    pools = {k: p for k, _t, p in AXIS_ORDER}
    for key in order:
        exclude = list(exclusions.get(key, [])) + taken.get(key, [])
        weights: dict[str, float] = {k: float(v) for k, v in (domain_w.get(key) or {}).items()}
        if not flat and key != ANCHOR:
            aff = AFFINITY.get(str(choice.get(ANCHOR, "")), {}).get(key)
            if aff:
                for v, mult in aff.items():
                    weights[v] = weights.get(v, 1.0) * mult
                harmony.append(f"`{key}` ← `{choice[ANCHOR]}`")
        choice[key] = pick(pools[key], seed, key, exclude, weights=weights or None)
    if domain_w:
        choice["domain_weighted_axes"] = sorted(domain_w)
    if harmony:
        choice["harmony"] = harmony

    counts = rng_for(seed, "counts")
    choice["motion"] = pick_many(MOTION_TECHNIQUES, seed, "motion", counts.choice([2, 3, 3, 4]))
    choice["extras"] = pick_many(EXTRAS, seed, "extras", counts.choice([3, 3, 4]))

    notes = resolve_conflicts(choice, seed, taken)

    signature_pool = {
        "app_background": "il fondo di marca: la prima cosa che si vede, prima del contenuto",
        "splash": "il primo istante — l'unico momento in cui l'app parla da sola",
        "app_shell": "la forma della navigazione",
        "illustration": "il linguaggio grafico degli stati",
        "extras": "il dettaglio che nessun template mette",
    }
    choice["signature"] = pick(signature_pool, seed, "signature")
    choice["signature_why"] = signature_pool[str(choice["signature"])]
    return {"choice": choice, "conflict_notes": notes, "seed": seed}


# Sibling apps may share invariants, never a silhouette.
DISTINCT_AXES = [
    "app_shell",
    "splash",
    "app_background",
    "list_pattern",
    "palette_family",
    "radius_family",
    "type_voices",
]


def build_batch(args, labels: list[str]) -> list[dict]:
    taken: dict[str, list[str]] = {k: [] for k in DISTINCT_AXES}
    out: list[dict] = []
    for i, label in enumerate(labels):
        seed = args.seed if i == 0 else f"{args.seed}-{i}"
        built = build(args, seed=seed, taken=taken)
        built["label"] = label
        for axis in DISTINCT_AXES:
            if len(taken[axis]) < len(POOLS[axis]) - 1:
                taken[axis].append(str(built["choice"][axis]))
        out.append(built)
    return out


def render_md(
    args, built: dict, refs: list[dict], stacks: dict[str, int], corpus: dict | None
) -> str:
    c = built["choice"]
    label = built.get("label")
    lines = [
        f"# Mobile web-app recipe{f' — {label}' if label else ''} (regole randomiche di creazione)",
        f"seed: `{built.get('seed', args.seed)}` · domain: `{args.domain or '—'}` "
        f"· activity: `{label or args.activity or '—'}`",
    ]
    if corpus:
        counts = corpus.get("counts", {})
        lines.append(
            f"corpus: {counts.get('total', 0)} template "
            f"({', '.join(f'{k}={v}' for k, v in (counts.get('by_source') or {}).items())}) "
            f"· built_at {corpus.get('built_at')}"
        )
    else:
        lines.append("corpus: **assente** — esegui `mobile_corpus.py --build` (dichiara il gap)")

    # A domain nobody has is a typo that would otherwise pass for research: the
    # refs would be generic while the header still said "pesati sul dominio".
    if corpus and args.domain:
        avail = known_domains(corpus)
        if args.domain not in avail:
            lines.append(
                f"> **attenzione** — il dominio `{args.domain}` non esiste nel corpus: "
                f"i refs sotto sono **generici**, non pesati. Domini disponibili: "
                f"{', '.join(avail) or 'nessuno'}."
            )
    lines.append("")

    lines.append("## Assi dichiarati")
    lines.append("")
    graphic_axes = {"splash", "app_background", "brand_mark", "onboarding", "illustration", "depth"}
    for key, title, pool in AXIS_ORDER:
        val = str(c[key])
        mark = " ·" if key in graphic_axes else ""
        lines.append(f"- **{title}**{mark} `{val}` — {pool[val]}")
    lines.append(
        "- **Motion** · "
        + ", ".join(f"`{v}`" for v in c["motion"])
        + " — "
        + " · ".join(MOTION_TECHNIQUES[v] for v in c["motion"])
    )
    lines.append(
        "- **Extra** · "
        + ", ".join(f"`{v}`" for v in c["extras"])
        + " — "
        + " · ".join(EXTRAS[v] for v in c["extras"])
    )
    lines.append(f"- **Signature** · `{c['signature']}` — {c['signature_why']}")
    if c.get("domain_weighted_axes"):
        lines.append(
            f"- **Pesi di dominio** (`{args.domain}`) su: "
            + ", ".join(f"`{a}`" for a in c["domain_weighted_axes"])
            + " — bias dichiarato, mai esclusione (`--flat` per l'estrazione uniforme)"
        )
    if c.get("harmony"):
        lines.append(
            "- **Armonia** · " + " · ".join(c["harmony"])
            + " — assi visivi accordati alla palette (affinità estetiche: bias, mai esclusione)"
        )
    lines.append("")

    if built["conflict_notes"]:
        lines.append("## Conflitti risolti")
        for n in built["conflict_notes"]:
            lines.append(f"- {n}")
        lines.append("")

    lines.append("## Invarianti (non negoziabili)")
    lines.append("")
    for inv in INVARIANTS:
        lines.append(f"- {inv}")
    lines.append("")

    if refs:
        lines.append(f"## Corpus refs ({len(refs)}) — struttura, mai clone")
        lines.append("")
        if stacks:
            lines.append(
                "segnale stack nel campione: "
                + " · ".join(f"{k} {v}" for k, v in list(stacks.items())[:6])
            )
        lines.append(
            "**Valgono per shell, dominio e stack — non per la grafica.** Misurato sul "
            "corpus: zero item con un tratto `splash` o `gradient` onesto, perché i "
            "cataloghi Envato omonimi restituiscono template generici (fedeltà 6% e 0%). "
            "Per splash, fondo di marca e onboarding la fonte è il campo visivo, non un "
            "catalogo di codice: **Figma Community** "
            "(`figma.com/community/mobile-apps`) da aprire **a mano** — il loro robots.txt "
            "vieta la raccolta automatica — oppure Dribbble. Il resto si decide."
        )
        lines.append("")
        for i, r in enumerate(refs, 1):
            tags = "/".join(((r.get("graphic") or []) + (r.get("domain") or []))[:2])
            lines.append(f"{i}. **{r.get('label')}** [{tags}] — {r.get('url')}")
        lines.append("")

    lines.append("## Done quando")
    lines.append("")
    lines.append("1. Ogni asse sopra è **visibile** nell'app finita, non solo nel brief.")
    lines.append("2. Installata sul telefono: **nessun lampo bianco** fra splash e primo schermo.")
    lines.append("3. Il testo regge il contrasto sui **due estremi** del fondo, non solo al centro.")
    lines.append("4. Ogni azione primaria si raggiunge **col pollice**, a schermo pieno e con tastiera aperta.")
    lines.append("5. Il momento di firma si riconosce al primo sguardo, senza spiegarlo.")
    lines.append("6. MEMORY aggiornata: `last_palette_families`, `last_radius_families`, `last_type_voices`, `last_app_backgrounds`, `last_splashes`.")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Seeded randomized mobile web-app creation rules")
    p.add_argument("--seed", default=datetime.now().strftime("%Y%m%d%H"),
                   help="Default YYYYMMDDHH (same clock as motion/craft_axes)")
    p.add_argument("--domain", help="Corpus domain to weight refs: food, fintech, travel, fitness…")
    p.add_argument("--flat", action="store_true",
                   help="Ignora pesi di dominio e affinità estetiche: estrazione uniforme")
    p.add_argument("--activity", help="Attività reale (es. 'consegna a domicilio a Padova')")
    p.add_argument("--refs", type=int, default=24, help="How many corpus refs to list (default 24)")
    p.add_argument("--last-palette", action="append", default=[], help="last_palette_families")
    p.add_argument("--last-radius", action="append", default=[], help="last_radius_families")
    p.add_argument("--last-type", action="append", default=[], help="last_type_voices")
    p.add_argument("--last-shell", action="append", default=[], help="Shell già usate")
    p.add_argument("--last-splash", action="append", default=[], help="last_splashes (MEMORY)")
    p.add_argument("--last-background", action="append", default=[],
                   help="last_app_backgrounds (MEMORY)")
    p.add_argument("--format", choices=("md", "json"), default="md")
    p.add_argument("--batch", metavar="LABELS",
                   help="Comma-separated labels: one recipe each, mutually distinct")
    p.add_argument("--out-dir", type=Path, help="With --batch: write <label>.md per recipe")
    args = p.parse_args()

    corpus = load_corpus()
    labels = [s.strip() for s in args.batch.split(",") if s.strip()] if args.batch else []
    recipes = build_batch(args, labels) if labels else [build(args)]

    payloads = []
    for built in recipes:
        refs: list[dict] = []
        stacks: dict[str, int] = {}
        if corpus:
            refs, stacks = sample_refs(
                corpus, args.domain, max(0, args.refs), built.get("seed", args.seed)
            )
        payloads.append((built, refs, stacks))

    if args.format == "json":
        def payload(b, r):
            return {
                "label": b.get("label"),
                "seed": b.get("seed", args.seed),
                "domain": args.domain,
                "activity": args.activity,
                "choice": b["choice"],
                "conflict_notes": b["conflict_notes"],
                "invariants": INVARIANTS,
                "refs": r,
            }
        out = [payload(b, r) for b, r, _s in payloads] if labels else payload(*payloads[0][:2])
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 0

    for built, refs, stacks in payloads:
        md = render_md(args, built, refs, stacks, corpus)
        if args.out_dir and built.get("label"):
            args.out_dir.mkdir(parents=True, exist_ok=True)
            path = args.out_dir / f"{built['label']}.md"
            path.write_text(md + "\n", encoding="utf-8")
            print(f"written: {path}")
        else:
            print(md)
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
