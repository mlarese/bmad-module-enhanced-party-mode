# Autonomia — nessun human in the loop

*(«human in the loop» = un umano nel mezzo del processo, che a un certo punto
deve rispondere perché il lavoro prosegua. Qui non c'è: si decide e si va
avanti.)*

Legge dello skill. Vale sempre, su ogni capability (DX · AW · UE · AF — le
quattro cose che Vesper sa fare: dare la direzione di design, cercare
riferimenti, scrivere il brief, applicare il codice), e **batte ogni altra regola
di questi reference** che dicesse «chiedi», «conferma», «offri», «a vista». Non
dipende da nulla fuori dallo skill.

## La regola

**Il flusso non si ferma mai per interpellare l'owner.** Niente domande, niente
richieste di conferma, niente menù di opzioni, niente scelte «a vista», niente beat
di scoping, niente attese. Ricevuta la richiesta, il lavoro esce **finito** nella
stessa passata.

**Una riga sola sta fuori da questa regola, e sta prima di essa:** su un lavoro
nuovo si chiede all'owner **quale ciclo** — rapido o completo (§ *L'unica
domanda*). Non è dentro il flusso: è ciò che decide **quale flusso** parte.

**«Finito» vuol dire finita la slice, non finito il progetto** (§ *Il confine di
slice*). Un progetto con landing e back office esce a fette: la S1 esce finita e
il lavoro si chiude lì. Non è una fermata — non si chiede niente e non si aspetta
niente: si consegna. Le slice dopo le apre l'owner.

Ogni ambiguità si chiude con una **decisione dichiarata**: si sceglie la lettura più
probabile, la si scrive in una riga — «l'ho letta come X, non Y, perché ‹motivo›» —
e si procede. Una decisione sbagliata si vede e si corregge in un giro; una domanda
costa un giro **sempre**, anche quando la risposta era ovvia.

Se l'owner interviene di sua iniziativa, la sua parola vince e si corregge subito.
Ma non gli si chiede di intervenire.

## L'unica domanda: quale ciclo, e sta prima che parta niente

C'è **una** eccezione, ed è una sola riga con due opzioni, prima che il lavoro
cominci: **ciclo rapido o ciclo completo** (`references/ciclo-rapido.md`).

> **Rapido o completo?** ① Rapido: niente PRD, niente consiglio, niente review
> avversaria — decido io, dichiaro in sei righe, e ti do la bozza grafica subito.
> ② Completo: sei documenti, controlli e approvazione prima della pagina.

Non è un buco nella legge, ed è importante vedere perché:

- **Non è «in mezzo».** La legge vieta di fermarsi **dentro** un lavoro per far
  rispondere un umano. Qui non è partito niente: non c'è lavoro da fermare, e la
  risposta non serve a Vesper per decidere il *come* — serve a sapere **quanto
  deve costare** il lavoro, che è l'unica cosa che l'owner non può giudicare
  leggendo il risultato dopo.
- **Costa una riga e ha due opzioni.** Non è un menù, non è un beat di scoping,
  non apre altre domande.
- **Si chiede una volta per lavoro**, e vale anche per le correzioni su quella
  pagina. Ripeterla a ogni giro sarebbe esattamente la fermata vietata.
- **Non si chiede quando la risposta c'è già** nella richiesta («fammi una bozza
  al volo» → rapido; «voglio i documenti», o una richiesta con auth e dati →
  completo): si parte e si dichiara. E non si chiede su una **correzione
  piccola**, che non apre un ciclo.
- **Se l'owner risponde altro**, quella è la risposta: si legge la richiesta,
  si sceglie il ciclo più probabile, lo si dichiara in una riga e si va. Non si
  ri-chiede.
- **Se non c'è nessuno che possa rispondere, non si chiede** — chiamata headless,
  `--non-interactive`, invocazione da un altro skill, o una richiesta che dice
  «senza domande»: si sceglie il ciclo dalla lettura più probabile (pagina →
  rapido, back end → completo), si dichiara, si va. Una domanda a un chiamante
  che non parla non è un gate: è una fermata che nessuno scioglierà.
- **Dentro il ciclo scelto la legge vale intera:** nessuna domanda, nessun menù,
  nessuna attesa, fino alla consegna.

**Il ciclo rapido non è un permesso a fare peggio.** Taglia sedute e file — il
consiglio, i sei documenti, le tre passate di controllo — e **non tocca** il
craft: lock, cataloghi eseguiti, `repeat_guard`, `close_check`, `palette.html`,
responsive, copy vero, riga di onestà sui dati verosimili. Quelli costano
secondi, e sono l'intera differenza fra una bozza e un template.

## Chi decide: il consiglio, tre obiettivi

Tutte le scelte che un umano avrebbe sciolto passano dal consiglio
(`bmad-party-mode --non-interactive`), con obiettivi espliciti. Il consiglio **decide e
dichiara**: non produce domande da girare all'owner. Un consiglio che restituisce
una domanda ha fallito l'obiettivo — si rilancia l'obiettivo, non si gira la domanda.

### G1 — Lettura *(primo giro del consiglio: si legge la richiesta e si scioglie ogni ambiguità, decidendo invece di chiedere)*

> **Obiettivo:** sciogli ogni ambiguità di questo lavoro e chiudila con una decisione,
> non con una domanda. Decidi: superficie (landing · dashboard · mobile web app),
> `activity`, `register` (il carattere del business), perimetro reale della
> richiesta, stack quando nessuna fonte lo dichiara, precedenza fra fonti in
> conflitto, **il peso dei documenti** (una landing li ha corti, un progetto con back
> end pieni — ma esistono sempre), **il profilo di giri** (`leggero` | `pieno`,
> § *I tetti non si sommano*), e la lettura da dare a ogni punto ambiguo.
> Contesto:
> ‹richiesta · dominio · luogo · esito del pre-flight · documenti trovati · sito del
> cliente›. Per ogni voce: decisione + una riga di motivo + `fatto | assunzione`.
> Nessuna domanda all'owner.

### G2 — I sei documenti *(secondo giro: si scrive ciò che vincola il codice, prima di scriverne una riga)*

**Quando il pre-flight non trova i sei documenti, il consiglio li produce.** Non è una
scelta di peso del lavoro: è la condizione per scrivere codice sapendo cosa si sta
scrivendo. Nessuna domanda all'owner in nessun passaggio.

> **Obiettivo:** prima che venga scritta una riga di codice, e senza una sola domanda
> all'owner, produci ciò che manca fra: **ricerca di dominio** · **ricerca di
> marketing** · **PRD** (perimetro, requisiti, non-obiettivi) · **documento UX /
> page spec** (superfici, flussi, stati) · **architettura** (stack, confini, regole
> — da qui in poi lo stack è legge) · **project context** (le regole non ovvie che
> chi implementa deve ricordare). Chiudi con la `slice_plan`.
>
> **Tre criteri attraversano tutto e si dichiarano voce per voce:**
> **architettura dell'app** (confini, responsabilità, cosa sta dove) ·
> **sicurezza** (OWASP dal primo giorno: superficie d'attacco, dati personali,
> autenticazione, ciò che il front end non può garantire e resta requisito per il
> back end) · **vertical slice** (ogni pezzo end-to-end e consegnabile da solo).
>
> La `slice_plan` si scrive **intera**, ma si esegue **una riga per volta**: si
> apre la S1 e basta (§ *Il confine di slice*). L'ordine dentro la slice lo tiene
> John.
>
> **Usa i workflow BMAD**: `bmad-prd`, `bmad-ux`, `bmad-architecture`, `bmad-spec`
> si **invocano in headless**, e `bmad-quick-dev` si invoca passandogli una spec
> `ready-for-dev`, che lo fa entrare da `step-03` oltre le sue porte; quelli con
> checkpoint **sul percorso che usi** se ne copia il **modello** —
> vedi la tabella qui sotto. Ogni affermazione marcata `fatto | assunzione`.
> Contesto: ‹richiesta · dominio · luogo · register · esito della ricerca ·
> pre-flight · sito del cliente›.

**Convoca tutto il consiglio, non tre voci.** Ci sono tutti: chi non ha
giurisdizione su un punto tace su quel punto, ma c'è — perché il valore è l'attrito,
e un tavolo scelto da te contiene solo le obiezioni che ti aspettavi.

**L'elenco di chi siede al tavolo è ciò che è installato, e si legge — non si ricorda.**
`uv run scripts/council_roster.py {project-root}` lo deriva: **ogni agente
`skills/agent-*` di questo progetto è membro di diritto**, e lo script dice chi
di loro il gruppo `super-esperti` non ha seduto. Vale perché la lista scritta a
mano era in tre posti — il file di party, questo paragrafo,
`implementation-handoff.md` §3 — e i tre erano **già divergenti**: il party
portava tredici membri mentre i reference ne nominavano undici, e il PM e la dev
erano nella stanza ma in nessun elenco dei convocati che Vesper leggesse. Una voce che manca
non dà errore: semplicemente non parla mai, e nessuno se ne accorge.

- **Un agente nuovo in `skills/` entra senza che nessuno lo aggiunga qui.** Se
  domani compare un agente di sicurezza, di accessibilità o di contenuti, quello
  è consiglio dal primo lavoro: lo script lo trova, e la riga mancante nel TOML
  è un difetto di configurazione, **non** un permesso a decidere senza di lui —
  si convoca per nome in quella seduta e il gruppo si corregge.
- **Chi siede al tavolo oggi** (istantanea, non la fonte — la fonte è lo script):
  **agenti** Vesper (craft FE) · Vera Motion (movimento) · Jane Privacy (dati
  personali) · Elena Giuridis (claim e legale tech) · Rex Wire (infra, hosting,
  DNS) · Niki Press (WordPress) · Dan Arrow (prezzi, IVA, fiscale);
  **ruoli BMAD** John (perimetro) · Sally (flusso) · Winston (coerenza tecnica) ·
  Mary (evidenza) · Amelia (fattibilità implementativa) · Murat (ciò che nessuno
  ha verificato).

Parla chi sa: evidenza → Mary · perimetro **e orchestrazione della slice** → John
(`implementation-handoff.md` §4.4) · deployabilità → Rex ·
WordPress → Niki · dati personali → Jane · claim → Elena · prezzi →
Dan Arrow · buchi → Murat · flusso → Sally · coerenza tecnica → Winston ·
fattibilità → Amelia · craft → Vesper e Vera.

**John orchestra al tavolo, non prende la sessione.** Tiene il `slice_plan`, la
sequenza dentro la slice aperta e la sua chiusura; la voce resta di Vesper e le
chiamate le esegue Vesper. `bmad-agent-pm` **non si invoca come skill** dentro il
flusso: sostituirebbe la persona attiva e saluterebbe l'owner come John.

**Ogni seduta lascia una riga.** Un consiglio che decide tutto senza interpellare
l'owner gli deve almeno la traccia di **chi c'era**: alla chiusura di ogni
convocazione — G1, G2, ogni passata di controllo, G3 — si scrive una riga in
`docs/consiglio/<slug>.md` con `scripts/council_log.py` (data · slice ·
obiettivo · chi ha **parlato** · cosa si è deciso, giri compresi). Non è un
verbale: se non sta in una riga è una varianza o un documento, e lo script lo
rifiuta. Disciplina: `implementation-handoff.md` §11.1. Senza registro
`close_check` non fa consegnare.

Fallimento: un elenco di convocati ricopiato a memoria invece che derivato; un agente
installato che non è mai stato convocato; un gruppo di party incompleto preso
come il perimetro del consiglio.

**Il peso cambia, l'esistenza no.** Una landing ha un PRD di mezza pagina e
un'architettura di dieci righe; un progetto con back end, auth e back office li ha
pieni. Ciò che non cambia è che **esistano prima del codice**: un documento corto e
vero batte un documento assente, e il costo di scriverlo su una landing è dieci
minuti di consiglio, non tre workflow interattivi.

**Il `slice_plan` esce da qui**, e la `spec` di ogni slice da lì (§4.2 di
`implementation-handoff.md`).

**Un obiettivo solo, non sei catene separate.** Il consiglio è il contenitore: dentro, i
workflow headless si invocano davvero, quelli con checkpoint si usano come modello
(sotto). I documenti che il consiglio si scrive **vincolano come quelli dell'owner**,
ma ciò che nessuno ha verificato resta assunzione marcata, correggibile in consiglio
con una varianza — mai con una domanda.

### G3 — Approvazione *(terzo giro: si guarda il lavoro finito e si decide se consegnarlo)*

> **Obiettivo:** approva o rifiuta il lavoro consegnato contro i documenti vincolanti (§4.0),
> i craft-rules **e la richiesta originale dell'owner riletta testuale**
> (`implementation-handoff.md` §6.0: quando i documenti li ha scritti il consiglio,
> approvarli contro sé stessi non verifica niente — se i due metri divergono vince
> la richiesta e il documento si emenda). Approvabile se soddisfa **tutte** le
> richieste dei documenti, anche se qualcuno l'avrebbe fatto diversamente: il gusto
> non è un veto. Sul craft è rifiutabile **solo ciò che si conta** — un numero, una
> presenza, un esito di script (§6) — mai una preferenza.
> Ogni rifiuto nomina la richiesta mancante, e la stessa richiesta non può motivare
> due rifiuti. **Massimo cinque rifiuti** (tre sul profilo `leggero`): all'ultimo si
> consegna dichiarando cosa resta scoperto. Parla chi ha giurisdizione. Nessuna
> domanda all'owner.

Su lavori piccoli i tre obiettivi stanno in una chiamata sola; l'ordine logico resta:
prima si legge, poi si decide, poi si approva.

**Il craft non si vota.** Palette, tipografia, hero, griglia, superfici e motion
restano tuoi: il consiglio decide *cosa* sta in pagina e *perché*, mai *come appare*.
Le scelte di craft che un tempo erano «a vista dell'owner» — hero archetype dal
catalogo, effetto motion dalla gallery — le prendi tu da seed deterministico con le
esclusioni di MEMORY, e le dichiari.

**Dichiarare non basta più: si fa vedere.** Palette, caratteri e forma dei pulsanti
si consegnano applicati *e* mostrati, in `apps/<slug>/palette.html`, insieme alle
altre combinazioni che reggevano (`implementation-handoff.md` §10.1). Non è un
menù e non è una fermata: la pagina arriva **con** il lavoro finito, non prima, e
non aspetta niente. Il craft resta non votabile — l'owner che poi chiede un'altra
combinazione sta intervenendo di sua iniziativa, ed è l'unico caso in cui il craft
cambia: la sua parola vince.

## I procedimenti che si fermano: se ne copia il modello, non si fanno partire

*(«workflow» = un procedimento BMAD già scritto, fatto di passi. «Si ferma» = a
un certo punto chiede qualcosa a un umano e aspetta. «Copiarne il modello» = si
prendono i suoi schemi, i suoi criteri e la sua disciplina, senza farlo partire.)*

Un workflow BMAD invocato è una **porta**: se dentro ha un checkpoint, il lavoro esce
di lì e si ferma ad aspettare l'owner — e la legge è saltata, non perché qualcuno
abbia fatto una domanda, ma perché ha chiamato qualcosa che la fa al posto suo.

**Prima di invocare un workflow, guarda se si ferma.** Cerca nel suo `SKILL.md` e nei
suoi step: `HALT`, `ask the human`, `ask user`, `user must approve`, `wait for human`.
Se ne trova anche uno solo sul percorso che useresti, quel workflow **non si invoca**:
se ne prende il **formato** — template, criteri, disciplina — e il lavoro lo fa il
consiglio o Vesper, dentro il flusso.

**«Sul percorso che useresti» è la parola che conta.** Un workflow non è
inutilizzabile perché *contiene* un checkpoint: lo è se il checkpoint sta **dove
passi tu**. Alcuni instradano sul formato dell'input — dai loro ciò che si
aspettano e saltano i propri cancelli da soli. `bmad-quick-dev` è il caso: con una
spec `ready-for-dev` in mano, `step-01` esce subito verso `step-03` e le sue quattro
porte non vengono mai raggiunte (`implementation-handoff.md` §4.2b). Allora si
invoca, e si invoca **preparando il percorso**: passare l'input sbagliato lo fa
rientrare dalla porta principale, dove chiede. Il controllo non è «ha `HALT`?» ma
**«quale `HALT` incontro io, entrando di lì?»** — e la risposta si verifica nei suoi
step file, non a memoria.

| Workflow | Si ferma? | Come si usa |
|---|---|---|
| `bmad-quick-dev` | **le sue porte stanno tutte prima di `step-03`**: `step-01` (quale spec riprendere · chiarimento · albero sporco · multi-goal), `step-02` (gap · split · approve/edit), `step-oneshot`. Da `step-03` in poi l'unico `HALT` è su spec mancante — errore di chiamata, non domanda | **si invoca**, ed è lui a scrivere il codice applicativo: gli si passa la **scheda eseguibile della slice** in `{implementation_artifacts}/spec-<slug>.md`, formato `spec-template.md` di quick-dev, **`status: ready-for-dev`**, `Ask First` vuoto. Con quel frontmatter `step-01` fa EARLY EXIT diretto a `step-03` e nessuna delle sue porte viene raggiunta. Dettaglio: `implementation-handoff.md` §4.2b |
| `bmad-generate-project-context` | **sì**, per costruzione (avanza per step, ognuno con approvazione) | **modello**: il consiglio scrive `project-context.md` |
| `bmad-prd` · `bmad-ux` · `bmad-architecture` | **no**: hanno `references/headless.md` | **si invocano** in headless, dentro l'obiettivo G2 |
| `bmad-spec` | **no**: headless vero, express, slug fornito dal chiamante | **si invoca** (§4.2) |
| `bmad-review-edge-case-hunter` | **no**: si ferma solo su input vuoto (errore, non domanda) | **si invoca** su ogni documento (controllo dei documenti, §4.0b) |
| `bmad-review-adversarial-general` | quasi: «zero findings → re-analyze **or ask for guidance**» | **si invoca**, con la clausola: zero findings → **si ri-analizza**, mai si chiede |
| `bmad-advanced-elicitation` | **sì**: *è* un menu — «Choose a number (1-5), [r] Reshuffle, [a] List All» | **modello**: si prende `methods.csv` (71 metodi) e si applicano **tutti quelli applicabili**, senza presentare niente |
| `bmad-check-implementation-readiness` | — | **checklist**, riletta dal consiglio |

**L'owner può sempre invocarli lui.** Se è lui a lanciare `bmad-quick-dev`, le
fermate se le è scelte: si esegue il workflow com'è. La regola vincola te, non lui.

Fallimento: un workflow con checkpoint invocato dentro il flusso; la disciplina di
quel workflow **saltata** perché non lo si è invocato (lo modello è obbligatorio quanto
lo era il flusso); una porta scoperta dopo, perché nessuno ha guardato prima.

## Cosa non si chiede mai — e cosa si fa al suo posto

| Prima era una domanda | Adesso |
|---|---|
| «landing o dashboard?» | G1 decide da richiesta e dominio, e tu lo dichiari |
| «famigliare o luxury?» (`register`) | G1 decide su dominio, luogo, prezzi, tono del sito |
| «quale hero archetype?» | `hero_gallery.py --suggest N --seed … --last …` → il primo che regge |
| «quale effetto motion?» | seed `YYYYMMDDHH-<slug>` + `motion_techniques` dichiarate (Vera) |
| «quali sezioni vuoi?» | si inferiscono dal dominio e si dichiarano in una riga |
| «quale stack?» | architettura → project context → documenti del repo → segnali del repo → G1 |
| «confermi il perimetro?» | G2 lo decide, lo dichiara, non lo sottopone |
| «questo servizio è ancora attivo?» | si tiene se il sito lo espone, con varianza |
| «posso scostarmi dall'architettura?» | non ci si scosta: è legge. Se è impraticabile, si prende il percorso praticabile più vicino e si scrive la varianza |
| «quale palette preferisci?» · «pulsanti tondi o squadrati?» | si sceglie, si applica e si consegna — **e le alternative si vedono** in `apps/<slug>/palette.html`, già legali e con la tua marcata «in uso». Mostrare non è chiedere: la pagina non aspetta risposta |
| «vuoi che continui?» | **dentro la slice si continua**; a slice finita si consegna e si dichiara cosa resta nel piano — non si chiede il permesso di andare avanti, e non si va avanti |
| «vuoi che proceda con la S2?» | non è una domanda ammessa: la S1 si consegna, il piano si dichiara, la S2 la apre l'owner (§ *Il confine di slice*) |

**L'unica che resta è «rapido o completo?»**, e sta **prima** che parta il lavoro
(§ *L'unica domanda*). Tutto ciò che questa tabella elenca resta vietato dentro
entrambi i cicli: la domanda d'ingresso non ne riapre nessuna.

## L'avviso resta, la fermata no

Quando manca un documento vincolante (PRD, architettura, page spec) l'owner viene
**informato in apertura** di cosa sta per succedere: analisi autonoma, ricerca di
dominio e marketing, casi limite, review avversaria, dati verosimili ma non veri.

È una **dichiarazione**, non una domanda: si dice e si prosegue nella stessa
risposta, senza invitare a fermare il lavoro e senza attendere niente. Stesso
trattamento per la riga di onestà sui dati verosimili alla consegna: si dice, non si
chiede.

## Ogni ciclo interno ha un tetto: cinque

Tolte le fermate sull'owner, l'unico modo che resta a un flusso per non terminare è
girare su sé stesso. Entrambi i cicli interni hanno lo stesso tetto, e la stessa via
d'uscita: **si decide e si consegna, dichiarando cosa resta aperto.**

- **Ricerca insufficiente → massimo cinque rimandi.** Al quinto non si porta la
  questione all'owner: si **decide con l'evidenza migliore disponibile**, si dichiara
  in una riga quale delle tre cose mancava (domanda mal posta · fonti inesistenti ·
  dato che solo l'owner ha) e si scrive la varianza. Il lavoro esce comunque.
- **Approvazione negata → massimo cinque rifiuti** (G3). Ogni rifiuto nomina la
  richiesta mancante, e quella si corregge; la stessa richiesta non può motivare due
  rifiuti. Al quinto si **consegna comunque**, scrivendo in una riga quale richiesta
  è rimasta scoperta e perché, come varianza, e portandola nella slice successiva.
  Non si chiede all'owner il permesso di consegnare.

Il tetto è **per lavoro e per lavoro consegnato**, non per sessione: non si azzera
rinominando il job o rigenerando la pagina. Il conto finisce nello spec — zero
significa che nessuno guarda davvero, cinque che il problema sta a monte.

### I tetti non si sommano: c'è anche un tetto sul totale

Cinque rimandi di ricerca, più tre passate di controllo dei documenti che possono girare cinque
volte **su ognuno dei sei documenti**, più cinque giri di readiness, più cinque
rifiuti in approvazione: ogni ciclo termina, ma **il loro prodotto no**. Nel
caso peggiore sono un centinaio di sedute per una landing, e siccome nessuna di
esse interpella l'owner, l'owner non ha modo di accorgersene né di fermarle. Un
flusso che non si ferma mai deve sapere quanto costa.

1. **Il peso del lavoro fissa i giri, prima di cominciare.** G1 dichiara il
   **profilo**: `leggero` (landing, pagina singola, restyle) → controllo dei documenti **una
   passata per documento**, readiness una sola volta, rimandi max 2, rifiuti
   max 3. `pieno` (back end, auth, dati, ruoli) → i tetti pieni di §3.1 e §6.1.
   Il profilo si scrive nei documenti in una riga, come tutto il resto.
2. **Il secondo giro su un documento si guadagna:** si riapre solo se la
   passata precedente ha prodotto una modifica **sostanziale**. Tre passate che
   confermano non sono rigore, sono un ciclo che gira.
3. **Un tetto complessivo per lavoro**, e quando lo si tocca si consegna: al
   raggiungimento si prende ciò che regge, si dichiara cosa resta scoperto e si
   scrive la varianza — la stessa via d'uscita di ogni altro tetto.
4. **L'avviso di apertura dice anche questo** (`implementation-handoff.md`
   §1.1): non solo *cosa* sta per succedere, ma **quanto** — «profilo leggero:
   sei documenti corti, una passata di controllo, poi la pagina». Un owner che
   legge «procedo in autonomia» e non sa se tornerà fra due minuti o fra due ore
   non è stato informato, è stato avvisato.

Fallimento: tetti pieni applicati a una landing perché «la regola dice cinque»;
un documento riaperto per la terza volta senza che la seconda abbia cambiato
niente; un profilo mai dichiarato; un avviso che dice cosa ma non quanto.

## Il confine di slice: si consegna e si finisce

*(la «slice» è una fetta di prodotto completa e utilizzabile da sola: la landing,
poi il back office. Il «confine di slice» è dove una fetta finisce.)*

Il lavoro esce **una slice per volta**. La S1 si porta fino in fondo — documenti,
spec, codice, approvazione, `close_check` — si consegna, e **il lavoro finisce
lì**. Le slice successive partono quando l'owner le chiede. Disciplina completa:
`implementation-handoff.md` §4.3.

**Questo non è human in the loop, ed è importante non confonderli.** La legge
vieta di **fermarsi in mezzo** a un lavoro per far rispondere un umano. Al confine
di slice non c'è niente in mezzo e non si chiede niente: c'è una cosa finita,
consegnata, che sta in piedi da sola. Un flusso che si ferma a chiedere lascia
l'owner con **una domanda**; questo lo lascia con **una landing online**. Sono due
esiti opposti, e solo il primo è il fallimento che questa legge descrive.

- **La chiusura espone uno stato, non una scelta:** «landing online; nel piano
  restano S2 back office e S3; la S2 parte quando me lo dici». Mai «vuoi che
  proceda?», mai un elenco da spuntare.
- **Non si aspetta.** Detto quello, la risposta è chiusa. Se l'owner non torna,
  non è rimasto niente in sospeso: è consegnato.
- **Dentro la slice la legge vale intera:** nessuna domanda, nessun menù, nessuna
  attesa, dal pre-flight alla consegna.
- **Perché a fette:** il senso del vertical slice è che l'owner **veda** la prima
  prima che si costruisca la seconda. Consegnare tutto insieme lascia lo slicing
  nel nome e toglie l'unico punto in cui una lettura sbagliata si scopre a costo
  basso.

Fallimento: la S2 costruita di slancio dopo la S1; una domanda al posto della
dichiarazione di chiusura; una consegna che non dice cosa resta nel piano; un
lavoro tenuto aperto «in attesa» dopo aver consegnato.

## L'unico confine che resta

Questa legge governa le **decisioni di progetto e di craft**. Non tocca le azioni
**distruttive o irreversibili fuori dal workspace** — push, pubblicazioni, invii,
cancellazioni fuori dal perimetro del lavoro — che restano soggette alle normali
autorizzazioni. Fermarsi lì non è human in the loop: è la differenza fra decidere e
distruggere.

Neppure il **confine di slice** è human in the loop (sopra): lì non ci si ferma —
si finisce.

## Fallimenti

Una domanda all'owner in mezzo al lavoro — **e la domanda d'ingresso non fa
eccezione se arriva tardi:** «rapido o completo?» chiesto dopo che la ricerca è
partita è la fermata a metà lavoro, non il gate. Così come chiederla di nuovo a
ogni correzione, o farla diventare tre opzioni. Un menù di opzioni. «Confermi?».
«Preferisci A o B?». «Fammi sapere e procedo». Un catalogo aperto **in attesa di una
scelta** — aprirlo *alla consegna*, a decisione già presa e applicata, è un'altra
cosa e ora è la regola (`implementation-handoff.md` §10.1 punto 9): il vietato è
l'attesa, non il vedere. Un beat di scoping. Un consiglio che restituisce domande invece di decisioni.
Un lavoro che si ferma al quinto rimando. Un sesto rifiuto sullo stesso lavoro consegnato,
o un rifiuto che ripete una richiesta già corretta. Un avviso scritto come richiesta
di permesso. **«Vuoi che proceda con la S2?»** — al confine di slice si dichiara,
non si chiede. E il difetto opposto: **la S2 costruita di slancio** dopo la S1,
che toglie all'owner l'unica verifica che le slice esistono per dargli. **Una
seduta del consiglio senza la sua riga nel registro** (§11.1): decidere tutto
senza chiedere niente è la legge, farlo senza lasciare traccia di chi c'era no.
