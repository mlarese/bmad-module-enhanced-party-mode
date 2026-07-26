# Craft Rules — nucleo (vale per ogni superficie)

Shared non-inferables for DX / UE / AF. Da caricare quando serve. Not a capability.

Qui vive ciò che vale **sempre**: decisioni, lavoro consegnato, scorciatoia per i lavori piccoli, responsive,
palette e font, tipografia, composizione, superfici, chrome, batch, motion.

> **Legge dello skill — nessun human in the loop** (`references/autonomia.md`).
> Il flusso **non si ferma mai** per interpellare l'owner:
> niente domande, conferme, menù, scelte «a vista», beat di scoping, attese. Ogni
> ambiguità si chiude con una **decisione dichiarata** in una riga («l'ho letta come X,
> non Y»). Le scelte che un umano avrebbe sciolto passano dal consiglio con i **tre obiettivi**
> (§ *Il consiglio decide — tre obiettivi*). Se qui sotto una regola dicesse «chiedi», vale
> questa: si decide, si dichiara, si va avanti. L'owner corregge di sua iniziativa, e
> allora la sua parola vince.

**Carica anche il file della superficie** (uno solo, quello del job):

| Superficie | File | Cosa aggiunge |
|---|---|---|
| marketing / landing / home | `references/craft-marketing.md` | hero (catalogo · trattamento · copy layout), sezioni dal dominio, gallerie |
| dashboard / admin / product | `references/dashboard-rules.md` | minimo non negoziabile (temi light+dark, chrome) + corpus, 14 decisioni di ricetta, firma |
| mobile web app / PWA | `references/mobile-rules.md` | minimo non negoziabile (6 decisioni grafiche, manifest, shell) + corpus, 16 decisioni, craft grafico |

Nucleo + una superficie: mai tutte e tre. Se il job cambia superficie a metà,
carica l'altro file allora, non prima.

## Le decisioni da dichiarare — indice

Qui sotto ci sono **le decisioni che ogni pagina deve dichiarare per iscritto** —
un tempo si chiamavano «assi», e nessuno fuori da questo skill sapeva cosa
fossero. La colonna *In parole semplici* c'è perché una decisione capita a metà
viene applicata a caso. Il vocabolario completo sta in `references/glossario.md`,
che è anche la regola su **come si scrive qui**: un termine tecnico o interno
porta la sua spiegazione fra parentesi al primo uso — nei reference come in ciò
che consegni.

| Decisione | In parole semplici | Dichiarare | MEMORY | Script / nota |
|------|--------------------|------------|--------|----------------|
| Palette + fonts | i colori e i caratteri, e da dove vengono | `locale` · **`register`** · `activity` · `palette_family` · **`hue_sector`** · **`ink_family`** · `fonts` | `last_palette_families` · `last_hue_sectors` · `last_ink_families` · `last_font_pairs` · `last_registers` | da luogo + **carattere** + business; verifica con `palette_guard.py --check … --ledger` |
| Tipografia sistema | la legge dei testi: quali font, quanto grandi, quanto spaziati | `type_voices` (3 ruoli) · `type_scale` · tracking 2 poli · leading | `last_type_voices` | `craft_axes.py` per la legge di scala |
| Composizione | come è impaginata la pagina: colonne, allineamenti, larghezza dei bordi | `grid_system` · `alignment_map` · `bleed_rhythm` · misura `ch` | `last_grid_systems` | `craft_axes.py` seed |
| Superfici | come cambiano i fondi scendendo nella pagina, e che trama hanno | `surface_rhythm` · `surface_texture` · token materiali | `last_surface_textures` | `craft_axes.py` seed |
| Forma di bottoni e schede | quanto sono arrotondati bottoni, schede e campi | `radius_family` + `--r-btn/box/chip` | `last_radius_families` | + batch ≥30 corner language |
| Hero archetipo | lo schema del primo schermo, scelto dal catalogo | `hero_archetype` (id del catalogo) | `last_hero_archetypes` | `hero_gallery.py --suggest` — shortlist da seed, scelta tua |
| Hero immagine | come è trattata l'immagine del primo schermo | `hero_treatment` | `last_hero_treatments` | mai velo scuro full-bleed default |
| Hero copy | dove sta scritto il testo nel primo schermo | `hero_copy` · placement · panel | `last_hero_copy` | `hero_copy.py` seed |
| Sezioni | quali blocchi ha la pagina e perché | elenco + perché (1 riga) | — | auto se non istruite |
| Galleria | come entrano e si dispongono le immagini | L→R · gapless · forme · reveal univoci | — | blow-up scroll obbligatorio nel mix |
| Dashboard | il pannello di controllo: temi, cornice, ricetta | light+dark · chrome · 14 decisioni di ricetta + firma | `dashboard_themes` · `dashboard_shells` | `dashboard_recipe.py` su corpus (`dashboard-rules.md`) |
| Mobile web app | l'app che gira nel browser del telefono | 6 decisioni grafiche (`splash` · `app_background` · `brand_mark` · `onboarding` · `illustration` · `depth`) + 10 di shell · barra sempre visibile | `last_splashes` · `last_app_backgrounds` | `mobile_recipe.py` su corpus (`mobile-rules.md`) |
| Fase implementativa | i documenti che vincolano il codice | PRD · architettura (stack **obbligatorio**) · page spec · project context — o analisi autonoma dichiarata | — | `bmad_context.py` (`implementation-handoff.md`) |
| Inspiration | quanti riferimenti veri hai guardato prima di decidere | batch ≥30 | — | `hero_sample.py` / inspire-ops |
| Motion | il movimento: quali effetti e con che numero di sorteggio | `motion_seed` · `motion_techniques` (2–4) | — | Vera **repeat**; seed `YYYYMMDDHH` |
| Responsive | la pagina si adatta allo schermo, telefono compreso | viewport meta · breakpoints · touch · no overflow | — | **sempre** — desktop e mobile |
| Output | dove finisce quello che consegni | cartella del progetto | `demo_output` | default `{project-root}/apps/<slug>/` — una per progetto, ogni superficie; dentro anche `DESIGN.md` e `palette.html` (§10.1); **se lo slug esiste non si sovrascrive** (§ *L'output non si sovrascrive*) |

## Il lavoro consegnato è finito (sempre — nessuna eccezione)

Ciò che consegni si legge come una pagina **vera**, non come una bozza da completare. Nel file consegnato **non compare mai** una nota di sostituzione: niente `[INSERIRE …]` · `TODO` · `XXX` · `lorem ipsum` · «testo di esempio» · «sostituire con i dati reali» · commenti HTML/CSS che avvisano · sezione finale con l'elenco dei dati fittizi. Vale per HTML, CSS, JS, spec e README: se una demo dichiara di essere incompleta, non dimostra niente — ed è il primo dettaglio che un cliente finale nota.

I contenuti mancanti si **derivano** (vedi `implementation-handoff.md` §9 *I testi*), non si segnalano. Contatti, prezzi e orari verosimili si scrivono per intero e senza marcatori; **l'onestà sui dati inventati si dice all'owner in chat** — nell'avviso e in una riga alla consegna — non dentro l'artefatto. Preferisci recapiti che non possano appartenere a una persona reale (fasce telefoniche non assegnate, dominio coerente col brand fittizio).

Restano fuori dal riempimento i **fatti che fanno danno se creduti**: certificazioni, premi, partner o clienti reali, riferimenti di legge, dati sanitari, recensioni attribuite a persone esistenti. Lì non si inventa e non si scrive un segnaposto: si progetta la sezione in modo che non richieda quel dato, e lo si dice a voce.

**Lo spec di accompagnamento è un'altra cosa** e non viola questa regola: lì vivono documenti usati, decisioni dichiarate, casi limite, canone applicato, requisiti lasciati al backend — **e la voce `dati_verosimili:`**, l'elenco di cosa è inventato e dove. Nel lavoro consegnato non compare, in chat si dice comunque: la chat sparisce e il sito resta, quindi la catena di responsabilità ha bisogno di un anello scritto. Confine completo in `implementation-handoff.md` §10 *Due artefatti, due regole*.

Fallimento: `TODO` nel file consegnato; blocco «dati da sostituire» in coda alla pagina o allo spec; `lorem ipsum`; una certificazione inventata.

## L'output non si sovrascrive

`{project-root}/apps/<slug>/` è il default, e il default vale per una cartella
che **non esiste ancora**. La legge di autonomia copre le decisioni di progetto,
non il diritto di cancellare lavoro: dentro il workspace non si chiede il
permesso di *scrivere*, ma non si distrugge ciò che c'era.

1. **Slug libero** → si scrive lì.
2. **Slug occupato da un lavoro tuo, e l'ask è ripresa o correzione** → si
   modifica in place. È lo stesso lavoro consegnato: il conto dei rifiuti (§6.1 di
   `implementation-handoff.md`) prosegue, non riparte.
3. **Slug occupato da qualcosa che non hai scritto tu, o da una consegna
   diversa** → **non si sovrascrive**: si scrive in `apps/<slug>-<data>/` (o
   `-v2`), lo si dice in una riga alla consegna, e la scelta è una varianza se
   qualcuno domani si chiederà perché ci sono due cartelle.
4. **Mai** un `rm -rf` sulla cartella per «ripartire pulito»: si scrive accanto.

Fallimento: una consegna precedente sparita senza che nessuno l'abbia chiesto;
due progetti che si sovrascrivono l'`anim.css`; un `apps/<slug>/` rigenerato da
zero che porta via le modifiche a mano dell'owner.

## Prima del codice: i documenti, poi le slice

Il flusso implementativo vive in `implementation-handoff.md`; i testi dei obiettivo in
`autonomia.md`. Qui sta solo ciò che serve sapere mentre fai craft:

1. **Ricerca** — dominio e marketing, entrambe **scritte** (§2). È il tuo mestiere e
   non è una fermata.
2. **G1 — lettura.** Il consiglio giudica gli input e scioglie ogni ambiguità che
   sarebbe stata una domanda: superficie, `activity`, `register`, perimetro, stack,
   precedenze. Ricerca insufficiente → si rifà, **max cinque rimandi**.
3. **G2 — i sei documenti, prima del codice.** Se il pre-flight non li trova, li
   scrive il consiglio **al completo**: ricerca di dominio · ricerca di marketing ·
   PRD · documento UX · architettura · project context, più la `slice_plan`. Tre
   criteri attraversano tutto — **architettura dell'app · sicurezza (OWASP) ·
   vertical slice**. Il peso cambia col lavoro (una landing li ha corti), l'esistenza
   no.
4. **Controllo dei documenti** — nessuno passa com'è uscito: **casi limite** ·
   **elicitazione con tutti i metodi applicabili** · **review adversarial**, in
   consiglio, esiti dentro il documento (`implementation-handoff.md` §4.0b).
5. **`slice_plan` verticale** — ogni slice end-to-end e consegnabile da sola. Sito:
   S1 landing → S2 back office (accesso minimo reale) → S3+. App: S1 una schermata
   che fa una cosa vera → S2 auth completa. Mai auth completa come S1. **Il piano si
   scrive intero, si esegue una riga per volta:** si apre la S1 e basta.
6. **Una slice = una spec eseguibile** — `bmad-spec` headless **sulla sola slice
   aperta**, slug `<progetto>-s<N>-<nome>`, Ready for Development, ~900–1600 token
   **sul contratto applicativo**: le decisioni di craft stanno nel DESIGN e la spec li
   referenzia. Le `open_questions` si chiudono nello stesso giro.
7. **Implementazione** — tu la pagina (AF → Vera); la parte applicativa la scrive
   **`bmad-quick-dev`, invocato** sulla scheda `{implementation_artifacts}/spec-<slug>.md`
   con `status: ready-for-dev` e `Ask First` vuoto: con quel frontmatter entra da
   `step-03` e nessuna delle sue porte viene raggiunta (`implementation-handoff.md`
   §4.2b). L'ordine dentro la slice lo tiene **John** (§4.4); il craft resta tuo.
8. **G3 — approvazione** contro documenti + craft-rules, **max cinque rifiuti**.
9. **Consegna della slice, e il lavoro finisce lì.** Si dichiara cosa è consegnato e
   cosa resta nel piano — «landing online; la S2 back office parte quando me lo dici»
   — e non si chiede il permesso di continuare (§4.3, `autonomia.md` → *Il confine di
   slice*). La S2 la apre l'owner.

**Colori, caratteri e pulsanti si consegnano visti.** Accanto al lavoro consegnato,
in `apps/<slug>/palette.html`, le combinazioni che reggevano — colore · carattere ·
**forma e colore dei pulsanti** (raggio, pieno o contornato, respiro, maiuscoletto),
con quella applicata marcata **in uso**. La genera `scripts/palette_page.py`, che
**rifiuta** le combinazioni che `palette_guard` non approverebbe: non si mostra ciò
che non si potrebbe scegliere. Non è una domanda e non ferma niente — se poi l'owner
ne chiede un'altra, vince la sua parola: si aggiorna il DESIGN, si rifà la pagina, si
rigenera la palette (`implementation-handoff.md` §10.1).

**Ogni seduta lascia una riga.** Alla chiusura di ogni convocazione — G1, G2, ogni
passata di controllo, G3 — una riga in `docs/consiglio/<slug>.md` con
`scripts/council_log.py`: data · slice · obiettivo · **chi ha parlato** · cosa si è
deciso, giri compresi. Un file per progetto, accanto alle varianze. È un indice, non
un verbale: oltre una riga è una varianza o un documento, e lo script lo rifiuta.
`close_check --council` non fa consegnare senza (`implementation-handoff.md` §11.1).

**Il craft non si vota.** Palette, tipografia, hero, griglia, superfici e motion
restano tuoi: il consiglio decide *cosa* sta in pagina e *perché*, mai *come appare*.
Hero archetype ed effetto motion li scegli da seed, con le esclusioni di MEMORY.

**Prima di invocare un workflow BMAD, guarda se si ferma** (`HALT`, «ask the human»,
«user must approve», un menu da scegliere): se ha un checkpoint **sul percorso che
useresti** non si invoca — se ne prende il **formato** e il lavoro lo fa il consiglio o
tu. Ma «sul percorso che useresti» è la parola che conta: un workflow che instrada
sul formato dell'input salta i propri cancelli se gli dai ciò che si aspetta — è il
caso di `bmad-quick-dev` con una spec `ready-for-dev`. Tabella verificata in
`autonomia.md`.

**Le varianze si scrivono in `docs/varianze/YYYY-MM-DD-<slug>.md`** — cinque righe:
atteso · deciso · perché · tipo (deviazione | assunzione da verificare | conflitto
risolto) · scadenza. Solo dove tra sei mesi qualcuno chiederebbe «perché qui è così?».
Mai dentro il lavoro consegnato. Il pre-flight le rilegge per prime.

**Le indicazioni del progetto si leggono, non si gestiscono:** `CLAUDE.md` /
`AGENTS.md` sono la prima fonte da consultare — li mantiene il progetto, non tu.

## Il sito esistente del cliente (quando c'è)

Fonte di **contenuto**, mai di **design**. Le due cose non si toccano:

- **Contenuto — si prende.** Immagini (le sue foto valgono più di qualunque stock: si usano quelle, se ci sono e sono usabili), servizi e offerta reali, nomi, fatti, recapiti. Se l'owner non elenca cosa offre, lo si **verifica sul sito e lo si ripropone** — riorganizzato e raccontato meglio, non sostituito con servizi inventati.
- **Design — non si guarda.** Layout, palette, tipografia, hero, ritmo delle sezioni restano derivati da `locale` · `register` · `activity` e dal batch ≥30, come su un progetto nuovo. **Se il risultato somiglia al sito vecchio, il lavoro non è stato fatto**: il cliente lo rifà proprio perché quello che ha non gli basta.
- **Il marchio è un vincolo, non è il design del sito:** logo, nome e colori di brand documentati si rispettano e si dichiarano; il layout no.

Disciplina completa (immagini, diritti, servizi obsoleti, precedenza delle fonti): `implementation-handoff.md` §8 *Il sito esistente del cliente*.

## La scorciatoia per i lavori piccoli

**Correzione piccola** = copy, un colore, un bug, un componente isolato su UI già craftata. Su correzione piccola: **skip** AW batch ≥30, `hero_copy.py`, `craft_axes.py`, rifacimento griglia / ritmo di superficie, espansione sezioni, dual-theme completo, Vera (salvo l’ask sia motion). **Lavoro nuovo / restyle sostanziale / nuova landing / nuova shell dashboard** → regole complete sotto. Owner «niente animazioni» → skip Vera. La scorciatoia non autorizza stub solo-hero né palette generica. **Responsive non ammette scorciatoie:** ogni sito/pagina consegnata deve funzionare su desktop e mobile.

## Responsive (sempre — desktop e mobile)

Ogni landing, page o shell che AF consegna **deve** essere responsive. Non è un’opzione né un “poi”: è criterio di done. La scorciatoia non lo sospende.

1. **Viewport:** `<meta name="viewport" content="width=device-width, initial-scale=1">` obbligatorio su ogni HTML.
2. **Layout fluido:** griglie (`asym-rail`, `fine`, `12-col`, hero split, gallery) **collassano** sotto breakpoint — tipicamente ≤820–900px → una colonna / stack. Rail verticale → orizzontale. Niente layout a due colonne “schiacciate” su telefono.
3. **Tipografia e misura:** `clamp` / unità relative; headline e body restano leggibili (≥16px body effettivo su mobile). `max-width` in `ch` sì; overflow orizzontale del testo **vietato**.
4. **Media:** immagini e iframe (mappe) `max-width: 100%`; hero media con altezza sensata su mobile (`min-height` in `svh`, non 100vh bloccato). Gallery mosaico: su mobile track semplificata (es. 2 col o stack) **senza buchi** e senza overflow.
5. **Nav / chrome:** menu che non esce dallo schermo; CTA tap-friendly (target ≥44px circa); niente hover-only come unica via d’azione.
6. **No overflow-x di pagina:** `100vw` + padding non deve generare scrollbar orizzontale (compensa con `min(…)` / `calc` / `overflow-x: clip` sul contenitore se serve un full-bleed).
7. **Verifica prima di chiudere AF:** ridimensiona / pensa mobile (~375) e desktop (~1280). Se il brand-test passa solo su desktop → fallimento.
8. Fallimento: sito solo-desktop; testo tagliato; griglia a N colonne senza media query; mappa o gallery che sforano; viewport meta assente.

## Colori e caratteri (sempre — da luogo + carattere + tipo di attività)

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

Neutro = **croma ≤ 4** — sotto quella soglia non resta tinta da nominare (la saturazione da sola inganna sugli scuri: vedi *Lo scuro è una decisione*). Il **settore dominante** è quello dei due colori che coprono più area (fondo e scuro strutturale), non quello dell'accento.

2. **Due regole, non una — e la seconda è quella che mancava.**
   - **Di fila:** vietato ripetere la **famiglia** dominante per 3 job consecutivi.
   - **Di quota:** vietato che una famiglia stia su **più di un terzo** degli ultimi 8 lavori. Misurato: la regola di fila da sola non vedeva niente mentre il verde stava al **57%** della serie reale, perché fra un verde e l'altro passava sempre qualcos'altro. Una predominanza non è una ripetizione: si vede solo contando.

   **Famiglia, non settore:** `verde` e `teal` sono due voci in tabella e **una sola impressione** a schermo, e MEMORY registrava «teal+verde 5 demo su 11» proprio perché contate separate non violavano mai niente. Ora l'anti-ripetizione le fonde. È l'unica coppia fusa: le altre si aggiungono quando c'è la misura, non a intuito.

   **Perché il verde e non un altro:** `verde` (70°–165°) e `teal` (165°–200°) occupano **130° dei 360** della ruota — il 36%, contro i 30° del rosso e i 25° del giallo. Una palette che non eviti apposta quella zona ci finisce **una volta su tre per geometria**, prima ancora che ci si metta il gusto. Non è un vezzo da correggere con la buona volontà: va contato.

   In MEMORY vive `last_hue_sectors` accanto a `last_palette_families`: il nome serve a te, il settore serve all'occhio. **Ordine: il più recente per primo** — `--last` conta la serie dall'inizio della lista, e una lista in ordine cronologico inverte il controllo senza che nessuno se ne accorga.
3. **Il controllo di chiusura è un comando solo:** `uv run scripts/close_check.py <pagina> --design <DESIGN.md> --ledger <ledger.json>` — colore, responsive, segnaposto e traccia insieme. **Si consegna solo su esito `0`**, e l'esito si scrive nel `DESIGN.md`. Quattro regole sparse le si salta una alla volta; un comando o lo esegui o no, e si vede.
4. **Il motore del colore, se vuoi guardarci dentro:** `uv run scripts/palette_guard.py --check <file>` (o `--hex …`) stampa settori, saturazioni e violazioni. Su lavoro nuovo è parte del check di chiusura, come il responsive.
   - **Tre esiti, non due:** `0` pulito · `1` violazioni da correggere · **`2` non misurabile**. Il 2 arriva quando la palette non è leggibile da quel file (utility class senza mappa di tema, colori in un altro modulo): allora si misura il file che dichiara i colori, o si passa `--hex`. **Un exit 2 non è un pass:** «palette_guard pulito» si dichiara solo su un exit 0.
   - **Il ledger tiene il conto al posto tuo, e ora è condiviso di suo.** Serve perché `last_hue_sectors` vive nel sanctum **di quel progetto**: un'agenzia che fa un repo per cliente ha un job per sanctum, e la regola non avrebbe mai dati su cui scattare — misurato, l'unico ledger trovato aveva **una voce**. «Puntalo a un percorso condiviso» era una cosa da ricordare, e le cose da ricordare non si fanno: adesso il default è `~/.claude/agent-frontend-taste/hue-ledger.json`, fuori dai progetti, e `--ledger` serve solo per tenerne uno per cliente o per team (o `VESPER_HUE_LEDGER`). `--no-ledger` per non toccarlo. Se il ledger c'è, `--last` non serve.
   - **I tre hard-reject sono misurati adesso:** purple-indigo AI, cream+serif+terracotta, Inter/system come display escono come violazione dallo script, non più solo dal tuo occhio.

### Lo scuro è una decisione, non un residuo

Il difetto misurato non era l'accento — quelli erano diversi ogni volta — ma `--ink`: **verde o teal in 6 demo su 9**, con saturazioni fino al 66%. Conta perché lo scuro riempie le superfici **grandi** (hero scura, fasce `dark` del `surface_rhythm`, footer): l'accento vive su pochi pixel, lo scuro su mezza pagina. Una palette «euganeo-zafferano» con l'ink verde **legge come sito verde**.

1. **Dichiara `ink_family:`** — `neutro` (croma ≤ 4) · `caldo` (hue 15–60) · `freddo` (hue 180–260) · `virato-accento` (qualunque altra tinta).
2. **Tetto di croma sulle superfici grandi:** ogni fondo scuro (L ≤ 30%) che copre una sezione intera, la hero o il footer sta **entro croma 6**.
   Si misura il **croma percepito** — `saturazione × (1 − |2L − 1|)` — non la saturazione grezza: a L=5% una S del 17% è nero, a L=27% la stessa cifra è verde evidente. Tarato sulle demo consegnate: i neutri veri stanno a 1,6–3,1, mentre `#1A2A22` — il verde che riempiva una hero e faceva leggere verde tutta la pagina — sta a 6,2. Sopra soglia non è «nero di marca»: è un colore pieno, e a mezza pagina domina tutto il resto. Ammesso come **scelta dichiarata**, su **una** sola superficie.
3. **Lo scuro segue il `register`:** `famigliare` · `artigianale` · `popolare` → scuri **caldi** (bruno, seppia, ombra bruciata, testa di moro); `clinico` · `minimal` → freddi desaturati; `luxury` → profondo quasi-neutro con una sola vibrazione. Un'osteria famigliare con l'ink verde-bosco ha il carattere contraddetto dalla superficie più grande della pagina.
4. **Non far coincidere ink e accento di settore:** se l'accento è verde, lo scuro non è verde — altrimenti la pagina ha una tinta sola in due luminosità.
5. Dopo approve: MEMORY `last_ink_families` oltre a `last_hue_sectors`.
### I caratteri si contano come i colori

Misurato il 2026-07-26 sulle cinque pagine consegnate negli eval, leggendo le
variabili e non solo i letterali: **`DM Mono` era il mono di 5 su 5** (100%),
`DM Sans` il body di 4 su 5 (80%), `Fraunces` il display di 3 su 5 (60%). Peggio
del verde, che stava al 57%. Non c'era **nessuna** regola: `last_font_pairs` in
MEMORY è una nota, non un cancello, e sui font non esisteva alcun controllo di
ripetizione.

1. **Le stesse due regole del colore, per ruolo** (`display` · `body` · `mono`):
   mai la stessa voce per **3 consegne di fila**, e mai una voce oltre **un terzo
   delle ultime otto**. Le conta `palette_guard`, che ora registra i caratteri nel
   ledger insieme ai settori.
2. **Il mono è il punto cieco.** Display e body si scelgono con attenzione; la
   terza voce si mette «quella che va bene» e diventa sempre la stessa. È l'unico
   dei tre ruoli arrivato al 100%: contalo come gli altri.
3. **Il controllo legge le variabili.** `--display: "Fraunces"` con
   `h1 { font-family: var(--display) }` è il modo in cui queste regole dicono di
   scrivere, e il vecchio hard-reject «Inter come display» **non poteva scattare
   lì**: verificato, rilevava Inter dentro `h1` e non dentro `--display`. Ora
   risolve le variabili, le dichiarazioni letterali e la forma abbreviata `font:`.
4. Fallimento: la stessa voce mono su tre consegne di fila; una famiglia oltre un
   terzo delle ultime otto; `last_font_pairs` aggiornato ma mai controllato.

### Anche l'impaginazione e la hero si contano

Misurato il 2026-07-26 sulle stesse cinque pagine: **`--r-btn: 999px` su 5 su 5**
— la pillola ovunque — impaginazione a **rail su 4 su 5** (80%), hero con foto su
4, `eyebrow`/`kicker` su tutte, sei sezioni su quattro. `last_radius_families` in
MEMORY mostrava varietà (pill · soft · micro · sharp · mixed): quella però è
l'**etichetta**, e la geometria consegnata era sempre la stessa. È la ripetizione
del colore, un piano più su.

1. **Tre assi contati, e sono quelli che si misurano senza discutere di gusto:**
   `grid_system` (rail · fine · 12-col · flow, letto dalle `grid-template-columns`
   vere), `radius_family` (letta dal **numero** sul bottone, non dal nome che le si
   è dato), `hero_shape` (media × altezza: `foto-piena`, `testo-auto`…).
2. **Le solite due regole:** mai lo stesso valore per 3 consegne di fila, mai oltre
   un terzo delle ultime otto. Stesso ledger di colori e caratteri.
3. **Il raggio si legge sul bottone**, perché è lì che la famiglia si vede. Un
   `--r-box: 22px` non salva una pagina che ha il bottone a pillola come le quattro
   prima.
4. Fallimento: `radius_family` dichiarata diversa dalla geometria consegnata; rail
   + 12 colonne come impaginazione predefinita; la stessa forma di hero oltre un
   terzo delle ultime otto.

6. Fallimento: `ink_family` non dichiarato; scuro strutturale sopra S 15% non dichiarato; footer e hero della stessa tinta dell'accento; tre job di fila nella stessa famiglia; **una famiglia oltre un terzo degli ultimi otto lavori**; `verde` e `teal` alternati e contati come due cose diverse; ledger puntato dentro il progetto, dove riparte da zero a ogni cliente.

8. Dichiara in direzione: `locale: …` · `register: …` · `activity: …` · `palette_family: …` · **`hue_sector: …`** · **`ink_family: …`** · `fonts: Display + Body (+ terza voce)` · `radius_family: …` · perché — una riga che leghi i tre segnali all'esito, non etichette scollegate.
9. Dopo approve: aggiorna MEMORY (`last_palette_families`, **`last_hue_sectors`**, **`last_ink_families`**, `last_font_pairs`, `last_registers`, `last_hero_treatments`, `last_hero_copy`, `last_radius_families`).
10. **Il `register` non si sorteggia mai da seed.** Composizione, superfici e hero si estraggono apposta, per varietà; il carattere no: è un **fatto del business**, non una variabile estetica. Un seed che decide "luxury" per una trattoria produce una pagina coerente con sé stessa e falsa rispetto al cliente. Il carattere viene dal brief, dal dominio, dal sito del cliente o da **G1** — mai da `craft_axes.py`, mai da una domanda.
11. **Se è ambiguo lo decide G1, e tu lo dichiari — non lo chiedi.** Quando le due letture darebbero design **opposti** (famigliare vs luxury, artigianale vs clinico) la questione va al consiglio con l'evidenza raccolta (dominio, luogo, prezzi, tono del sito, clientela), e il verdetto entra nei documenti: «l'ho letto come famigliare, non luxury — perché ‹riga di motivo›». Negli altri casi decidi da sola e dichiara. Sbagliare `register` è l'errore più caro del set — non si corregge cambiando un font, si rifà tutto — ed è **esattamente** per questo che si decide sull'evidenza e si scrive la riga: una lettura sbagliata dichiarata si vede subito, una domanda costa un giro sempre.
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

## Composizione — griglia, allineamenti, misura (sempre su lavoro nuovo)

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
9. Scorciatoia (lavoro piccolo): correzione piccola → non rifare la griglia. Fallimento: container centrato + 12-col mai usata davvero + tutto left; oppure hero, header di sezione e CTA tutti centrati.

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

## La forma di bottoni, schede e campi (sempre)

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
   - **Batch ≥30** (`hero_sample.py` / inspire-ops): mentre studi i riferimenti, annota la **lingua degli angoli** (quanti sharp vs soft vs pill). La famiglia scelta deve essere **coerente con il mix dominante dei migliori**, non col primo Dribbble soft-rounded a caso — e **diversa** da `last_radius_families` in MEMORY. **Senza batch** (rete assente) comanda la tipologia + l'esclusione di MEMORY, e il buco si dichiara: § *Prima i riferimenti, poi la struttura* → *Quando il batch non c'è*.
4. Procedura: (a) leggi MEMORY → (b) activity → shortlist 1–2 famiglie → (c) conferma/altera col batch ≥30 → (d) dichiara token → (e) applica a **btn, card, input, chip, modal** in modo coerente.
5. Scorciatoia (lavoro piccolo): correzione piccola su UI già radius-ata → non rifare tutto; **lavoro nuovo / new landing** → regola completa.
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

## Prima si guardano i riferimenti, poi si decide la struttura

Run AW batch (`hero_sample.py --surface marketing|dashboard|mobile`) before locking structure. Scorciatoia correzione piccola → skip. Ops: `references/inspire-ops.md`.

**Quando il batch non c'è** (rete assente, sorgente cambiata, `hero_sample.py`
esce 1 con meno card del target): il lavoro **non si ferma** — la legge di
autonomia non prevede attese — ma non si finge nemmeno di aver misurato.

1. **Si dichiara il buco** in una riga, con il numero vero: «batch 12/30, fetch
   fallito su Envato». Un batch citato a memoria è il fallimento che §3 di
   `implementation-handoff.md` fa rifare.
2. **Le decisioni che dipendevano dal batch si decidono sull'altro input e lo si
   dice.** `radius_family` ne ha due (tipologia/`activity` **e** batch): senza
   il secondo comanda la tabella per tipologia, con l'esclusione di
   `last_radius_families` — non il default `soft` «perché SaaS».
3. **Corpus locale prima della rete:** `dashboard_corpus.py --stats` e
   `mobile_corpus.py --stats` leggono un corpus già costruito, che non dipende
   dalla rete di adesso. Se c'è, quello è il batch.
4. **Varianza** quando il buco ha deciso una decisione: cinque righe, così la pagina
   dopo sa che quella scelta non era misurata.

Fallimento: «batch ≥30 fatto» senza le card; una rete assente che diventa una
fermata; una decisione deciso dal default e dichiarato come se venisse dai riferimenti.

## Il movimento — lo cura Vera

After substantial static craft (AF on page/layout/hero/**dashboard**), invoke **Vera Motion** (`agent-web-animations`). Marketing → cinematic; dashboard → micro-motion, verify in both themes. Scorciatoia / «niente animazioni» → skip. Pure motion → Vera without AF. No invented GSAP timelines.

**Repeat obbligatorio (sempre):**
1. Tutti i reveal / curtain / counter / motion on-scroll **ripetono** a ogni ingresso nel viewport (enter → play, leave → reset). Default Vera: niente `data-anim-once`.
2. **Non** usare `data-anim-once` né one-shot equivalenti, salvo richiesta esplicita del owner in quel job.
3. Brief a Vera e Motion intent in UE devono dichiarare: `repeat: always`.
4. Scorciatoia (lavoro piccolo): se il progetto ha già one-shot e l’ask è correzione piccola → non forzare un refactor globale; su **lavoro nuovo / restyle motion** → converti a repeat.

**Motion diversificato — direzioni + seed ora/giorno (sempre su lavoro nuovo):**
1. I reveal devono **mescolare direzioni**: da **destra**, da **sinistra**, da **alto** (e varianti). Non solo `up` / non solo una direzione.
2. Pool direzionale base (Vera):
   - destra → `slide` · `right`
   - sinistra → `slide-left` · `left`
   - alto → `slide-up` · `up` · `down` / `slide-down`
   - accenti: `zoom` · `zoom-out` · `blur` · `wipe` · `flip` (max ~1/3, non maggioranza)
3. **Seed = giorno + ora** `YYYYMMDDHH`. Dichiara `motion_seed: …` in DX/AF.
4. Procedura: `n = int(seed)`; `n % 3` = direzione dominante (0 destra, 1 sinistra, 2 alto) senza monopolio; ruota il pool con `n % pool_len`; gallery ≥4 → ≥1 per direzione.
5. Fallimento: tutta la pagina mono-`up` / mono-direzione; seed assente su lavoro nuovo.

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
