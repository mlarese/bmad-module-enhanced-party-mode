# Craft Rules — nucleo (vale per ogni superficie)

Shared non-inferables for DX / UE / AF. Load on invoke. Not a capability.

Qui vive ciò che vale **sempre**: assi, deliverable, soft-gate, responsive,
palette e font, tipografia, composizione, superfici, chrome, batch, motion.

> **Legge dello skill — nessun human in the loop** (`references/autonomia.md`).
> Il flusso **non si ferma mai** per interpellare l'owner:
> niente domande, conferme, menù, scelte «a vista», beat di scoping, attese. Ogni
> ambiguità si chiude con una **decisione dichiarata** in una riga («l'ho letta come X,
> non Y»). Le scelte che un umano avrebbe sciolto passano dal consiglio con i **tre goal**
> (§ *Il consiglio decide — tre goal*). Se qui sotto una regola dicesse «chiedi», vale
> questa: si decide, si dichiara, si va avanti. L'owner corregge di sua iniziativa, e
> allora la sua parola vince.

**Carica anche il file della superficie** (uno solo, quello del job):

| Superficie | File | Cosa aggiunge |
|---|---|---|
| marketing / landing / home | `references/craft-marketing.md` | hero (catalogo · trattamento · copy layout), sezioni dal dominio, gallerie |
| dashboard / admin / product | `references/dashboard-rules.md` | minimo non negoziabile (temi light+dark, chrome) + corpus, 14 assi di ricetta, firma |
| mobile web app / PWA | `references/mobile-rules.md` | minimo non negoziabile (6 assi grafici, manifest, shell) + corpus, 16 assi, craft grafico |

Nucleo + una superficie: mai tutte e tre. Se il job cambia superficie a metà,
carica l'altro file allora, non prima.

## Craft Axes Index

| Asse | Dichiarare | MEMORY | Script / nota |
|------|------------|--------|----------------|
| Palette + fonts | `locale` · **`register`** · `activity` · `palette_family` · **`hue_sector`** · **`ink_family`** · `fonts` | `last_palette_families` · `last_hue_sectors` · `last_ink_families` · `last_font_pairs` · `last_registers` | da luogo + **carattere** + business; verifica con `palette_guard.py` |
| Tipografia sistema | `type_voices` (3 ruoli) · `type_scale` · tracking 2 poli · leading | `last_type_voices` | `craft_axes.py` per la legge di scala |
| Composizione | `grid_system` · `alignment_map` · `bleed_rhythm` · misura `ch` | `last_grid_systems` | `craft_axes.py` seed |
| Superfici | `surface_rhythm` · `surface_texture` · token materiali | `last_surface_textures` | `craft_axes.py` seed |
| Chrome geometry | `radius_family` + `--r-btn/box/chip` | `last_radius_families` | + batch ≥30 corner language |
| Hero archetipo | `hero_archetype` (id del catalogo) | `last_hero_archetypes` | `hero_gallery.py --suggest` — shortlist da seed, scelta tua |
| Hero immagine | `hero_treatment` | `last_hero_treatments` | mai velo scuro full-bleed default |
| Hero copy | `hero_copy` · placement · panel | `last_hero_copy` | `hero_copy.py` seed |
| Sezioni | elenco + perché (1 riga) | — | auto se non istruite |
| Galleria | L→R · gapless · forme · reveal univoci | — | blow-up scroll obbligatorio nel mix |
| Dashboard | light+dark · chrome · 14 assi di ricetta + firma | `dashboard_themes` · `dashboard_shells` | `dashboard_recipe.py` su corpus (`dashboard-rules.md`) |
| Mobile web app | 6 assi grafici (`splash` · `app_background` · `brand_mark` · `onboarding` · `illustration` · `depth`) + 10 di shell · barra sempre visibile | `last_splashes` · `last_app_backgrounds` | `mobile_recipe.py` su corpus (`mobile-rules.md`) |
| Fase implementativa | PRD · architettura (stack **obbligatorio**) · page spec · project context — o analisi autonoma dichiarata | — | `bmad_context.py` (`implementation-handoff.md`) |
| Inspiration | batch ≥30 | — | `hero_sample.py` / inspire-ops |
| Motion | `motion_seed` · `motion_techniques` (2–4) | — | Vera **repeat**; seed `YYYYMMDDHH` |
| Responsive | viewport meta · breakpoints · touch · no overflow | — | **sempre** — desktop e mobile |
| Output demo | path file | `demo_output` | default `{project-root}/frontend-demos/` |

## Deliverable finito (sempre — nessuna eccezione)

Ciò che consegni si legge come una pagina **vera**, non come una bozza da completare. Nel file consegnato **non compare mai** una nota di sostituzione: niente `[INSERIRE …]` · `TODO` · `XXX` · `lorem ipsum` · «testo di esempio» · «sostituire con i dati reali» · commenti HTML/CSS che avvisano · sezione finale con l'elenco dei dati fittizi. Vale per HTML, CSS, JS, spec e README: se una demo dichiara di essere incompleta, non dimostra niente — ed è il primo dettaglio che un cliente finale nota.

I contenuti mancanti si **derivano** (vedi `implementation-handoff.md` §9 *I testi*), non si segnalano. Contatti, prezzi e orari verosimili si scrivono per intero e senza marcatori; **l'onestà sui dati inventati si dice all'owner in chat** — nell'avviso e in una riga alla consegna — non dentro l'artefatto. Preferisci recapiti che non possano appartenere a una persona reale (fasce telefoniche non assegnate, dominio coerente col brand fittizio).

Restano fuori dal riempimento i **fatti che fanno danno se creduti**: certificazioni, premi, partner o clienti reali, riferimenti di legge, dati sanitari, recensioni attribuite a persone esistenti. Lì non si inventa e non si scrive un segnaposto: si progetta la sezione in modo che non richieda quel dato, e lo si dice a voce.

**Lo spec di accompagnamento è un'altra cosa** e non viola questa regola: lì vivono documenti usati, assi dichiarati, casi limite, canone applicato, requisiti lasciati al backend. Quello che non vive **da nessuna parte** è l'elenco dei dati fittizi — sta nella conversazione. Confine completo in `implementation-handoff.md` §10 *Due artefatti, due regole*.

Fallimento: `TODO` nel file consegnato; blocco «dati da sostituire» in coda alla pagina o allo spec; `lorem ipsum`; una certificazione inventata.

## La via breve: kernel + slice (default sui lavori nuovi)

Le fasi BMAD complete costano più di quello che proteggono su una pagina. Comprimile in **un artefatto e una fermata**:

1. **Ricerca** (dominio, marketing, servizi dal sito) — nessuna fermata, è il tuo mestiere.
1b. **Il consiglio valuta gli input e scioglie le ambiguità prima di decidere (G1):** **la richiesta stessa dell'owner**, ricerca di dominio e di marketing, PRD, architettura e documento di architettura, project context, spec già consegnati. Richiesta ambigua → si sceglie la lettura più probabile e la si **dichiara** nel kernel («l'ho letta come X, non Y»), non si torna con una domanda. Nello stesso giro si chiudono **superficie**, **`register`**, **perimetro** e **stack** quando non sono dichiarati da nessuna fonte. Chi produce la ricerca non la valida. Per giurisdizione (evidenza → Mary, deployabilità → Rex, WordPress → Niki, dati personali → Jane, claim → Elena, prezzi → commercialista, buchi → Murat). I documenti **restano vincolanti**: la valutazione dice quanto coprono e dove tacciono. Buco → decide e dichiara (varianza); contraddizione → vince la precedenza, il conflitto è varianza; dato sbagliato di fatto → si segnala in consegna; ricerca insufficiente → **si rifà**, unico caso in cui il lavoro torna indietro, con **tetto di cinque rimandi** (ogni rimando nomina cosa manca; al quinto si **decide con l'evidenza migliore**, si dichiara quale delle tre cose mancava — domanda mal posta · fonti inesistenti · dato che solo l'owner ha — e si scrive la varianza: il lavoro esce comunque). Verdetto: una riga per input dentro il kernel.
2. **G2 — cosa si costruisce, in consiglio.** Il ramo lo decide G1 e lo dichiara. **Ramo A (landing, pagina singola, solo front-end):** `bmad-party-mode --non-interactive` con goal «decidi perimetro, servizi, flusso di conversione, sezioni, stack, vincoli, non-obiettivi e `slice_plan`; nessuna domanda all'owner» — **kernel a 5 campi, che sostituisce PRD + UX spec + architettura**. **Ramo B (progetto con back end e front end: auth, dati che persistono, back office, API, ruoli, più superfici):** un **solo goal** che produce i quattro documenti veri — PRD · UX/page spec · architettura · `project-context.md` — più la `slice_plan`, con i workflow BMAD come **stampo, non come flusso** (invocarli uno per uno apre porte da cui il lavoro esce a chiedere: `bmad-generate-project-context` si ferma a ogni step per costruzione). Disciplina: `implementation-handoff.md` §4.0. In entrambi i rami il consiglio decide *cosa* sta in pagina e *perché*; **il craft non si vota** (palette, font, hero restano tuoi). Fatti verificati e **assunzioni** restano separati e marcati — vale anche per i documenti che ti sei scritta da sola, che vincolano come gli altri. L'esito si **dichiara** all'owner in una battuta — non è una richiesta di conferma e non blocca.
3. **`slice_plan` verticale** — ogni slice end-to-end e consegnabile da sola. Sito: **S1 landing** → **S2 back office** (accesso minimo reale + la schermata che gestisce ciò che la landing produce) → S3+. Dashboard/app: **S1 una schermata che fa una cosa vera con l'accesso che serve a farla** → **S2 auth completa** → S3+. Mai auth completa come S1; mai aprire una slice prima che la precedente sia consegnata e vista.
3b. **Lo stesso consiglio approva il risultato (G3)** (`--non-interactive`, goal «approva o rifiuta contro kernel, documenti vincolanti e craft-rules»): **approvabile se soddisfa tutte le richieste dei documenti BMAD + craft-rules**, anche se qualcuno l'avrebbe fatto diversamente — il gusto non è un veto, e ogni rifiuto deve **nominare** la richiesta mancante. **Tetto di cinque rifiuti** per deliverable (la stessa richiesta non ne motiva due; al quinto si consegna dichiarando cosa resta scoperto, come varianza): un consiglio che rifiuta all'infinito è un ciclo che non termina, e senza fermate sull'owner nessuno lo interrompe. Parla chi ha giurisdizione (form → Jane, prezzo → commercialista, claim → Elena, WordPress → Niki, hosting → Rex, motion → Vera); chi non ce l'ha tace. Vale come la review avversaria, non in aggiunta.
4. **Ogni slice diventa una spec eseguibile** — `bmad-spec` in **headless** (nessuna domanda, express), slug per slice `<progetto>-s<N>-<nome>`, Ready for Development (task con path, AC in Given/When/Then, zero TBD), ~900–1600 token **contati sul contratto applicativo**: gli assi di craft stanno nel DESIGN/spec di accompagnamento e la spec li referenzia, non li duplica. Le `open_questions[]` dell'express **si chiudono nello stesso giro** (decisione + assunzione marcata + varianza): una spec con domande aperte non è pronta, e quelle domande non hanno nessuno a cui andare. Il kernel — o i quattro documenti — è la **fonte** che le vincola tutte. Se sfora davvero, quasi sempre erano **due** slice.
5. **Implementazione:** tu la pagina (AF → Vera) **e** la parte applicativa di quella spec (endpoint, persistenza, auth di slice), con la **disciplina di `bmad-quick-dev`** — `spec-template.md`, standard Ready for Development — **senza invocarlo**: quel workflow si ferma a chiedere in ogni ramo (`autonomia.md` → *I workflow che si fermano si usano come stampo*). Se lo lancia l'owner, si esegue com'è. A consegna fatta la spec resta in `implementation-artifacts/` e vincola la slice dopo; si aggiorna ri-derivandola sullo stesso slug, mai a mano. Dettaglio: `implementation-handoff.md` §4.2.

**Non è un flusso nuovo:** sono i workflow BMAD chiamati a pezzi — `bmad-spec` **invocato** per il kernel e le spec di slice; `bmad-quick-dev`, `bmad-prd`/`bmad-ux`/`bmad-architecture`, `bmad-create-story`/`bmad-code-review` usati come **stampo** dentro il flusso, perché hanno checkpoint e invocarli lo fermerebbe. **Si sale di peso, non si parte pesanti.**

**Le varianze si scrivono in `docs/varianze/YYYY-MM-DD-<slug>.md`** — cinque righe: atteso · deciso · perché · tipo (deviazione | assunzione da verificare | conflitto risolto) · scadenza. Si scrive solo dove tra sei mesi qualcuno chiederebbe «perché qui è così?»: assunzioni entrate in pagina, deviazioni da convenzioni, conflitti risolti, scelte contro un default dei craft-rules. Mai dentro il deliverable. Il pre-flight le rilegge **per prime**.

**Le indicazioni del progetto si leggono, non si gestiscono:** `CLAUDE.md` / `AGENTS.md` (stack, convenzioni, vincoli) sono la prima fonte da consultare — li mantiene il progetto, non tu. Se non le dicono → leggi i **documenti chiarificatori** in `docs/` e README (il pre-flight li elenca, ordinati per rilevanza) **prima** di dedurre lo stack dai file. Ambiguo → **decide G1** e la decisione si dichiara nel kernel + varianza; nessuna domanda, nessuna riga scritta nei file di configurazione del progetto.

La via breve vale sul **ramo A** (landing, pagina singola, solo front-end). Sul **ramo B** — back end e front end, progetto vivo e multi-pagina, dominio regolato, o richiesta esplicita dell'owner — si producono i quattro documenti (sempre in un solo goal, sempre senza fermate). Se PRD/architettura esistono già non si rigenerano: vincolano. Disciplina: `implementation-handoff.md` §§1-6 (il flusso) e §15 (quando non usarla).

## Il consiglio decide — tre goal (nessuna domanda, mai)

Ogni scelta che un umano avrebbe sciolto passa da qui. Il consiglio gira sempre
`bmad-party-mode --non-interactive` e **decide**: un consiglio che restituisce una
domanda ha fallito il goal, e il goal si rilancia — non si gira la domanda all'owner.
Testo integrale dei tre goal: `references/autonomia.md`.

| Goal | Quando | Decide |
|---|---|---|
| **G1 — Lettura** | dopo il pre-flight e la ricerca, prima del kernel | superficie · `register` · perimetro reale · stack non dichiarato · precedenza fra fonti in conflitto · ogni punto ambiguo della richiesta. Per voce: decisione + una riga di motivo + `fatto \| assunzione` |
| **G2 — Cosa si costruisce** | prima del codice | **ramo A** (landing / solo FE): kernel a 5 campi + `slice_plan`. **ramo B** (BE + FE: auth, dati, back office): i quattro documenti — PRD · UX/page spec · architettura · `project-context.md` — in **un solo goal**, mai invocando i workflow uno per uno |
| **G3 — Approvazione** | prima di consegnare | approva se soddisfa **tutte** le richieste dei documenti + craft-rules; ogni rifiuto nomina la richiesta mancante; **max 5 rifiuti**, poi si consegna dichiarando cosa resta scoperto |

**Entrambi i cicli interni hanno tetto cinque** — rimandi della ricerca (G1) e rifiuti in approvazione (G3) — e la stessa via d'uscita: si decide, si consegna, si dichiara cosa resta aperto come varianza. Tolte le fermate sull'owner, l'unico modo che resta a un flusso per non terminare è girare su sé stesso. Una **regressione** non conta come rifiuto ripetuto; due andate e ritorni fra due richieste incompatibili si chiudono scegliendo quale cede (varianza).

**Il ramo si promuove, mai il contrario:** quando una slice introduce il back end — auth reale, dati che persistono, API, ruoli, pagamenti — **prima** di aprirla si producono i quattro documenti, e da lì in poi il lavoro è ramo B, S3 compresa. Il kernel non si butta: diventa input del PRD. La promozione la dichiara G1 ed è una varianza (`implementation-handoff.md` §4.0).

**Prima di invocare un workflow BMAD, guarda se si ferma** (`HALT`, «ask the human», «user must approve»): se ha un checkpoint sul percorso che useresti, non si invoca — se ne prende il **formato** e il lavoro lo fa il consiglio o tu. Elenco verificato in `autonomia.md`.

Su lavori piccoli i tre goal stanno in una chiamata sola, ma l'ordine resta: prima si
legge, poi si decide, poi si approva.

**Il craft non si vota.** Palette, tipografia, hero, griglia, superfici e motion restano
tuoi: il consiglio decide *cosa* sta in pagina e *perché*, mai *come appare*. Le scelte
di craft che prima erano «a vista dell'owner» — hero archetype, effetto motion — le
prendi tu da seed deterministico con le esclusioni di MEMORY, e le dichiari.

## Il sito esistente del cliente (quando c'è)

Fonte di **contenuto**, mai di **design**. Le due cose non si toccano:

- **Contenuto — si prende.** Immagini (le sue foto valgono più di qualunque stock: si usano quelle, se ci sono e sono usabili), servizi e offerta reali, nomi, fatti, recapiti. Se l'owner non elenca cosa offre, lo si **verifica sul sito e lo si ripropone** — riorganizzato e raccontato meglio, non sostituito con servizi inventati.
- **Design — non si guarda.** Layout, palette, tipografia, hero, ritmo delle sezioni restano derivati da `locale` · `register` · `activity` e dal batch ≥30, come su un progetto nuovo. **Se il risultato somiglia al sito vecchio, il lavoro non è stato fatto**: il cliente lo rifà proprio perché quello che ha non gli basta.
- **Il marchio è un vincolo, non è il design del sito:** logo, nome e colori di brand documentati si rispettano e si dichiarano; il layout no.

Disciplina completa (immagini, diritti, servizi obsoleti, precedenza delle fonti): `implementation-handoff.md` §8 *Il sito esistente del cliente*.

## Soft-gate (canonico)

**Micro-edit** = copy, un colore, un bug, un componente isolato su UI già craftata. Su micro-edit: **skip** AW batch ≥30, `hero_copy.py`, `craft_axes.py`, rifacimento griglia / ritmo di superficie, espansione sezioni, dual-theme completo, Vera (salvo l’ask sia motion). **New craft / restyle sostanziale / nuova landing / nuova shell dashboard** → regole complete sotto. Owner «niente animazioni» → skip Vera. Soft-gate non autorizza stub solo-hero né palette generica. **Responsive non è soft-gateable:** ogni sito/pagina consegnata deve funzionare su desktop e mobile.

## Responsive (sempre — desktop e mobile)

Ogni landing, page o shell che AF consegna **deve** essere responsive. Non è un’opzione né un “poi”: è criterio di done. Soft-gate non lo sospende.

1. **Viewport:** `<meta name="viewport" content="width=device-width, initial-scale=1">` obbligatorio su ogni HTML.
2. **Layout fluido:** griglie (`asym-rail`, `fine`, `12-col`, hero split, gallery) **collassano** sotto breakpoint — tipicamente ≤820–900px → una colonna / stack. Rail verticale → orizzontale. Niente layout a due colonne “schiacciate” su telefono.
3. **Tipografia e misura:** `clamp` / unità relative; headline e body restano leggibili (≥16px body effettivo su mobile). `max-width` in `ch` sì; overflow orizzontale del testo **vietato**.
4. **Media:** immagini e iframe (mappe) `max-width: 100%`; hero media con altezza sensata su mobile (`min-height` in `svh`, non 100vh bloccato). Gallery mosaico: su mobile track semplificata (es. 2 col o stack) **senza buchi** e senza overflow.
5. **Nav / chrome:** menu che non esce dallo schermo; CTA tap-friendly (target ≥44px circa); niente hover-only come unica via d’azione.
6. **No overflow-x di pagina:** `100vw` + padding non deve generare scrollbar orizzontale (compensa con `min(…)` / `calc` / `overflow-x: clip` sul contenitore se serve un full-bleed).
7. **Verifica prima di chiudere AF:** ridimensiona / pensa mobile (~375) e desktop (~1280). Se il brand-test passa solo su desktop → fallimento.
8. Fallimento: sito solo-desktop; testo tagliato; griglia a N colonne senza media query; mappa o gallery che sforano; viewport meta assente.

## Palette + fonts (always — da luogo + carattere + business)

**Tre segnali, non due.** Il luogo da solo non basta: Cortina è un hotel a cinque stelle *e* un rifugio dove si mangia in dieci al tavolo, e le due cose non possono uscire con la stessa palette e lo stesso font. Il segnale che decide il **registro** è il carattere.

1. Read MEMORY/BOND for `last_palette_families`, `last_font_pairs`, `last_registers`.
2. Inferisci i tre segnali e **dichiarali**:
   - **`locale`** — città / regione / clima / materialità: mare, montagna, metropoli, campagna, lago, borgo storico. Dà la **materia** (pietra, legno, neve, salsedine, cemento, terra) e la luce.
   - **`register`** — il **carattere** dell'attività: `luxury` · `alta gamma sobria` · `famigliare` · `popolare / quotidiano` · `artigianale / materico` · `istituzionale / autorevole` · `giovane / energico` · `clinico / tecnico` · `romantico` · `minimal rigoroso`. È il segnale che comanda il tono: **stesso luogo + carattere diverso = palette e font diversi**, sempre.
   - **`activity`** — la **tipologia di business** concreta: ristorante, trattoria, hotel, spa, studio legale, e-commerce, SaaS, clinica, palestra, cantina. Dà gli oggetti e i vincoli funzionali (menù, prenotazione, catalogo, dashboard).
3. **Deriva** `palette_family` + 4–6 hex **e** le voci tipografiche dall'incrocio dei tre — mai da un default generico "bello". Come pesano:
   - il **luogo** dà la famiglia cromatica e la materia;
   - il **carattere** dà saturazione, contrasto, profondità e il registro tipografico;
   - il **business** dà quanti colori funzionali servono (stati, CTA, categorie) e la leggibilità richiesta.
4. **Il carattere sul colore** (logiche aperte, non lista chiusa): `luxury` → gamma stretta, scuri profondi, un solo metallo caldo, saturazione bassa e contrasto alto; `famigliare` → medi caldi, legno/pane/terracotta ragionata, contrasto morbido, nessun nero puro; `popolare` → colori pieni e diretti, accento vivo, poca sofisticazione; `artigianale` → terre, ossidi, sporcature, neutri non perfetti; `clinico` → freddi desaturati, bianchi netti, accento singolo; `giovane` → accento acido su base neutra, contrasto netto.
5. **Il carattere sul font:** `luxury` → didone / serif ad alto contrasto o grotesque stretta, tracking negativo deciso; `famigliare` → umanista o rounded, contrasto basso, leading generoso; `popolare` → grottesca condensata o slab, pesi alti; `artigianale` → serif old-style, incise, un italic vero come terza voce; `istituzionale` → transizionale o serif editoriale; `clinico` → neo-grotesque + mono come voce dati.
6. **Esempi d'incrocio** (aperti, e deliberatamente sparsi sulla ruota — non prenderli come catalogo): Cortina + `luxury` + hotel → obsidian/firn/**bronzo** desaturati + serif alto contrasto; Cortina + `famigliare` + rifugio → **legno/mattone/panna caldi** + umanista rounded; Milano + `luxury` + notte → obsidian/champagne + Bodoni-like; costa + `famigliare` + trattoria → **sabbia/cotto/bianco calce**, non il teal da boutique hotel; Bologna + `popolare` + osteria → **porpora/ocra/gesso**; product + `clinico` + SaaS → graphite + neo-grotesque + mono. Il verde-pineta e il teal-laguna sono scelte legittime, non la traduzione automatica di «luogo italiano».
7. Famiglia **diversa** dalle ultime in MEMORY; e **stesso `register` due volte di fila → cambia comunque famiglia**, altrimenti tutti i luxury diventano lo stesso sito nero e oro. Hard-reject: purple-indigo AI · cream `#F4F1EA`+serif+terracotta · Inter/system display.

### Il settore cromatico, non il nome (anti-ripetizione vera)

Misurato sulle demo consegnate: `laguna-pino` · `abete-rame` · `euganeo-zafferano` · `adriatico-corallo` · `concrete-teal` sono **nomi tutti diversi** — quindi il controllo al punto 7 passava ogni volta — ma cadono nello **stesso settore di tinta**. Il nome non è il colore: l'occhio vede l'hue.

1. **Classifica la palette per settore**, non per etichetta:

| Settore | Hue | | Settore | Hue |
|---|---|---|---|---|
| rosso | 345–15 | | teal/ciano | 165–200 |
| terra/arancio | 15–45 | | blu | 200–260 |
| giallo/ocra | 45–70 | | viola | 260–300 |
| verde | 70–165 | | magenta/rosa | 300–345 |

Neutro = **croma ≤ 4** — sotto quella soglia non resta tinta da nominare (la saturazione da sola inganna sugli scuri: vedi *Lo scuro è un asse*). Il **settore dominante** è quello dei due colori che coprono più area (fondo e scuro strutturale), non quello dell'accento.

2. **Vietato ripetere il settore dominante per 3 job consecutivi.** In MEMORY vive `last_hue_sectors` accanto a `last_palette_families`: il nome serve a te, il settore serve all'occhio.
3. **Verificalo, non fidarti del nome che gli hai dato:** `uv run scripts/palette_guard.py --check <file>` (o `--hex …`) stampa settori, saturazioni e violazioni. Su new craft è parte del check di chiusura, come il responsive.

### Lo scuro è un asse, non un residuo

Il difetto misurato non era l'accento — quelli erano diversi ogni volta — ma `--ink`: **verde o teal in 6 demo su 9**, con saturazioni fino al 66%. Conta perché lo scuro riempie le superfici **grandi** (hero scura, fasce `dark` del `surface_rhythm`, footer): l'accento vive su pochi pixel, lo scuro su mezza pagina. Una palette «euganeo-zafferano» con l'ink verde **legge come sito verde**.

1. **Dichiara `ink_family:`** — `neutro` (croma ≤ 4) · `caldo` (hue 15–60) · `freddo` (hue 180–260) · `virato-accento` (qualunque altra tinta).
2. **Tetto di croma sulle superfici grandi:** ogni fondo scuro (L ≤ 30%) che copre una sezione intera, la hero o il footer sta **entro croma 6**.
   Si misura il **croma percepito** — `saturazione × (1 − |2L − 1|)` — non la saturazione grezza: a L=5% una S del 17% è nero, a L=27% la stessa cifra è verde evidente. Tarato sulle demo consegnate: i neutri veri stanno a 1,6–3,1, mentre `#1A2A22` — il verde che riempiva una hero e faceva leggere verde tutta la pagina — sta a 6,2. Sopra soglia non è «nero di marca»: è un colore pieno, e a mezza pagina domina tutto il resto. Ammesso come **scelta dichiarata**, su **una** sola superficie.
3. **Lo scuro segue il `register`:** `famigliare` · `artigianale` · `popolare` → scuri **caldi** (bruno, seppia, ombra bruciata, testa di moro); `clinico` · `minimal` → freddi desaturati; `luxury` → profondo quasi-neutro con una sola vibrazione. Un'osteria famigliare con l'ink verde-bosco ha il carattere contraddetto dalla superficie più grande della pagina.
4. **Non far coincidere ink e accento di settore:** se l'accento è verde, lo scuro non è verde — altrimenti la pagina ha una tinta sola in due luminosità.
5. Dopo approve: MEMORY `last_ink_families` oltre a `last_hue_sectors`.
6. Fallimento: `ink_family` non dichiarato; scuro strutturale sopra S 15% non dichiarato; footer e hero della stessa tinta dell'accento; tre job di fila nello stesso settore.

8. Dichiara in direzione: `locale: …` · `register: …` · `activity: …` · `palette_family: …` · **`hue_sector: …`** · **`ink_family: …`** · `fonts: Display + Body (+ terza voce)` · `radius_family: …` · perché — una riga che leghi i tre segnali all'esito, non etichette scollegate.
9. Dopo approve: aggiorna MEMORY (`last_palette_families`, **`last_hue_sectors`**, **`last_ink_families`**, `last_font_pairs`, `last_registers`, `last_hero_treatments`, `last_hero_copy`, `last_radius_families`).
10. **Il `register` non si sorteggia mai da seed.** Composizione, superfici e hero si estraggono apposta, per varietà; il carattere no: è un **fatto del business**, non una variabile estetica. Un seed che decide "luxury" per una trattoria produce una pagina coerente con sé stessa e falsa rispetto al cliente. Il carattere viene dal brief, dal dominio, dal sito del cliente o da **G1** — mai da `craft_axes.py`, mai da una domanda.
11. **Se è ambiguo lo decide G1, e tu lo dichiari — non lo chiedi.** Quando le due letture darebbero design **opposti** (famigliare vs luxury, artigianale vs clinico) la questione va al consiglio con l'evidenza raccolta (dominio, luogo, prezzi, tono del sito, clientela), e il verdetto entra nel kernel: «l'ho letto come famigliare, non luxury — perché ‹riga di motivo›». Negli altri casi decidi da sola e dichiara. Sbagliare `register` è l'errore più caro del set — non si corregge cambiando un font, si rifà tutto — ed è **esattamente** per questo che si decide sull'evidenza e si scrive la riga: una lettura sbagliata dichiarata si vede subito, una domanda costa un giro sempre.
12. Fallimento: `register` non dichiarato; luxury e famigliare della stessa categoria che escono identici; carattere dichiarato e poi contraddetto dal colore (una trattoria "famigliare" in nero/oro); carattere estratto da seed.

## Sistema tipografico (oltre la coppia)

La coppia display+body è il minimo, non il sistema: due nomi di font non fanno una voce. Nei siti premiati la tipografia è una **legge** (scala, tracking, leading) su **tre voci**. Senza quella legge ogni landing eredita gli stessi eyebrow maiuscoli e lo stesso `clamp()` di riflesso, qualunque sia la coppia.

1. **Dichiara `type_voices:` — tre famiglie con ruolo fisso:** display · body · **terza voce** (`mono` | italic dedicato | serif d’accento). La terza voce ha un compito semantico (didascalia, dato, citazione, label), non è decorazione. Due sole famiglie solo se il vincolo di brand è dichiarato — mai per omissione.
   - Il **mono può essere voce primaria** (label, metriche, nav, eyebrow), non “il font del codice”.
2. **Dichiara `type_scale:` come legge, non come lista:** base a 1200px + ratio + **ampiezza fluida differenziata** — display `max ≈ min × 1.5`, body `max ≈ min × 1.2–1.25`. Il display respira, il testo di lettura no.
3. **Tracking a due poli (obbligatorio):** display da `-0.03em` a `-0.06em`, più negativo al crescere del corpo; eyebrow/label `+0.10em`…`+0.18em` con uppercase. Un solo valore di tracking su tutta la pagina = fallimento.
4. **Leading per registro:** display `0.80–0.95`, body `1.35–1.50`. Nessun display sopra `1.1` salvo scelta dichiarata (serif culturale ariosa).
5. **`font-variant-numeric: tabular-nums`** su ogni cifra in colonna: tabelle, KPI, prezzi, timer, contatori. Su dashboard è parte delle regole tabella.
6. **`text-wrap: balance`** sulle headline, `pretty` sui paragrafi. `hyphens: auto` solo con misura corta.
7. `hero_treatment: type-first` → display in **unità viewport nude** (`8–24vw`), non `clamp`: il clamp protegge il testo che deve restare leggibile, il vw dichiara che quel testo è una superficie.
8. **Vietato `clamp(x, …, x)`** con estremi uguali (fluidità finta, token dump da design tool): se non scala, scrivi il valore fisso.
9. Fallimento: due famiglie e solo pesi 400/700; stesso tracking su titolo ed eyebrow; `line-height: 1.5` globale; numerali proporzionali in tabella.

## Composizione — griglia, allineamenti, misura (sempre su new craft)

Il problema misurato: due landing con palette, font, `radius_family` e hero **diversi** possono avere la stessa impaginazione — stesso container centrato, stesso `text-align: left` su tutto, stesso ritmo verticale. È il modo più probabile in cui i progetti si somigliano, perché la silhouette pesa più del colore.

1. **Dichiara `grid_system:`** prima del layout:

| `grid_system` | Come | Quando |
|---|---|---|
| `fine` | `repeat(24–36, 1fr)` + placement esplicito (`grid-column: 6/16`) | editorial, brand, luxury, culturale — l’off-center diventa una misura, non un occhio |
| `asym-rail` | traccia fissa `12–22vw` (o `rem`) + `1fr` | rail di metadati/nav laterale; asimmetria cablata, quindi coerente su tutte le sezioni |
| `12-col` | `repeat(12, 1fr)` + span | product/dashboard — **da motivare**, non è il default |

2. **Almeno 2 blocchi per pagina con `grid-column: <start>/<end>` esplicito** (start ≠ 1 oppure end ≠ -1). Se tutta la pagina è `span N`, l’off-center non esiste: è un template.
3. **Dichiara `alignment_map:`** sezione per sezione (es. `hero left · storia rail-right · statement center · gallery full-bleed · footer split`).
   - Stesso allineamento su **tutte** le sezioni = fallimento.
   - **Centratura: massimo 2 sezioni**, e solo su statement o CTA finale. Centrare tutto azzera la forza della centratura.
   - `justify-self: start|end|center` **mescolati** dentro la stessa griglia: ogni blocco si aggancia al bordo che gli serve.
   - Il **destra-allineato è un registro reale** per metadati, anni, numeri di sezione, contatti — mai per il corpo.
4. **Misura su due registri in `ch`:** headline `10–20ch` (2–3 parole per riga, ragged progettato), body `55–68ch`. Nessun testo eredita la larghezza del contenitore.
5. **Dichiara `bleed_rhythm:`** — `contained` (rail rigoroso, full-bleed solo per media) oppure `alternating` (fasce `100vw` alternate a blocchi in colonna) — e tienilo per tutta la pagina. Margini derivati dai token di griglia (`calc(var(--grid-gap) …)`), non da `max-width: 1200px; margin: auto`.
6. **`subgrid`** su liste di card con testo di lunghezza variabile: titoli e footer si allineano davvero, non a occhio.
7. **`aspect-ratio` scelto**, non solo `16/9` e `1/1`: rapporti come `4/5`, `1/1.2`, `9/16`, `351/442` sono parte della composizione.
8. Rail verticale: `writing-mode: vertical-rl` su label/numero di sezione giustifica un margine largo — usalo se il rail esiste, non come decorazione.
9. Soft-gate: micro-edit → non rifare la griglia. Fallimento: container centrato + 12-col mai usata davvero + tutto left; oppure hero, header di sezione e CTA tutti centrati.

## Superfici — ritmo, texture, luce (dalla sezione 2 in poi)

`hero_treatment` governa **solo il primo viewport**: sotto, senza regola, arrivano sei sezioni di tinta piatta con card bianche. È lo stesso riflesso del velo scuro, spostato più in basso.

1. **Dichiara `surface_rhythm:`** come sequenza di fondi (es. `paper → dark → paper → full-bleed media → paper`): **cambio di chiave tonale ogni 2–3 sezioni**. Implementalo con `data-theme` **sulla sezione**, non con override di colore sparsi. Light/dark non è solo un toggle utente: è ritmo di pagina (temi d’accento di sezione ammessi).
2. **Dichiara `surface_texture:` — una sola texture di casa** (max due, mai zero):

| `surface_texture` | Come |
|---|---|
| `rule-lines` | hairline `1px solid` **o `1px dashed`** come sistema, token `--rule`; il tratteggio è grafica, non stato disabled |
| `svg-pattern` | data-URI ripetuto con `background-size` agganciato al modulo di griglia (`1rem`, `18px`, `4rem`) — peso zero |
| `baseline-rule` | `background-size: 100% <line-height>px` + `repeat-y`: carta rigata col passo della riga di base |
| `grain` | `feTurbulence` / noise — texture vera, non un velo al 3% su tutto come alibi |

3. **Luce con raggio dichiarato:** `radial-gradient(circle at X Y, <accento>, transparent 8–15rem)`, oppure una forma colorata con `blur(20–30px)` **dietro** il contenuto. Vietato il gradiente lineare a tutta pagina come fondo di sezione; vietato `backdrop-filter` come risposta a ogni pannello. **Unica eccezione dichiarata:** il fondo di marca di una **web app mobile** (superficie continua della shell, non sezione di landing) — perimetro e regole tecniche in `references/mobile-rules.md` → Fondo d'app. Su landing il divieto resta pieno.
4. **Token di superficie nominati per materiale:** `--bg-paper`, `--bg-dirty-white`, `--bg-inv` + 1–2 fasce di color-blocking derivate da `palette_family`. L’off-white è un token dichiarato, mai `#f8f9fa` di riflesso.
5. **Un angolo di gradiente di casa** (uno, es. `135deg`) riusato, più al massimo una deviazione dichiarata. **Scala di opacità** a 4–6 gradini fissi (`.08 .2 .4 .6 .8`), non valori inventati per occorrenza.
6. Testo che scorre sopra fondi che cambiano → `mix-blend-mode: difference` invece di duplicare le regole di colore. `clip-path` / `mask-image` per superfici non rettangolari.
7. Fallimento: alternare `#ffffff` / `#f8f9fa` (alternanza invisibile, costa come una vera e non produce ritmo); pagina di tinta piatta + card bianche con shadow morbida; hero curatissima e sezioni successive senza nessuna decisione di superficie.

## Chrome geometry — forma di box e pulsanti (sempre)

Il problema: senza una scelta esplicita, ogni landing finisce con **angoli a 0** (box e CTA “tutti quadrati”). È lo stesso riflesso del velo scuro: un default invisibile che rende i progetti uguali anche quando palette e font cambiano.

1. **Vietato come default implicito:** `border-radius: 0` su bottoni + card + input + panel in ogni job. Se usi sharp, deve essere una **scelta dichiarata**.
2. **Dichiara `radius_family:`** (e token CSS `--r-btn` / `--r-box` / `--r-chip`) prima di implementare. Famiglie (scegline una dominante; puoi mischiare btn≠box solo se dichiarato):

| `radius_family` | Bottoni | Box / card / input | Quando (tipologia) |
|---|---|---|---|
| `sharp` | 0–2px | 0–4px | sport, editorial luxury, architecture, brand “tagliente” |
| `soft` | 8–14px | 10–16px | **SaaS / product / revenue / dashboard**, tool B2B |
| `rounded` | 16–24px | 16–20px | hospitality warm, food, lifestyle, family hotel |
| `pill` | 999px | box restano soft/rounded | consumer app, wellness, promo CTA (non tutto pill) |
| `mixed-signal` | pill o soft | sharp panels | fintech/data con CTA morbida su chrome rigoroso |
| `organic` | 12px asym / blob leggero | 20px+ irregolare | artisanal, studio creativo (raro; non forzare) |

3. **Due input obbligatori per scegliere:**
   - **Tipologia / activity** (tabella sopra = priorità).
   - **Batch ≥30** (`hero_sample.py` / inspire-ops): mentre studi i riferimenti, annota la **lingua degli angoli** (quanti sharp vs soft vs pill). La famiglia scelta deve essere **coerente con il mix dominante dei migliori**, non col primo Dribbble soft-rounded a caso — e **diversa** da `last_radius_families` in MEMORY.
4. Procedura: (a) leggi MEMORY → (b) activity → shortlist 1–2 famiglie → (c) conferma/altera col batch ≥30 → (d) dichiara token → (e) applica a **btn, card, input, chip, modal** in modo coerente.
5. Soft-gate: micro-edit su UI già radius-ata → non rifare tutto; **new craft / new landing** → regola completa.
6. Fallimento: ogni demo con gli stessi angoli a 0; oppure pill ovunque su un brand luxury sharp; oppure ignorare il batch e defaultare sempre a soft “perché SaaS”.

Token minimi da mettere in `:root` (esempio):
```css
:root {
  --r-btn: 999px;   /* o 0 / 10px … */
  --r-box: 12px;
  --r-chip: 8px;
}
```
Poi `border-radius: var(--r-btn)` su `.btn`, `var(--r-box)` su card/panel/input.

## Inspiration before structure

Run AW batch (`hero_sample.py --surface marketing|dashboard|mobile`) before locking structure. Soft-gate micro-edit → skip. Ops: `references/inspire-ops.md`.

## Motion (Vera)

After substantial static craft (AF on page/layout/hero/**dashboard**), invoke **Vera Motion** (`agent-web-animations`). Marketing → cinematic; dashboard → micro-motion, verify in both themes. Soft-gate / «niente animazioni» → skip. Pure motion → Vera without AF. No invented GSAP timelines.

**Repeat obbligatorio (sempre):**
1. Tutti i reveal / curtain / counter / motion on-scroll **ripetono** a ogni ingresso nel viewport (enter → play, leave → reset). Default Vera: niente `data-anim-once`.
2. **Non** usare `data-anim-once` né one-shot equivalenti, salvo richiesta esplicita del owner in quel job.
3. Brief a Vera e Motion intent in UE devono dichiarare: `repeat: always`.
4. Soft-gate: se il progetto ha già one-shot e l’ask è micro-edit → non forzare un refactor globale; su **new craft / restyle motion** → converti a repeat.

**Motion diversificato — direzioni + seed ora/giorno (sempre su new craft):**
1. I reveal devono **mescolare direzioni**: da **destra**, da **sinistra**, da **alto** (e varianti). Non solo `up` / non solo una direzione.
2. Pool direzionale base (Vera):
   - destra → `slide` · `right`
   - sinistra → `slide-left` · `left`
   - alto → `slide-up` · `up` · `down` / `slide-down`
   - accenti: `zoom` · `zoom-out` · `blur` · `wipe` · `flip` (max ~1/3, non maggioranza)
3. **Seed = giorno + ora** `YYYYMMDDHH`. Dichiara `motion_seed: …` in DX/AF.
4. Procedura: `n = int(seed)`; `n % 3` = direzione dominante (0 destra, 1 sinistra, 2 alto) senza monopolio; ruota il pool con `n % pool_len`; gallery ≥4 → ≥1 per direzione.
5. Fallimento: tutta la pagina mono-`up` / mono-direzione; seed assente su new craft.

**Palette di tecniche motion (opzionali — scegli, non ripetere sempre le stesse):**
Non applicare mai lo stesso pacchetto su ogni landing. Il seed + locale + register + activity + densità desiderata decidono **quali** tecniche usare (di solito 2–4 per job, non tutte). Espandi il repertorio oltre lo slide IO:

| Tecnica | Cosa fa | Quando ha senso |
|---------|---------|-----------------|
| Reveal direzionale (IO) | entra da L/R/alto, repeat | default leggero; liste, copy, gallery |
| Hero crossfade / stack | dissolve opacità+z-index | hero multi-media hospitality/brand |
| Hero hard-slide | translate X | quando vuoi ritmo più tagliente |
| Scroll-scrub / progress | CSS vars legate allo scroll, reversibili | sezioni split, storia, menu cinematic |
| Pin / sticky + cover | fascia ferma, sezione dopo scorre sopra | passaggi tra capitoli |
| Zoom+fade in uscita | dissolve verso il blocco successivo | chiusura sezione media-heavy |
| Mosaico a finestre | card che compaiono lungo il progress | menu / griglia piatti |
| Gallery progressive | insert L→R + reveal univoci + **blow-up scroll-scrub** (gonfia man mano che scorre) + grow-from-center + lightbox | gallerie lunghe |
| Header reveal on scroll | nav nascosta in hero, compare dopo soglia | hero full-bleed |
| Parallax / pan | depth o pan orizzontale | media d’impatto (non ovunque) |
| Lenis / smooth scroll | scroll smussato | solo se stack/Vera lo supportano già o densità alta |

Riferimento osservato (principi, **non** ricetta obbligatoria né clone): [D’Aiello · Positano](https://www.daiellopositano.it/).  
Fallimento: ripetere sempre crossfade+scrub+sticky su ogni ristorante; oppure solo slide IO quando il job chiede densità cinematografica. Dichiara in DX/AF: `motion_techniques: […]` scelte per questo seed/job.
