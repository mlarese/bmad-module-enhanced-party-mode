# Glossario — ogni termine in parole semplici

## Prima regola: le parole normali battono quelle inventate

Questo skill parlava di «assi», «tempra», «stampo», «soft-gate», «goal»,
«deliverable» e «roster». Erano le parole di chi lo aveva scritto; per chiunque
altro erano rumore. E una regola che non si capisce non viene ignorata — viene
applicata **a caso**, che è peggio.

Adesso si scrive così:

| Si diceva | Si dice |
|---|---|
| asse / assi | **decisione / decisioni** — quelle che ogni pagina dichiara |
| goal | **obiettivo** |
| deliverable | **il lavoro consegnato** |
| stampo | **modello** — se ne copia la forma, non lo si fa partire |
| tempra | **controllo dei documenti** — le tre passate |
| soft-gate | **la scorciatoia per i lavori piccoli** |
| roster | **chi siede al tavolo** |
| new craft | **lavoro nuovo** |
| micro-edit | **correzione piccola** |

**Regola di scrittura, non solo di lettura: al primo uso in un documento, un
termine tecnico o interno porta la sua spiegazione fra parentesi.** Vale per i
lavori consegnati quanto per i reference: se in una consegna scrivi
«`bleed_rhythm: alternating`», scrivi accanto cosa significa.

Quando invece un termine inglese **è il nome vero della cosa** — `hero`,
`slice`, `responsive`, `seed`, `layout` — si tiene: tradurlo renderebbe
irriconoscibile ciò che tutti chiamano così. Ma si spiega la prima volta, sempre.

## Le parole che restano, e cosa vogliono dire

| Termine | In parole semplici |
|---|---|
| craft | il **mestiere fatto bene**: la differenza fra una pagina che funziona e una che si vede che qualcuno l'ha curata |
| hero | il **primo schermo** della pagina, quello che si vede senza scorrere |
| slice | una **fetta di lavoro completa**: schermo, dati e logica di quella funzione insieme, consegnabile da sola |
| seed | il **numero data+ora** (`2026072618`) usato come sorteggio: stessa ora, stessa scelta — le scelte variano ma restano ripetibili |
| batch | il **gruppo di riferimenti veri** guardati prima di decidere (almeno trenta) |
| corpus | la **raccolta di riferimenti** già scaricata, che non dipende dalla rete di adesso |
| scout | gli **script che vanno a cercare** riferimenti online |
| shell | l'**impalcatura dell'app**: barre, menu, contenitore — ciò che resta fermo mentre il contenuto cambia |
| chrome | la **cornice dell'interfaccia**: navigazione, barre, bottoni, campi |
| brief | le **istruzioni scritte** per chi implementa |
| sanctum | la **memoria su disco** dell'agente: chi è, cosa ha imparato, cosa ha già consegnato |
| owner | **tu**: chi dà il lavoro all'agente. Il cliente è un'altra persona |

## Le decisioni di design (quelle che ogni pagina deve dichiarare)

| Termine | In parole semplici |
|---|---|
| `locale` | il **luogo** del cliente: mare, montagna, città, campagna. Decide materiali e luce della palette |
| `register` | il **carattere** dell'attività: di lusso, familiare, popolare, artigianale, clinico. È un fatto del business, non un gusto |
| `activity` | il **mestiere**: ristorante, hotel, studio legale, e-commerce. Decide quali sezioni e quali oggetti servono |
| `palette_family` | il **nome** che dai al gruppo di colori scelto (es. «pino-rame») |
| `hue_sector` | il **settore di tinta** vero, misurato: rosso, terra, giallo, verde, teal, blu, viola, magenta, neutro. Il nome può cambiare mentre il colore resta lo stesso |
| `ink_family` | che tipo è lo **scuro** che riempie hero e footer: neutro, caldo, freddo o virato verso l'accento |
| croma | quanto un colore è **lontano dal grigio** agli occhi. Un nero con dentro un po' di verde ha croma bassa; un verde scuro pieno ha croma alta |
| `type_voices` | le **tre voci tipografiche**: il font dei titoli, quello del testo, e un terzo con un compito preciso (dati, citazioni, etichette) |
| `type_scale` | la **legge delle dimensioni** del testo: da quale misura si parte e di quanto cresce a ogni gradino |
| tracking | lo **spazio fra le lettere**. Negativo stringe (titoli grandi), positivo apre (etichette maiuscole) |
| leading | lo **spazio fra le righe** |
| `grid_system` | l'**impalcatura invisibile** in colonne su cui si appoggia il contenuto |
| `alignment_map` | dove sta il testo **sezione per sezione**: a sinistra, a destra, centrato, spezzato |
| `bleed_rhythm` | se le fasce di colore arrivano **fino ai bordi** dello schermo o restano dentro una colonna |
| `surface_rhythm` | l'**alternanza dei fondi** scendendo nella pagina: chiaro, scuro, immagine, chiaro |
| `surface_texture` | la **trama di casa**: righe sottili, puntinato, carta rigata, grana. Una sola, ripetuta |
| `radius_family` | quanto sono **arrotondati** bottoni e riquadri: spigolo vivo, morbido, tondo, a pillola |
| `hero_archetype` | lo **schema del primo schermo** scelto dal catalogo: che media, dove sta il testo, se c'è un pannello dietro |
| `hero_treatment` | come è **trattata l'immagine** del primo schermo (tagliata, in un riquadro, a due toni…) |
| `hero_copy` | **dove sta scritto** il testo nel primo schermo (non cosa dice: quello sono i testi) |
| `motion_seed` · `motion_techniques` | il **numero** (data+ora) che sorteggia gli effetti, e **quali effetti** hai scelto |
| la scorciatoia (era «soft-gate») | su una correzione piccola non si rifà tutto: niente batch, niente ripensamento della griglia |

## Il processo

| Termine | In parole semplici |
|---|---|
| il consiglio | la **riunione degli agenti** installati (privacy, legale, fiscale, infra, WordPress, motion, più i ruoli BMAD) che decide invece di chiedere all'owner |
| **G1** | primo giro: **si legge e si scioglie l'ambiguità** — cos'è questo lavoro, per chi, con che carattere |
| **G2** | secondo giro: **si scrivono i sei documenti** prima del codice |
| **G3** | terzo giro: **si approva o si rifiuta** il lavoro finito |
| i sei documenti | ricerca sul settore · ricerca di marketing · **PRD** · documento **UX** · architettura · contesto di progetto |
| PRD | il documento che dice **cosa deve fare** il prodotto e cosa no (*Product Requirements Document*) |
| documento UX | il documento che descrive **schermate, passaggi e stati** (vuoto, in caricamento, errore) |
| architettura | il documento che fissa **con quali tecnologie** si costruisce e dove sta ogni cosa |
| project context | le **regole non ovvie** che chi scrive il codice deve ricordare |
| il controllo dei documenti (era «tempra») | le **tre passate** su ogni documento: casi limite, domande di approfondimento, lettura ostile |
| casi limite | cosa succede **ai bordi**: nessun dato, troppi dati, testo lunghissimo, connessione assente |
| review avversaria | una lettura fatta **apposta per trovare il difetto**, non per confermare |
| slice (fetta verticale) | un pezzo di lavoro **completo e consegnabile da solo**: schermo, dati e logica di quella funzione insieme |
| `slice_plan` | l'**ordine delle fette**: prima la landing, poi il back office, e così via. Si scrive intero, si esegue **una riga per volta** |
| confine di slice | il punto in cui **una fetta finisce e si consegna**: il lavoro si chiude lì, e la fetta dopo la chiede l'owner. Non è una domanda — è una consegna |
| orchestratore della slice | **John** (il PM): tiene il piano, l'ordine degli agenti dentro la fetta aperta e la sua chiusura. Non decide l'aspetto: il craft non si vota |
| spec eseguibile | la **scheda di lavoro** di una fetta: cosa fare, dove, e come si verifica che sia fatto |
| `ready-for-dev` | il **timbro** sulla scheda di lavoro che dice «si può implementare così com'è»: è anche ciò che fa entrare `bmad-quick-dev` direttamente nell'implementazione, saltando le sue domande |
| `Ask First` | un campo del modello di scheda che **genera fermate**: ciò che ci scrivi dentro diventa una domanda all'umano a metà implementazione. Qui resta vuoto |
| varianza | il **verbale di uno scostamento**: cosa ci si aspettava, cosa si è fatto, perché |
| workflow «che si ferma» | un procedimento BMAD che a un certo punto **chiede qualcosa a un umano**: qui non si invoca, se ne copia il formato |
| **modello** (era «stampo») | usare **la forma** di un procedimento — i suoi schemi e criteri — senza farlo partire |
| headless | far partire un procedimento **senza interazione**, che risponde con un file o un risultato |
| checkpoint | il punto in cui un procedimento **si ferma ad aspettare** una risposta |
| tetto dei cinque | il **numero massimo di giri** prima di consegnare comunque, dichiarando cosa resta aperto |
| profilo `leggero` / `pieno` | quanti giri di controllo merita **questo** lavoro: pochi su una landing, tutti quando c'è un back end |

## Il mestiere tecnico

| Termine | In parole semplici |
|---|---|
| responsive | la pagina **si adatta** allo schermo: funziona sul telefono come sul computer |
| viewport (meta) | la riga di codice che dice al telefono **di usare la sua larghezza vera**. Senza, il sito esce rimpicciolito |
| breakpoint | la **larghezza di schermo** alla quale il layout cambia disposizione |
| `clamp()` | una misura che **cresce con lo schermo** fra un minimo e un massimo |
| `subgrid` | far **allineare davvero** gli elementi dentro le schede, invece che a occhio |
| `tabular-nums` | cifre tutte della **stessa larghezza**, così le colonne di numeri si incolonnano |
| overflow orizzontale | quando la pagina si **può trascinare di lato**: quasi sempre un difetto |
| tap target | l'**area toccabile** di un bottone: sotto i 44px circa, sul telefono si sbaglia |
| light/dark | i due **temi** chiaro e scuro |
| **OWASP** | la lista dei **rischi di sicurezza web** più comuni, da tenere presenti dal primo giorno |
| **SOLID** | scrivere il codice in **pezzi con una responsabilità sola**, così si cambia senza rompere |
| **SoC** | *separation of concerns*: **tenere separati** struttura, aspetto, comportamento e dati |
| **KISS** | scegliere la soluzione **più semplice** che regge i casi limite |
| **DRY** | ogni cosa **scritta una volta sola**, ma non a costo di complicare |
| escaping | **neutralizzare** il testo che arriva da fuori, così non può diventare codice eseguito |
| MEMORY `last_*` | l'elenco delle **ultime scelte fatte**, per non ripetersi |
| ledger | il **registro** dei settori di colore già usati, condivisibile fra progetti |
