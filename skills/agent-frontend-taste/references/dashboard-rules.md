# Dashboard Rules — corpus + regole randomiche di creazione

Come si progetta una dashboard che non sia il template admin di default. Load da DX/UE/AF quando la superficie è `dashboard`. Non è una capability.

Il problema misurato: le dashboard si somigliano più delle landing. Cambiano palette e font, resta la stessa silhouette — sidebar a sinistra, cinque card bianche uguali in alto, una tabella piatta, zero grafici, zero stati vuoti, zero firma. È il velo scuro della hero spostato nel prodotto: un default invisibile.

Due strumenti, in quest'ordine:

| Strumento | Cosa fa | Quando |
|---|---|---|
| `scripts/dashboard_corpus.py` | costruisce/legge il corpus di **centinaia** di template admin reali, con tratti (stack · domain · style) | una volta, poi refresh quando invecchia |
| `scripts/dashboard_recipe.py` | estrae dal seed una **ricetta**: 14 decisioni + data-viz + extra + motion + firma, con invarianti e refs dal corpus | a ogni new shell / restyle sostanziale |

```bash
uv run scripts/dashboard_corpus.py --build --target 700     # ~30 request, poi assets/dashboard-corpus.json
uv run scripts/dashboard_corpus.py --stats                  # tallies del corpus salvato
uv run scripts/dashboard_recipe.py --domain booking --activity "noleggio bici a Padova"
uv run scripts/dashboard_recipe.py --batch "app-a,app-b,app-c" --out-dir _bmad-output/dashboard-recipes
```

**`--build --offline` non tocca un corpus reale già presente** (stesso guard di
`mobile_corpus.py`): se la nuova build produce meno della metà degli item
esistenti, rifiuta e chiede `--force`. Costruito dopo un incidente reale, non
teorico — un probe senza `--out` esplicito ha sovrascritto il corpus committato.

## Minimo non negoziabile

**Ricetta prima della shell (new shell / restyle sostanziale):** genera le decisioni con `dashboard_recipe.py` (seed `YYYYMMDDHH`, `--domain`, esclusioni da MEMORY; `--batch` per varianti sorelle) e dichiarali. Il corpus di riferimento si costruisce con `dashboard_corpus.py`. Il minimo non negoziabile è qui sotto; leve di ricerca misurate, decisioni e invarianti nel resto di questo file.

**Themes — light + dark required**

1. Same `palette_family`, two token maps (`light` / `dark`).
2. Typical: `data-theme="light"|"dark"` on `<html>` + CSS variables; persist toggle (localStorage); optional `prefers-color-scheme` on first load.
3. Both themes must be readable — not blind invert.
4. Scorciatoia (lavoro piccolo): correzione piccola on an already-themed surface → skip full dual theme; new shell → both.

**Chrome**

1. Primary nav: SVG icon + label (`currentColor`; no emoji random).
2. Theme toggle = **icon only** (sun/moon) with `aria-label` — never text-only “Dark/Light”.
3. Tables: round avatar ~32px on name column; smaller for related people.
4. **Edit = whole-row click** (`cursor: pointer` on `tr`); keyboard focus + Enter/Space. No textual “Modifica” button.
5. Row actions = **icons only** (e.g. delete); `stopPropagation`; `aria-label` required.
6. Scorciatoia (lavoro piccolo): micro-copy OK; new shell/table → rules 1–5.

## Corpus — cosa funziona davvero come leva

Misurato 2026-07-25 (rifallo se cambia):

| Superficie | Resa | Nota |
|---|---|---|
| `elements.envato.com/web-templates/admin-templates` + 2 cataloghi sorella | ~48 item ciascuno | canonico |
| `…/admin-templates/{tag}` (22 tag: bootstrap, tailwind, react, dark, minimal, crm, analytics…) | 48 item per tag, **largamente disgiunti** → 560 unici | **la vera leva di ampiezza**; il tag è anche un tratto affidabile |
| `api.github.com/search/repositories` | 100 repo per query | label + descrizione ricche, buone per i domini |
| `all-items?terms=<query>` | 110 item, **ma il termine è ignorato server-side** | stesso set per qualunque query → una sola fetch come filler |
| `?page=N` su Envato | nessun effetto: paginazione client-side | non è una leva |
| ThemeForest (`/category/…`, `/search/…`) | **403** | dichiara il gap, non insistere |

Il corpus non serve a copiare: serve a **pesare**. La ricetta stampa il segnale di stack del campione e sceglie i refs pesati sul dominio richiesto (`--domain crm|booking|pos|analytics|…`), così la direzione si giustifica sul campo reale invece che sul primo Dribbble soft-rounded.

Etica come per `inspire-ops.md`: poche request, UA onesto, niente `/api/*` di Envato, niente mirror di asset.

## La legge randomica (deterministica, non capricciosa)

1. **Seed** `YYYYMMDDHH` — stesso clock di `craft_axes.py`, `hero_copy.py` e del motion. Stessa ora → stessa ricetta; ora dopo → ricetta diversa.
2. **Uno stream RNG per decisione** (`random.Random("<seed>|<asse>")`). L'hash moltiplicativo di `craft_axes` va bene su pool da 6, ma su pool da 5 lascia sequenze visibili: misurato `radius_family` fermo su 2 valori su 5 per sei ore consecutive. Uno stream per decisione decorrela le decisioni e copre il pool.
3. **Esclusioni da MEMORY**: `--last-palette`, `--last-radius`, `--last-type`, `--last-texture`, `--last-shell` togliono dal pool quello che hai appena consegnato. Se il pool si svuota, torna intero (mai bloccarsi).
4. **Conflitti risolti e dichiarati**: coppie che direbbero due volte la stessa cosa vengono ripescate (shell `split-master-detail` + dettaglio `split-detail`; header `search-first` + `command-palette`; KPI `card-sparkline` + grafico `sparkline`; header `segmented-tabs` + filtri `saved-views`; `dense-pro` + tabella `comfortable-hairline`; shell senza colonna laterale + `faceted-panel`). Le sostituzioni finiscono nel blocco «Conflitti risolti» della ricetta.
5. **Batch mutuamente distinto**: con `--batch` le dashboard sorelle **non possono** condividere `shell`, `header_bar`, `kpi_style`, `table_pattern`, `palette_family`, `radius_family`, `type_voices`. Serve quando consegni varianti dello stesso prodotto: è esattamente il fallimento già registrato in MEMORY (palette diverse, stessa impaginazione).
6. **Una firma per dashboard**: la decisione sorteggiata come `signature` è quello che deve leggersi al primo sguardo. Le altre decisioni sostengono, non competono.

**Armonia estetica (2026-07-26):** la palette è l'**àncora di registro** — viene
estratta per prima e le decisioni visive si accordano a lei tramite una matrice di
affinità dichiarata (`AFFINITY`: bone-oxblood → serif editoriale/sharp,
graphite-cyan → mono/rule-lines, plum-lime → condensed/pill…). I pesi favoriscono o sfavoriscono, **mai eliminano**; le
poche coppie davvero stonate sono `DISSONANCES` dure, risolte come i conflitti e
dichiarate. La ricetta stampa la riga **Armonia** con le decisioni accordate;
`--flat` spegne tutto (pesi di dominio e affinità). Misurato: gli abbinamenti
stonati scendono dal 12,2% al 2,2% (mobile) e dal 6,9% all'1,3% (dashboard),
con varietà e determinismo intatti. È gusto codificato in una tabella
ispezionabile, non un punteggio opaco — e non sostituisce la verifica visiva
sul renderizzato.

**Pesi di dominio (2026-07-26):** con `--domain` l'estrazione è pesata (`DOMAIN_WEIGHTS`: pos ↑ dense-pro/compact-zebra, analytics ↑ inline-chart/mono, finance ↑ sharp/mono…). Bias dichiarato nella ricetta, mai un'esclusione, `--flat` per l'estrazione uniforme, determinismo pieno.

La ricetta **propone**. DX/UE/AF confermano o alterano ogni decisione contro `activity`, dominio e corpus — e poi la **dichiarano**. Una decisione non dichiarata è una decisione ereditata per riflesso.

## Decisioni (pool nel codice, non duplicati qui)

`shell` · `header_bar` · `kpi_style` · `table_pattern` · `row_action` · `detail_surface` · `filter_pattern` · `state_treatment` · `palette_family` · `radius_family` · `type_voices` · `surface_texture` · `density` · `grid_law`, più **2–3 data-viz**, **3–4 extra**, **2–4 tecniche di motion** e la **firma**.

Nota su tre decisioni che tornano nel resto della skill: `palette_family` resta soggetta a palette-da-località+attività (`craft-rules.md`), `radius_family` alle famiglie di Chrome geometry, `surface_texture` al ritmo di superficie. La ricetta sorteggia il candidato, la regola generale ha l'ultima parola.

## Invarianti (non sorteggiabili)

Sono stampati in ogni ricetta e valgono sempre: light+dark con due mappe di token e toggle **solo icona**; nav icona SVG + label; **riga = azione** con focus da tastiera e azioni di riga solo icone (`aria-label` + `stopPropagation`); `tabular-nums` su ogni cifra in colonna; **grafici inline SVG** senza librerie né canvas, con titolo e valori leggibili; ≥1 grafico vero e ≤5 KPI; empty state **e** skeleton per ogni lista; responsive (rail → orizzontale ≤900px, tabella con colonna sticky o card-list, nessun overflow-x, target ≥44px); `:focus-visible` e contrasto AA nei due temi; `prefers-reduced-motion` rispettato; motion **repeat**; palette hard-reject (purple-indigo AI, cream+serif+terracotta, Inter/system come display).

Corollario operativo: i grafici si calcolano **dai dati veri** dello stato dell'app. Un grafico con numeri finti è un placeholder, e un placeholder non può essere la firma.

## Procedura

1. Corpus presente e non vecchio (`--stats`); se manca, `--build` o dichiara il gap.
2. Genera la ricetta col dominio giusto e le esclusioni da MEMORY. Su varianti sorelle usa `--batch`.
3. Traduci **ogni** decisione in markup/CSS/JS concreti per quel dominio (es. `utilization-grid` = una cella per asset colorata per stato; `drilldown-panel` = dal KPI alla lista filtrata che lo spiega). Se una decisione non ha senso per il dominio, cambialo **e dichiara perché** — non ignorarlo in silenzio.
4. Verifica i due temi a ~375px e ~1280px, poi affianca la dashboard all'ultima consegnata: se le silhouette si somigliano, il batch o le esclusioni non hanno fatto il loro lavoro.
5. Aggiorna MEMORY: `last_palette_families`, `last_radius_families`, `last_type_voices`, `dashboard_shells`.

## Fallimenti

Sidebar + cinque card bianche + tabella piatta; grafici da libreria o con dati inventati; ricetta generata e poi ignorata («ho tenuto la sidebar perché era già lì»); tre varianti con palette diverse e stessa impaginazione; KPI senza drill-down che spieghi il numero; tabella vuota senza spiegazione; tema scuro ottenuto per inversione.
