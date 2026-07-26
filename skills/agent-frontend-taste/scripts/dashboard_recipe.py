#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Seeded 'random' creation rules for a dashboard shell — deterministic per seed.

Kills the default admin look: sidebar + five white KPI cards + one flat table,
no chart, no signature. Every axis below is *picked*, declared and justified
against the corpus (`dashboard_corpus.py`) — never inherited by reflex.

The script proposes; DX/UE/AF still justify each pick against activity, the
corpus signal and MEMORY exclusions (see references/dashboard-rules.md).
It never emits hex: palette comes from locale + register + activity
(craft-rules.md).

Usage:
    uv run scripts/dashboard_recipe.py --domain booking --activity "noleggio bici"
    uv run scripts/dashboard_recipe.py --seed 2026072518 --refs 30
    uv run scripts/dashboard_recipe.py --domain crm --last-shell icon-rail \
        --last-palette asphalt-volt --last-radius soft
    uv run scripts/dashboard_recipe.py --format json
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[1] / "assets" / "dashboard-corpus.json"

# ---------------------------------------------------------------- axes pools

SHELLS: dict[str, str] = {
    "icon-rail": "rail 72–96px solo icone + tooltip; label solo su hover/focus — massima area dati",
    "wide-sidebar-grouped": "sidebar 220–260px con gruppi di sezione (eyebrow + voci), non lista piatta",
    "topbar-workspace": "niente sidebar: topbar con nav primaria + workspace centrato in colonna misurata",
    "rail-plus-context": "rail icone + secondo pannello contestuale per la sezione attiva (filtri/alberatura)",
    "split-master-detail": "lista a sinistra sempre visibile, dettaglio a destra: la riga non apre, seleziona",
    "hub-switcher-rail": "rail + switcher di hub/sede in testa: il contesto operativo è dichiarato in alto",
}

HEADERS: dict[str, str] = {
    "command-bar": "barra sticky con ricerca globale + azione primaria + stato sync",
    "breadcrumb-actions": "breadcrumb di contesto a sinistra, cluster azioni a destra",
    "segmented-tabs": "tab segmentati per vista (oggi / settimana / tutto) sotto il titolo",
    "search-first": "campo ricerca dominante al centro, azioni ridotte a icone",
    "kpi-in-header": "2–3 metriche vive dentro l’header: lo stato prima del contenuto",
    "context-strip": "striscia di contesto (periodo, filtri attivi, conteggio) sempre leggibile",
}

KPI_STYLES: dict[str, str] = {
    "numeric-strip": "riga di numeri senza card: solo hairline di separazione, tabular-nums",
    "card-sparkline": "card con sparkline inline (SVG) sotto il numero: valore + tendenza",
    "hero-metric-minis": "una metrica grande dominante + 3–4 mini metriche satellite",
    "bento-mixed": "bento: celle di dimensione diversa, una ospita un grafico, non 5 card uguali",
    "delta-inline": "numero + delta percentuale inline con segno e colore semantico",
    "gauge-trio": "tre archi/gauge SVG per metriche di saturazione (occupazione, carico, salute)",
}

DATAVIZ: dict[str, str] = {
    "sparkline": "polyline SVG 60×20 senza assi, dentro card o riga tabella",
    "donut-ring": "anello con stroke-dasharray: composizione per stato",
    "stacked-bars": "barre impilate settimanali: volume + mix in una sola lettura",
    "calendar-heatmap": "griglia giorni × settimane con scala di opacità a 4–6 gradini",
    "gauge-arc": "arco 180° con soglia marcata: saturazione o SLA",
    "slope-line": "linea con area sfumata e punto finale etichettato",
    "horizon-bars": "barre orizzontali ordinate: classifica compatta (top N)",
    "progress-rail": "rail di avanzamento con tacche di milestone",
    "funnel-steps": "passi di imbuto con larghezza proporzionale",
    "utilization-grid": "griglia di celle-unità (una per asset) colorate per stato: la flotta a colpo d’occhio",
}

TABLE_PATTERNS: dict[str, str] = {
    "comfortable-hairline": "riga 56–64px, separatori hairline, nessuna zebra",
    "compact-zebra": "riga 40–44px con zebra tenue: densità operativa",
    "grouped-sections": "righe raggruppate per chiave (stato/giorno) con intestazione di gruppo sticky",
    "expandable-rows": "riga che si espande in place con i dettagli secondari",
    "pinned-first-col": "prima colonna sticky, resto scorre in orizzontale su schermi stretti",
    "row-with-inline-chart": "ogni riga porta una micro-visualizzazione (sparkline o barra di utilizzo)",
}

ROW_ACTIONS: dict[str, str] = {
    "icon-only": "icone sempre visibili, aria-label obbligatorio, stopPropagation",
    "hover-reveal": "azioni che compaiono su hover/focus della riga (ma raggiungibili da tastiera)",
    "kebab-menu": "menu a tre punti con popover: poche azioni visibili, il resto raccolto",
    "inline-quick-toggle": "un’azione di stato eseguibile dalla riga (chiudi noleggio, sospendi)",
}

DETAIL_SURFACES: dict[str, str] = {
    "modal-dialog": "dialog centrato: form breve, focus trap nativo",
    "right-drawer": "drawer laterale: il contesto della lista resta visibile",
    "inline-expand": "espansione nella riga: nessun cambio di superficie",
    "split-detail": "pannello di dettaglio fisso a destra, selezione dalla lista",
    "sheet-bottom": "sheet dal basso su mobile, dialog su desktop: una sola logica, due forme",
}

FILTER_PATTERNS: dict[str, str] = {
    "chips-row": "chip di filtro attive e rimovibili, con conteggio risultati",
    "segmented-search": "segmented control per lo stato + ricerca testuale",
    "faceted-panel": "pannello di faccette (stato, tipo, hub) con contatori per valore",
    "saved-views": "viste salvate come tab: 'in ritardo', 'da revisionare', 'oggi'",
    "token-query-bar": "barra query con token (stato:attivo tipo:ebike) e suggerimenti",
}

STATE_TREATMENTS: dict[str, str] = {
    "skeleton-shimmer": "skeleton con shimmer sul primo caricamento, poi crossfade al contenuto",
    "illustrated-empty": "empty state con micro-illustrazione SVG di casa + una sola CTA",
    "hint-rows": "righe fantasma con suggerimento inline al posto del vuoto",
    "zero-to-one": "empty state che precompila un esempio con un click (seed guidato)",
}

EXTRAS: dict[str, str] = {
    "command-palette": "palette ⌘K/Ctrl+K: naviga sezioni ed esegue azioni, con ricerca fuzzy",
    "density-toggle": "toggle densità (comfortable/compact) persistito",
    "bulk-selection": "selezione multipla + barra azioni di massa contestuale",
    "activity-feed": "feed attività recenti con timestamp relativi",
    "status-timeline": "timeline di stato per l’entità (passaggi con orario)",
    "keyboard-shortcuts": "overlay scorciatoie (?) + navigazione righe con ↑/↓",
    "csv-export": "export CSV della vista filtrata (non solo del dataset intero)",
    "quick-add": "quick-add da header/palette: crea senza aprire la sezione",
    "notifications-drawer": "drawer notifiche con non-letti e raggruppamento",
    "map-panel": "pannello mappa/planimetria per asset con posizione",
    "drilldown-panel": "drill-down dal KPI alla lista filtrata che lo spiega",
    "audit-trail": "traccia modifiche per record (chi, quando, cosa)",
}

PALETTE_FAMILIES: dict[str, str] = {
    "asphalt-volt": "grigio asfalto + verde volt: mobilità urbana",
    "steel-copper": "acciaio freddo + rame caldo: industriale, officina",
    "slate-marigold": "ardesia + calendula: operativo caldo, logistica",
    "graphite-cyan": "grafite + ciano tecnico: monitoring, IoT",
    "bone-oxblood": "osso + rosso sangue di bue: editoriale severo",
    "moss-clay": "muschio + argilla: agricolo, outdoor, verde",
    "navy-sand": "blu notte + sabbia: nautico, hospitality costiera",
    "plum-lime": "prugna profonda + lime acido: consumer energico",
    "ink-saffron": "inchiostro + zafferano: culturale, food",
    "concrete-teal": "cemento + verde acqua: civico, sanitario",
    "umber-ice": "terra d’ombra + ghiaccio: finanziario caldo/freddo",
    "olive-ember": "oliva + brace: ristorazione, fuoco",
}

RADIUS_FAMILIES: dict[str, str] = {
    "sharp": "btn 0–2px · box 0–4px — rigoroso, data-dense",
    "soft": "btn 8–14px · box 10–16px — SaaS/product (default di riflesso: motivalo)",
    "rounded": "btn 16–24px · box 16–20px — consumer caldo",
    "pill": "btn 999px · box soft — azioni consumer, chip protagonisti",
    "mixed-signal": "CTA morbida su pannelli sharp — fintech/data",
}

TYPE_TRIOS: dict[str, str] = {
    "grotesk-mono-serif": "grotesque stretto (display) · sans neutra (body) · mono per metriche e label",
    "mono-first": "mono come voce primaria su nav/label/KPI · sans per il corpo · serif solo su titoli di sezione",
    "editorial-serif": "serif d’accento su numeri e titoli · sans tecnica per il corpo · mono per codici",
    "condensed-display": "condensata alta su titoli e KPI · sans larga per il corpo · italic per didascalie",
    "humanist-pair": "sans umanista per corpo e nav · display geometrica sui numeri · mono su ID e timestamp",
}

SURFACE_TEXTURES: dict[str, str] = {
    "rule-lines": "hairline 1px solid come sistema (token --rule) su pannelli e tabelle",
    "rule-lines-dashed": "hairline tratteggiata come grafica di casa, non stato disabled",
    "svg-pattern": "pattern data-URI agganciato al modulo di griglia, peso zero",
    "baseline-rule": "carta rigata sul passo della riga di base",
    "grain": "noise SVG come texture vera, non velo al 3%",
}

DENSITIES: dict[str, str] = {
    "comfortable": "spazi generosi: poche entità, uso occasionale",
    "operational": "densità media: turni di lavoro, molte letture al giorno",
    "dense-pro": "densità alta: molte righe, tastiera protagonista",
}

MOTION_TECHNIQUES: dict[str, str] = {
    "kpi-count-up": "count-up dei numeri all’ingresso (repeat, reduced-motion off)",
    "row-stagger": "stagger righe per indice (40–80ms), non tutte insieme",
    "panel-reveal": "reveal direzionale dei pannelli (mescola direzioni, non solo up)",
    "chart-draw-in": "path del grafico che si disegna (stroke-dashoffset)",
    "drawer-slide": "drawer/sheet con easing di casa e backdrop in dissolvenza",
    "tab-underline-morph": "indicatore dei tab che si sposta invece di apparire",
    "state-crossfade": "skeleton → contenuto in crossfade, non salto",
    "value-flash": "flash breve sulla cella che cambia valore",
}

GRID_LAWS: dict[str, str] = {
    "12-col": "repeat(12, 1fr) + span dichiarati — da motivare, non default",
    "asym-rail": "traccia fissa rail + 1fr: asimmetria cablata su tutte le viste",
}

# Domain-aware weights: {domain: {axis: {value: weight}}}, default weight 1.
# Weights BIAS the seeded draw, they never remove an option (no zero weights):
# the craft knowledge that lived only in the human override downstream — POS is
# dense, analytics leads with charts, finance is sharp — moves into the pick
# while the seed law stays deterministic. `--flat` disables them.
DOMAIN_WEIGHTS: dict[str, dict[str, dict[str, int]]] = {
    "pos": {
        "density": {"dense-pro": 3, "operational": 2},
        "table_pattern": {"compact-zebra": 3, "pinned-first-col": 2},
        "header_bar": {"context-strip": 2, "kpi-in-header": 2},
    },
    "analytics": {
        "kpi_style": {"card-sparkline": 2, "bento-mixed": 2},
        "table_pattern": {"row-with-inline-chart": 3},
        "density": {"operational": 2},
        "type_voices": {"mono-first": 2},
    },
    "crm": {
        "detail_surface": {"split-detail": 2, "right-drawer": 2},
        "filter_pattern": {"saved-views": 2, "token-query-bar": 2},
        "table_pattern": {"comfortable-hairline": 2},
    },
    "booking": {
        "kpi_style": {"gauge-trio": 2},
        "filter_pattern": {"segmented-search": 2},
        "header_bar": {"segmented-tabs": 2},
    },
    "finance": {
        "density": {"dense-pro": 3, "operational": 2},
        "radius_family": {"sharp": 2, "soft": 2, "pill": 1},
        "type_voices": {"mono-first": 2, "grotesk-mono-serif": 2},
    },
    "crypto": {
        "density": {"dense-pro": 3},
        "radius_family": {"sharp": 2, "soft": 2},
        "type_voices": {"mono-first": 3},
    },
    "restaurant": {
        "radius_family": {"rounded": 3, "soft": 2},
        "density": {"comfortable": 2},
    },
    "support": {
        "filter_pattern": {"saved-views": 3},
        "detail_surface": {"right-drawer": 2, "inline-expand": 2},
        "state_treatment": {"hint-rows": 2},
    },
}

# Aesthetic affinities: the palette anchors the register, radius and type tune
# to it. Same contract as mobile_recipe.AFFINITY — >1 favours, <1 disfavours,
# never removes. Baseline before this layer: 6.9% of recipes carried a jarring
# pairing (bone-oxblood with pill CTAs, graphite-cyan with warm rounded chrome).
AFFINITY: dict[str, dict[str, dict[str, float]]] = {
    "bone-oxblood": {
        "radius_family": {"sharp": 3, "pill": 0.3, "rounded": 0.5},
        "type_voices": {"editorial-serif": 3, "condensed-display": 2},
        "surface_texture": {"baseline-rule": 2, "rule-lines": 2},
    },
    "plum-lime": {
        "radius_family": {"pill": 2, "rounded": 2},
        "type_voices": {"condensed-display": 2, "editorial-serif": 0.4},
    },
    "graphite-cyan": {
        "radius_family": {"sharp": 2, "soft": 2, "rounded": 0.4},
        "type_voices": {"mono-first": 3},
        "surface_texture": {"rule-lines": 2, "grain": 0.5},
    },
    "steel-copper": {
        "radius_family": {"sharp": 2, "pill": 0.4},
        "type_voices": {"grotesk-mono-serif": 2},
        "surface_texture": {"grain": 2},
    },
    "navy-sand": {
        "radius_family": {"soft": 2, "rounded": 2},
        "type_voices": {"humanist-pair": 2},
    },
    "slate-marigold": {
        "radius_family": {"soft": 2},
        "type_voices": {"humanist-pair": 2},
    },
    "moss-clay": {
        "radius_family": {"rounded": 2, "soft": 2},
        "surface_texture": {"grain": 2},
    },
    "asphalt-volt": {
        "radius_family": {"sharp": 2, "mixed-signal": 2},
        "type_voices": {"mono-first": 2},
    },
}

# Hard aesthetic clashes, resolved like conflicts (re-pick, declared).
DISSONANCES: list[tuple[str, str, str, str, str]] = [
    ("palette_family", "bone-oxblood", "radius_family", "pill",
     "editoriale severo con CTA pillola: registro rotto"),
    ("palette_family", "graphite-cyan", "radius_family", "rounded",
     "monitoring tecnico con angoli consumer caldi"),
]

# Combos that would say the same thing twice, or contradict each other.
CONFLICTS: list[tuple[str, str, str, str, str]] = [
    ("shell", "split-master-detail", "detail_surface", "split-detail", "shell già in split"),
    ("shell", "topbar-workspace", "filter_pattern", "faceted-panel", "nessuna colonna laterale"),
    ("shell", "rail-plus-context", "filter_pattern", "faceted-panel", "faccette già nel pannello di contesto"),
    ("header_bar", "search-first", "extras", "command-palette", "doppia ricerca dominante"),
    ("kpi_style", "gauge-trio", "dataviz", "gauge-arc", "gauge ripetuto"),
    ("kpi_style", "card-sparkline", "dataviz", "sparkline", "sparkline ripetuta"),
    ("header_bar", "segmented-tabs", "filter_pattern", "saved-views", "doppia striscia di tab"),
    ("shell", "split-master-detail", "table_pattern", "expandable-rows", "dettaglio due volte"),
    ("density", "dense-pro", "table_pattern", "comfortable-hairline", "densità in contraddizione"),
]

INVARIANTS: list[str] = [
    "**light + dark** — stessa `palette_family`, due mappe di token, toggle persistito, entrambi leggibili (mai invert cieco)",
    "**toggle tema = solo icona** (sole/luna) con `aria-label`; nav = icona SVG `currentColor` + label",
    "**riga = azione**: click sulla riga apre/seleziona (`cursor: pointer`), focus da tastiera + Enter/Space; azioni di riga solo icone con `aria-label` e `stopPropagation`",
    "**`font-variant-numeric: tabular-nums`** su ogni cifra in colonna (KPI, tabelle, importi, orari)",
    "**grafici inline SVG**: zero librerie, zero CDN, zero canvas; ogni grafico ha un titolo testuale e valori leggibili",
    "**≥1 grafico vero** e **≤5 KPI**: niente muro di card bianche uguali",
    "**empty state + skeleton** per ogni lista: mai una tabella vuota senza spiegazione",
    "**responsive**: rail/sidebar → orizzontale ≤900px, tabella → colonna sticky o card-list, nessun overflow-x di pagina, target tap ≥44px",
    "**a11y**: `:focus-visible` visibile su tutti i controlli, contrasto AA nei due temi, `prefers-reduced-motion` rispettato",
    "**motion repeat**: i reveal ripartono a ogni ingresso nel viewport (nessun `data-anim-once` se non richiesto)",
    "**hard-reject palette**: purple-indigo AI · cream+serif+terracotta · Inter/system come display",
]

AXIS_ORDER: list[tuple[str, str, dict[str, str]]] = [
    ("shell", "Shell", SHELLS),
    ("header_bar", "Header", HEADERS),
    ("kpi_style", "KPI", KPI_STYLES),
    ("table_pattern", "Tabella", TABLE_PATTERNS),
    ("row_action", "Azioni di riga", ROW_ACTIONS),
    ("detail_surface", "Superficie di dettaglio", DETAIL_SURFACES),
    ("filter_pattern", "Filtri", FILTER_PATTERNS),
    ("state_treatment", "Stati vuoti / caricamento", STATE_TREATMENTS),
    ("palette_family", "Palette family", PALETTE_FAMILIES),
    ("radius_family", "Radius family", RADIUS_FAMILIES),
    ("type_voices", "Voci tipografiche", TYPE_TRIOS),
    ("surface_texture", "Texture di superficie", SURFACE_TEXTURES),
    ("density", "Densità", DENSITIES),
    ("grid_law", "Griglia", GRID_LAWS),
]


POOLS: dict[str, dict[str, str]] = {name: pool for name, _title, pool in AXIS_ORDER}


def rng_for(seed: str, axis: str) -> random.Random:
    """One independent stream per axis: seeds one hour apart must not correlate.

    A multiplicative hash (craft_axes law) is fine for a 6-slot pool but leaves
    visible runs on small pools across adjacent hours — measured: radius_family
    stuck on 2 of 5 values over six consecutive seeds.
    """
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
        # rng.choices consumes randomness differently from rng.choice, so the
        # weighted path only engages when a weight table actually applies —
        # recipes without a domain keep their historical outputs per seed.
        return rng_for(seed, axis).choices(
            candidates, weights=[weights.get(k, 1) for k in candidates]
        )[0]
    return rng_for(seed, axis).choice(candidates)


def pick_many(
    pool: dict[str, str],
    seed: str,
    axis: str,
    n: int,
    exclude: list[str] | None = None,
) -> list[str]:
    excluded = {e.strip() for e in (exclude or []) if e.strip()}
    candidates = [k for k in pool if k not in excluded] or list(pool)
    n = min(n, len(candidates))
    return rng_for(seed, axis).sample(candidates, n)


def resolve_conflicts(
    choice: dict[str, object], seed: str, taken: dict[str, list[str]] | None = None
) -> list[str]:
    """Re-pick the second axis of any conflicting pair; return the notes.

    A single pass left ~1 recipe in 110 with a live conflict (measured on 2000
    seeds): three pairs write to `filter_pattern`, and the later one could hand
    back the value an earlier pair had just banned, since the re-pick excluded
    only the value it was replacing. Same story on the multi-value axes, where
    the spare pool was computed from the current list.

    So: keep a per-axis ban list for the whole resolution, and iterate to a fixed
    point. `taken` carries the batch siblings' spent values: a re-pick that
    ignored them could hand a sibling's axis back to this recipe — measured
    before the fix, 63/800 mobile batches and 100/800 dashboard batches broke
    the mutual-distinctness promise exactly on the conflict-rewritten axes.
    """
    notes: list[str] = []
    taken = taken or {}
    pools = {name: pool for name, _, pool in AXIS_ORDER}
    multi_pools = {"extras": EXTRAS, "dataviz": DATAVIZ}
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
                    pools[b_key], seed, f"{b_key}-swap-{sweep}",
                    exclude=sorted(banned[b_key] | set(taken.get(b_key, []))),
                )
                notes.append(f"`{b_key}` — ripescato, `{b_val}` in conflitto ({why})")
                changed = True
        if not changed:
            break
    return notes


def known_domains(corpus: dict | None) -> list[str]:
    """Domains the corpus can actually weight on."""
    if not corpus:
        return []
    out: set[str] = set()
    for i in corpus.get("items", []):
        out.update(d for d in (i.get("domain") or []) if d != "generic")
    return sorted(out)


def load_corpus() -> dict | None:
    if not CORPUS.exists():
        return None
    with CORPUS.open(encoding="utf-8") as fh:
        return json.load(fh)


def sample_refs(
    corpus: dict, domain: str | None, count: int, seed: str
) -> tuple[list[dict], dict[str, int]]:
    """Domain-matching refs first, then generic filler. Seeded shuffle."""
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
    stacks: dict[str, int] = {}
    for it in picked:
        for s in it.get("stack") or []:
            stacks[s] = stacks.get(s, 0) + 1
    return picked, dict(sorted(stacks.items(), key=lambda kv: (-kv[1], kv[0])))


def build(args, seed: str | None = None, taken: dict[str, list[str]] | None = None) -> dict:
    """One recipe. `taken` holds values already spent by siblings in a batch."""
    seed = seed or args.seed
    taken = taken or {}
    flat = getattr(args, "flat", False)
    domain_w: dict[str, dict[str, int]] = {}
    if args.domain and not flat:
        domain_w = DOMAIN_WEIGHTS.get(args.domain, {})
    exclusions = {
        "shell": args.last_shell,
        "palette_family": args.last_palette,
        "radius_family": args.last_radius,
        "type_voices": args.last_type,
        "surface_texture": args.last_texture,
    }
    choice: dict[str, object] = {}
    harmony: list[str] = []
    # Palette first: it anchors the register the visual axes tune to. Per-axis
    # RNG streams keep the order harmless for every unweighted axis.
    anchor = "palette_family"
    order = [anchor] + [k for k, _t, _p in AXIS_ORDER if k != anchor]
    pools_by_key = {k: p for k, _t, p in AXIS_ORDER}
    for key in order:
        exclude = list(exclusions.get(key, [])) + taken.get(key, [])
        weights: dict[str, float] = {k: float(v) for k, v in (domain_w.get(key) or {}).items()}
        if not flat and key != anchor:
            aff = AFFINITY.get(str(choice.get(anchor, "")), {}).get(key)
            if aff:
                for v, mult in aff.items():
                    weights[v] = weights.get(v, 1.0) * mult
                harmony.append(f"`{key}` ← `{choice[anchor]}`")
        choice[key] = pick(pools_by_key[key], seed, key, exclude, weights=weights or None)
    if domain_w:
        choice["domain_weighted_axes"] = sorted(domain_w)
    if harmony:
        choice["harmony"] = harmony

    counts = rng_for(seed, "counts")
    choice["dataviz"] = pick_many(DATAVIZ, seed, "dataviz", counts.choice([2, 3, 3]))
    choice["extras"] = pick_many(EXTRAS, seed, "extras", counts.choice([3, 4, 4]))
    choice["motion"] = pick_many(MOTION_TECHNIQUES, seed, "motion", counts.choice([2, 3, 4]))

    notes = resolve_conflicts(choice, seed, taken)

    # One signature moment: the axis that must read as deliberate at first glance.
    signature_pool = {
        "dataviz": "il grafico di firma (non un placeholder)",
        "kpi_style": "il modo di dire i numeri",
        "shell": "la forma della shell",
        "table_pattern": "la tabella come strumento",
        "extras": "l’extra che nessun template AI mette",
    }
    choice["signature"] = pick(signature_pool, seed, "signature")
    choice["signature_why"] = signature_pool[str(choice["signature"])]
    return {"choice": choice, "conflict_notes": notes, "seed": seed}


# Sibling dashboards may share invariants, never a silhouette: two apps with
# different palettes but the same shell/header/KPI read as the same product.
DISTINCT_AXES = [
    "shell",
    "header_bar",
    "kpi_style",
    "table_pattern",
    "palette_family",
    "radius_family",
    "type_voices",
]


def build_batch(args, labels: list[str]) -> list[dict]:
    """N recipes that cannot collide on the axes that make the silhouette."""
    taken: dict[str, list[str]] = {k: [] for k in DISTINCT_AXES}
    out: list[dict] = []
    for i, label in enumerate(labels):
        seed = args.seed if i == 0 else f"{args.seed}-{i}"
        built = build(args, seed=seed, taken=taken)
        built["label"] = label
        for axis in DISTINCT_AXES:
            # Keep at least one option free, otherwise the pool starves.
            if len(taken[axis]) < len(POOLS[axis]) - 1:
                taken[axis].append(str(built["choice"][axis]))
        out.append(built)
    return out


def render_md(args, built: dict, refs: list[dict], stacks: dict[str, int], corpus: dict | None) -> str:
    c = built["choice"]
    label = built.get("label")
    lines = [
        f"# Dashboard recipe{f' — {label}' if label else ''} (regole randomiche di creazione)",
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
        lines.append("corpus: **assente** — esegui `dashboard_corpus.py --build` (dichiara il gap)")

    # A domain nobody has is a typo that would otherwise pass for research.
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
    for key, title, pool in AXIS_ORDER:
        val = str(c[key])
        lines.append(f"- **{title}** · `{val}` — {pool[val]}")
    lines.append(
        "- **Data-viz** · "
        + ", ".join(f"`{v}`" for v in c["dataviz"])
        + " — "
        + " · ".join(DATAVIZ[v] for v in c["dataviz"])
    )
    lines.append(
        "- **Extra** · "
        + ", ".join(f"`{v}`" for v in c["extras"])
        + " — "
        + " · ".join(EXTRAS[v] for v in c["extras"])
    )
    lines.append(
        "- **Motion** · "
        + ", ".join(f"`{v}`" for v in c["motion"])
        + " — "
        + " · ".join(MOTION_TECHNIQUES[v] for v in c["motion"])
    )
    lines.append(f"- **Signature** · `{c['signature']}` — {c['signature_why']}")
    if c.get("harmony"):
        lines.append(
            "- **Armonia** · " + " · ".join(c["harmony"])
            + " — assi visivi accordati alla palette (affinità estetiche: bias, mai esclusione)"
        )
    if c.get("domain_weighted_axes"):
        lines.append(
            f"- **Pesi di dominio** (`{args.domain}`) su: "
            + ", ".join(f"`{a}`" for a in c["domain_weighted_axes"])
            + " — bias dichiarato, mai esclusione (`--flat` per l'estrazione uniforme)"
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
        if stacks:
            lines.append("")
            lines.append(
                "segnale stack nel campione: "
                + " · ".join(f"{k} {v}" for k, v in list(stacks.items())[:6])
            )
        lines.append("")
        for i, r in enumerate(refs, 1):
            tags = "/".join((r.get("domain") or [])[:2])
            lines.append(f"{i}. **{r.get('label')}** [{tags}] — {r.get('url')}")
        lines.append("")

    lines.append("## Done quando")
    lines.append("")
    lines.append("1. Ogni asse sopra è **visibile** nel prodotto finito (non solo nel brief).")
    lines.append("2. Gli invarianti passano in **entrambi** i temi, a ~375px e ~1280px.")
    lines.append("3. Il momento di firma si riconosce **al primo sguardo**, senza spiegarlo.")
    lines.append("4. Affiancata all’ultima dashboard consegnata: **non** si somigliano nella silhouette.")
    lines.append("5. MEMORY aggiornata: `last_palette_families`, `last_radius_families`, `last_type_voices`, shell usata.")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Seeded randomized dashboard creation rules")
    p.add_argument(
        "--seed",
        default=datetime.now().strftime("%Y%m%d%H"),
        help="Default YYYYMMDDHH (same clock as motion/craft_axes)",
    )
    p.add_argument("--domain", help="Corpus domain to weight refs: crm, booking, pos, analytics…")
    p.add_argument("--flat", action="store_true",
                   help="Ignora pesi di dominio e affinità estetiche: estrazione uniforme")
    p.add_argument("--activity", help="Attività reale (es. 'noleggio bici a Padova')")
    p.add_argument("--refs", type=int, default=30, help="How many corpus refs to list (default 30)")
    p.add_argument("--last-shell", action="append", default=[], help="Shell già usate (MEMORY)")
    p.add_argument("--last-palette", action="append", default=[], help="last_palette_families")
    p.add_argument("--last-radius", action="append", default=[], help="last_radius_families")
    p.add_argument("--last-type", action="append", default=[], help="last_type_voices")
    p.add_argument("--last-texture", action="append", default=[], help="last_surface_textures")
    p.add_argument("--format", choices=("md", "json"), default="md")
    p.add_argument(
        "--batch",
        metavar="LABELS",
        help="Comma-separated labels: one recipe each, mutually distinct silhouettes",
    )
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
        print(
            json.dumps(
                [
                    {
                        "label": b.get("label"),
                        "seed": b.get("seed", args.seed),
                        "domain": args.domain,
                        "activity": args.activity,
                        "choice": b["choice"],
                        "conflict_notes": b["conflict_notes"],
                        "invariants": INVARIANTS,
                        "refs": r,
                    }
                    for b, r, _s in payloads
                ]
                if labels
                else {
                    "seed": args.seed,
                    "domain": args.domain,
                    "activity": args.activity,
                    "choice": payloads[0][0]["choice"],
                    "conflict_notes": payloads[0][0]["conflict_notes"],
                    "invariants": INVARIANTS,
                    "refs": payloads[0][1],
                },
                ensure_ascii=False,
                indent=1,
            )
        )
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
