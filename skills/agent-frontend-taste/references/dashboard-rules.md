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

## Tabelle: paginazione e filtro multicampo, sempre

*(«server side» = il lavoro lo fa il server: la pagina chiede *quelle* venti righe
e *quel* filtro, invece di scaricare tutto e setacciarlo nel browser.
«autocomplete» = mentre scrivi, il campo propone i valori che esistono davvero.)*

Default **non negoziabile su ogni tabella**, salvo che i documenti dicano altro
(ultimo punto). Non è una preferenza: una tabella senza paginazione regge finché
i dati sono finti, e un filtro che setaccia in pagina regge finché le righe sono
venti. Le dashboard vere non stanno in nessuno dei due casi.

**Paginazione**

1. **Ogni tabella è paginata, e la paginazione è server side.** La pagina chiede
   un intervallo, il server risponde con le righe **e il totale**.
2. **Si vede a che punto sei:** «1–25 di 340», non solo frecce avanti e indietro.
   Senza il totale nessuno sa se sta guardando il 7% o il 90% dei dati.
3. **Ordinamento e filtro vanno server side con lei, o la paginazione mente.**
   Ordinare le 25 righe della pagina corrente sembra funzionare e non funziona:
   ordina un venticinquesimo dei dati e chiama «il più recente» il più recente
   *di questa pagina*. È il difetto classico, ed è invisibile in demo.
4. **Il modo di paginare si dichiara:** `offset` regge le prime pagine e crolla in
   fondo ai dataset grandi; `cursore` regge ma non salta a «pagina 12». Si sceglie
   sul dominio, si scrive nel DESIGN, e la dimensione di pagina predefinita con lui.
5. **Vuoto e vuoto-per-filtro sono due stati diversi.** «Non ci sono ancora
   prenotazioni» e «nessuna prenotazione con questi filtri» dicono cose opposte:
   il secondo offre di azzerare i filtri, il primo no. Confonderli fa credere che
   i dati siano spariti.
6. **Tastiera e lettori di schermo:** `nav` con `aria-label`, pagina corrente con
   `aria-current="page"`, e il cambio pagina annunciato — non solo dipinto.

**Filtro multicampo, server side, con autocomplete**

1. **Multicampo:** più campi combinabili — testo, stato, intervallo di date,
   relazione — non una sola casella di ricerca. La casella singola è il filtro che
   si mette quando non si è deciso su cosa si filtra davvero.
2. **La forma la sceglie la ricetta, il comportamento no.** `filter_pattern`
   (faceted-panel · search-first · saved-views…) resta **sorteggiato**: decide
   *che aspetto ha* il filtro e dove sta. Che sia multicampo, server side e con
   autocomplete non è sorteggiabile — è un invariante, e vale qualunque forma esca.
3. **Autocomplete sui campi che lo ammettono**, con quello che lo rende usabile
   invece che fastidioso: attesa breve prima di chiamare (~250 ms), un minimo di
   caratteri, stati di **caricamento · nessun risultato · errore**, frecce e invio
   e `esc` da tastiera, `role="combobox"` con `aria-expanded` e
   `aria-activedescendant`. **I suggerimenti non sono un veto:** si deve poter
   cercare un valore che non compare in lista.
4. **Le risposte tornano fuori ordine, e va gestito.** Chi digita «mar» in fretta
   manda tre richieste: se arriva per ultima quella di «ma», la tendina mostra i
   suggerimenti sbagliati sotto il testo giusto. Ogni risposta che non corrisponde
   all'ultima query si **scarta** (`AbortController` o un contatore di sequenza).
   È il difetto numero uno degli autocomplete, e in demo non si vede mai perché in
   locale le risposte tornano in ordine.
5. **Su una consegna statica non si finge:** si costruisce con la **forma** server
   side — una funzione di fetch parametrica, l'attesa, gli stati, il totale — e gli
   **endpoint si scrivono come requisito per il back end** nello spec
   (`implementation-handoff.md` §13 punto 5). Un filtro che setaccia in pagina venti
   righe finte è una demo che mente su come si comporterà a cinquantamila, e chi la
   approva compra quella bugia.
6. **Sicurezza e dati personali — qui parlano Jane e Rex, non il craft:**
   - il testo del filtro finisce in una query: **parametrizzata**, mai concatenata;
   - **l'endpoint di autocomplete è un enumeratore.** Digitare «a» restituisce
     l'elenco dei clienti: va autorizzato **come i dati che espone**, con un tetto
     ai risultati e un limite di frequenza, e non deve suggerire a qualcuno dati
     che non avrebbe il diritto di leggere. È il punto che non finisce mai nello
     spec, e resta aperto anche quando la tabella è protetta bene;
   - **i filtri con dati personali non vanno nella query string** — finiscono nei
     log, nel referrer e nella cronologia. Gli altri sì, e devono: una vista
     filtrata si manda a un collega, o non è una vista.

**La porta d'ingresso è l'eccezione.** Profilo e uscita valgono per le schermate
**dietro** l'accesso: una pagina di login, di registrazione o di recupero
password non ne ha, e non è un difetto — è la definizione. `close_check` la
riconosce (campo password, nessun logout, nome o testo da schermata d'accesso) e
non gliele chiede. Il **profilo** invece ha anche lui un campo password e resta
controllato, perché sta dentro e la sua uscita ce l'ha.

**Scorciatoia (lavoro piccolo):** una correzione su una tabella che c'è già non
obbliga a rifarle la paginazione. Una **tabella nuova** sì, sempre.

**A meno che i documenti non dicano altro.** PRD, documento UX, page spec e
architettura **vincolano** (`implementation-handoff.md` §7): se dicono lista corta
senza paginazione, o filtro in pagina perché l'insieme è chiuso e piccolo, comanda
il documento — e la deroga si scrive in una riga nel DESIGN, con il perché. Questo
è il default per quando **nessuno ha deciso**, non una regola da difendere contro
la specifica.

**Si dichiara nel DESIGN**, o è una decisione ereditata per riflesso:

```yaml
paginazione: server-side · offset · 25 per pagina · totale esposto
filtro: server-side · stato + intervallo date + cliente(autocomplete) · debounce 250ms
        requisiti backend → spec-<slug>.md (endpoint, autorizzazione, tetto risultati)
```

## Account: profilo, logout, admin — sempre

Una dashboard è un'area riservata: se ci si entra, si deve poter **uscire** e si
deve poter **cambiare la propria password**. E qualcuno deve poter rimettere in
piedi l'utente che si è chiuso fuori, o l'unico rimedio diventa una query a mano
sul database. Sono tre cose che non si aggiungono dopo: si progettano con la shell.

**Nel chrome, sempre**

1. **Profilo** raggiungibile da ogni schermata (voce di menù utente o avatar in
   alto a destra), e **logout** dentro quel menù — non nascosto in una pagina
   impostazioni.
2. **Il logout chiude la sessione sul server**, non svuota solo `localStorage`. Un
   logout che cancella un token e lascia la sessione viva sul server è un logout
   finto: chi ha copiato quel token entra lo stesso.
3. Chi sei e con che ruolo **si legge** nel menù utente. Un'interfaccia che cambia
   in base al ruolo senza mai dire quale ruolo hai è un'interfaccia che sembra
   rotta a chi ha meno permessi.

**Profilo — cambio password**

1. Il profilo permette il **cambio password**, e il cambio **chiede la password
   attuale**. Senza, chi si siede al posto di un collega con la sessione aperta si
   prende l'account in due clic: la ri-autenticazione è ciò che separa una sessione
   rubata da un account rubato.
2. **Cambiata la password, le altre sessioni cadono.** Se cambio la password
   *perché* qualcuno è entrato, e la sua sessione resta valida, non ho fatto niente.
3. Regole di robustezza dichiarate e verificate **anche sul server**: la
   validazione nel browser è comodità, mai sicurezza (`implementation-handoff.md`
   §13 punto 5).

**Admin — esiste sempre, e resetta le password**

1. **Il ruolo admin esiste dal momento in cui esistono gli account.** Non si
   aggiunge alla slice dopo: aggiungere i ruoli a cose fatte vuol dire riaprire
   ogni query e ogni schermata.
2. **L'admin resetta, non sceglie.** Non imposta una password che poi conosce e
   non gliela mostra: **emette un link di reset a uso singolo e con scadenza**, e
   la password se la sceglie l'utente. Un admin che conosce la password di un
   utente può agire *come lui*, e da quel momento nessun registro può più dire chi
   ha fatto cosa. È la differenza fra un amministratore e una chiave universale.
3. **Il token di reset:** uso singolo, scadenza corta, conservato **cifrato** (chi
   legge il database non deve poter usare i link in sospeso), invalidato quando ne
   viene chiesto un altro, e **tutte le sessioni dell'utente cadono** quando il
   reset va a buon fine.
4. **Nessuna password in chiaro, da nessuna parte:** non nei log, non in una mail,
   non in una schermata «ecco la nuova password», non nella risposta di un'API.
   Conservate con un algoritmo pensato per le password (argon2id, bcrypt) — mai un
   hash generico.
5. **Chi resetta cosa resta scritto.** Un registro delle azioni amministrative —
   chi, su chi, quando — non è burocrazia: è l'unico modo di rispondere fra sei
   mesi a «chi è entrato nel mio account?», ed è responsabilità che il GDPR chiede
   di poter dimostrare. **Qui parla Jane.**
6. **Nessuna credenziale di default consegnata.** `admin/admin` — o una password
   iniziale scritta nel repo, nel README o nel seed — è la vulnerabilità più banale
   che esista, ed è quella che sopravvive fino in produzione. Il primo accesso si
   fa con una procedura di avvio che **obbliga** a impostare le credenziali.
7. **Il reset e il cambio hanno un limite di frequenza**, o l'endpoint diventa un
   modo per provare password e per bersagliare di mail un utente.

**Chi lo scrive.** Profilo, sessione, ruoli e reset sono **parte applicativa**: li
scrive `bmad-quick-dev`, invocato sulla scheda `ready-for-dev` della slice
(`implementation-handoff.md` §4.2b). Vesper fa la loro superficie.

**In quale slice.** Profilo e logout stanno nella slice che porta la shell della
dashboard — una dashboard consegnata senza uscita non è consegnabile. Il **reset
amministrativo** sta nella slice dell'autenticazione, e quella slice porta il back
end: i sei documenti si **approfondiscono prima** di aprirla (§4.0b → *Il peso si
alza quando arriva il back end*). Finché non è aperta, ciò che manca vive nello
spec come **requisito per il back end**, scritto — non come un buco taciuto.

**A meno che i documenti non dicano altro** (`implementation-handoff.md` §7): se il
PRD dice accesso unico senza ruoli, o l'architettura impone un identity provider
esterno che gestisce password e reset per conto suo, comanda quello — e la deroga
si scrive nel DESIGN con il perché. Il default vale quando nessuno ha deciso.
**Ma l'uscita e il cambio password non sono derogabili per comodità:** se li toglie
un documento, quel documento ha preso una decisione di sicurezza, e va detto.

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

Sono stampati in ogni ricetta e valgono sempre: light+dark con due mappe di token e toggle **solo icona**; nav icona SVG + label; **riga = azione** con focus da tastiera e azioni di riga solo icone (`aria-label` + `stopPropagation`); **ogni tabella paginata server side con il totale esposto, e filtro multicampo server side con autocomplete** (§ *Tabelle: paginazione e filtro multicampo, sempre* — la forma la sorteggia `filter_pattern`, il comportamento no; salvo che un documento vincolante dica altro); **profilo e logout sempre nel chrome**, logout che chiude la sessione **sul server**, cambio password che chiede **la password attuale**, **ruolo admin dal primo account** con reset **a link monouso** (mai una password che l'admin conosce), zero credenziali di default (§ *Account: profilo, logout, admin — sempre*); `tabular-nums` su ogni cifra in colonna; **grafici inline SVG** senza librerie né canvas, con titolo e valori leggibili; ≥1 grafico vero e ≤5 KPI; empty state **e** skeleton per ogni lista; responsive (rail → orizzontale ≤900px, tabella con colonna sticky o card-list, nessun overflow-x, target ≥44px); `:focus-visible` e contrasto AA nei due temi; `prefers-reduced-motion` rispettato; motion **repeat**; palette hard-reject (purple-indigo AI, cream+serif+terracotta, Inter/system come display).

Corollario operativo: i grafici si calcolano **dai dati veri** dello stato dell'app. Un grafico con numeri finti è un placeholder, e un placeholder non può essere la firma.

## Procedura

1. Corpus presente e non vecchio (`--stats`); se manca, `--build` o dichiara il gap.
2. Genera la ricetta col dominio giusto e le esclusioni da MEMORY. Su varianti sorelle usa `--batch`.
3. Traduci **ogni** decisione in markup/CSS/JS concreti per quel dominio (es. `utilization-grid` = una cella per asset colorata per stato; `drilldown-panel` = dal KPI alla lista filtrata che lo spiega). Se una decisione non ha senso per il dominio, cambialo **e dichiara perché** — non ignorarlo in silenzio.
4. Verifica i due temi a ~375px e ~1280px, poi affianca la dashboard all'ultima consegnata: se le silhouette si somigliano, il batch o le esclusioni non hanno fatto il loro lavoro.
4b. **Prova la tabella come se i dati fossero tanti:** seconda pagina, ordinamento su una colonna mentre un filtro è attivo, filtro che non trova niente, autocomplete digitato in fretta. Sono i quattro punti in cui una tabella finta si rompe, e nessuno di loro si vede guardando la prima schermata.
4c. **Prova l'uscita e il rientro:** logout, poi torna indietro col tasto del browser — se rivedi la dashboard, la sessione non è chiusa. Poi cambia la password e verifica che l'altra sessione cada.
5. Aggiorna MEMORY: `last_palette_families`, `last_radius_families`, `last_type_voices`, `dashboard_shells`.

## Fallimenti

Sidebar + cinque card bianche + tabella piatta; **tabella senza paginazione**, o paginata in pagina su dati già tutti scaricati; **ordinamento che riordina solo la pagina corrente** e si spaccia per ordinamento; totale delle righe non esposto; **una sola casella di ricerca** al posto del filtro multicampo; filtro che setaccia un array in pagina senza che gli endpoint siano scritti come requisito per il back end; autocomplete senza scarto delle risposte fuori ordine, o senza stato di «nessun risultato»; **endpoint di autocomplete non autorizzato**, che enumera i clienti a chi digita una lettera; filtri con dati personali nella query string; vuoto-per-filtro confuso con il vuoto vero; deroga presa senza che un documento la dicesse, o presa e non dichiarata; **dashboard senza logout**, o logout che svuota `localStorage` e lascia viva la sessione sul server; **cambio password senza la password attuale**; sessioni che sopravvivono al cambio o al reset; **admin che imposta una password e la conosce**, o che la mostra a schermo; token di reset riusabile, senza scadenza o in chiaro nel database; password in un log, in una mail o in una risposta di API; **`admin/admin` o una password iniziale nel repo**; ruoli aggiunti alla slice dopo; reset amministrativo senza traccia di chi l'ha fatto e su chi; grafici da libreria o con dati inventati; ricetta generata e poi ignorata («ho tenuto la sidebar perché era già lì»); tre varianti con palette diverse e stessa impaginazione; KPI senza drill-down che spieghi il numero; tabella vuota senza spiegazione; tema scuro ottenuto per inversione.
