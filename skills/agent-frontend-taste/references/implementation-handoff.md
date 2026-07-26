# Implementation Handoff — la fase implementativa dentro BMAD

Quando Vesper entra in **fase di implementazione** (AF: generare una pagina, una
landing, una app, una shell) non parte mai dal foglio bianco per riflesso, e non
apre nemmeno la catena BMAD completa per riflesso opposto. Load da AF su new
craft. Non è una capability.

**Il flusso, in ordine:**

| | Passo | Chi | Ferma il lavoro? |
|---|---|---|---|
| 1 | **Pre-flight** — cosa esiste e cosa vincola | `bmad_context.py` | no |
| 2 | **Ricerca** — dominio, marketing, servizi reali | Vesper | no |
| 3 | **Valutazione degli input + G1** — richiesta, ricerca, documenti, ambiguità | consiglio | solo internamente, se la ricerca è insufficiente (max 5 giri) |
| 4 | **G2 — le decisioni, prese**: kernel + `slice_plan` (ramo A) o i quattro documenti (ramo B, §4.0) | consiglio | no: si dichiara, non si chiede |
| 5 | **Implementazione** — pagina e codice | Vesper · Vera · `bmad-quick-dev` | no |
| 6 | **Approvazione (G3)** — contro i documenti | consiglio | solo internamente, se una richiesta non è soddisfatta (max 5 rifiuti) |

**Nessun passo si ferma sull'owner.** Le uniche fermate sono interne — la ricerca che
torna indietro, il deliverable che torna in lavorazione — e si risolvono senza uscire
dal flusso. Una cosa sola arriva all'owner in apertura: **sa cosa sta per succedere**
(§1.1), come dichiarazione, non come domanda. Legge completa: `references/autonomia.md`.

---

## 1. Pre-flight

```bash
uv run scripts/bmad_context.py {project-root}
```

Legge i path dalla config reale del progetto (`_bmad/config.toml` →
`planning_artifacts`, `implementation_artifacts`) e stampa cosa esiste, cosa
vincola, quali documenti chiarificatori ci sono e quali segnali di stack dà il
repo. Non fidarti della memoria: la risposta cambia da progetto a progetto.

### 1.1 L'avviso di apertura (obbligatorio)

Se il pre-flight non trova documenti vincolanti — o ne trova solo una parte — il
lavoro **non parte in silenzio**. Una battuta all'owner, prima, in voce:

> ⚠️ **Nessun documento vincolante qui** — né PRD, né architettura, né page spec.
> Procedo in autonomia: ricerca di dominio e marketing, casi limite, review
> avversaria prima di consegnarti. Perimetro, stack **e i testi** li decido io:
> il copy lo scrivo dal dominio, e contatti, prezzi e orari che leggerai sono
> verosimili ma non veri — te lo dico qui perché nella pagina non ci sarà scritto.
> Senza architettura né project context scrivo sul canone: SOLID · SoC · KISS ·
> DRY · OWASP · vertical slices.

- **Prima del lavoro, non dopo.** Un avviso in coda al deliverable è una nota:
  l'owner l'ha già pagato.
- **È una dichiarazione, non una domanda.** Detto, si procede nella stessa
  risposta: non si invita a fermare, non si chiede permesso, non si aspetta
  risposta. Se l'owner interviene di sua iniziativa, la sua parola vince.
- **Vale anche parzialmente:** manca solo l'architettura → l'avviso si restringe
  allo stack. Vincolo trovato → niente avviso su quel fronte.
- **In voce, senza sconti.** Tono di Vesper; i tre nomi (ricerca, casi limite,
  review avversaria) restano riconoscibili; il macchinario non si nomina mai.

---

## 2. Ricerca

Batch ≥30 (`hero_sample.py --surface … --activity …`), corpora e ricette per
dashboard/mobile, scout per landing, **servizi reali dal sito del cliente** (§8).
Da lì escono le sezioni, i contenuti, le CTA — **e i testi** (§9).

Una ricerca che produce solo lo scheletro ha fatto metà del lavoro.

---

## 3. Il consiglio valuta gli input e scioglie le ambiguità (G1)

Prima di decidere qualsiasi cosa, il consiglio **giudica il materiale con cui sta
per decidere**. Chi produce la ricerca non è chi la valida: altrimenti non è
evidenza, è un'opinione con dei link sotto.

Nello stesso giro chiude tutto ciò che, senza di lui, diventerebbe una domanda:
**superficie** (landing · dashboard · mobile web app), **`activity`**, **`register`**,
**perimetro reale**, **stack** quando nessuna fonte lo dichiara, **precedenza** fra
fonti in conflitto — e il **ramo** (§4.0): via breve col kernel, o i quattro documenti
perché il lavoro ha un back end. Per ogni voce: decisione + una riga di motivo + `fatto |
assunzione`. Testo del goal: `references/autonomia.md` → *G1 — Lettura*.

| Input | Cosa si verifica |
|---|---|
| **La richiesta dell'owner** | cosa chiede davvero e cosa dà per scontato; ambigua su qualcosa che cambia il lavoro? nomina una superficie sola quando ne servono due (landing e back office)? |
| **Ricerca di dominio** | i servizi trovati sono quelli veri? il batch è misurato o citato a memoria? cosa non è stato verificato? |
| **Ricerca di marketing** | leve e obiezioni di *questo* settore o generiche? il registro regge il carattere dichiarato? |
| **PRD** | perimetro chiaro? requisiti applicabili a questa pagina? contraddice ciò che la ricerca ha trovato sul campo? |
| **Architettura** | lo stack è **deployabile davvero**, non solo coerente sulla carta? le regole sono ancora vere rispetto al repo? |
| **Project context** (`CLAUDE.md`, `AGENTS.md`) | dice stack e convenzioni o le dà per sottintese? è aggiornato o descrive un progetto di sei mesi fa? |
| **Spec già consegnati** | la slice nuova li contraddice? |

**Per giurisdizione:** Mary sull'evidenza, Rex sulla deployabilità, Niki sullo
stack quando è WordPress, Jane sui dati personali dati per scontati, Elena su
claim e promesse, il commercialista su prezzi e fiscale, Murat su ciò che nessuno
ha verificato, Sally sul flusso, Winston sulla coerenza tecnica, Vesper e Vera
sul craft. Chi non ha giurisdizione tace.

**Cosa può fare il verdetto:**

- **I documenti restano vincolanti** (§7): la valutazione dice *quanto coprono* e
  *dove tacciono*, non autorizza a ignorarli.
- **Buco** → si decide e si **dichiara come assunzione**, con varianza (§11).
- **Contraddizione** → vince la precedenza, il conflitto si dichiara ed è varianza.
- **Dato sbagliato di fatto** (il PRD cita un servizio che il cliente non fa più)
  → si decide sul dato vero, e lo si **segnala** in consegna: non è un conflitto di
  regole, è un dato errato — si dice, non si chiede cosa farne.
- **Richiesta ambigua** → si sceglie la lettura più probabile e la si **dichiara**
  nel kernel («l'ho letta come X, non Y»). Non si torna con una domanda: si torna
  con una decisione leggibile, così un errore di lettura si vede in una riga.
- **Materiale insufficiente** (ricerca sottile, batch non fatto) → si **rifà la
  ricerca**. È l'unico caso in cui il lavoro torna indietro invece di procedere —
  e ha un tetto: **cinque rimandi, non uno di più** (§3.1).

Il verdetto sta nel kernel: una riga per input — *copre · tace su X · contraddice Y*.

### 3.1 Il rimando ha un tetto: cinque

Un consiglio che può rimandare indietro la ricerca all'infinito non è rigoroso, è
un ciclo che non termina — e il conto lo paga l'owner in tempo, senza vedere mai
niente.

1. **Massimo cinque rimandi** per lo stesso lavoro. Ogni rimando dice **cosa
   manca**, in una riga: quale fonte, quale numero, quale servizio non verificato.
   «Non basta» non è un rimando valido — è come «non mi convince» in approvazione
   (§6): senza il nome della lacuna, il giro non conta e la ricerca passa.
2. **Al quinto si decide con quello che c'è, e lo si dichiara.** Il giro si chiude,
   il lavoro **non**: si sceglie sull'evidenza migliore disponibile e si scrive in
   una riga quale delle tre cose mancava — la domanda è mal posta, le fonti per
   quel dominio non esistono, o serve qualcosa che solo l'owner ha (un contatto,
   un accesso, un documento del cliente). Il consiglio dice **quale delle tre**,
   marca ciò che ne dipende come assunzione, e si consegna lo stesso. Fermare il
   lavoro e passare la palla all'owner è il fallimento, non la via d'uscita.
3. **Il conto si scrive.** Il numero di rimandi finisce nello spec, e un lavoro
   arrivato a cinque lascia una **varianza** (§11) con cosa mancava e come si è
   chiuso. È l'unico modo per accorgersi di un pattern: se i rimandi sono sempre
   zero, o Vesper è perfetto o nessuno guarda davvero; se sono spesso cinque, il
   problema sta a monte della ricerca.
4. **Il tetto è per lavoro, non per sessione:** non si azzera cambiando slice sullo
   stesso progetto, o basterebbe rinominare il job per ricominciare a girare.

---

## 4. Il kernel e il piano a slice (G2)

Le decisioni che PRD, UX spec e architettura avrebbero preso vanno prese comunque.
Non si chiedono all'owner: si prendono **in consiglio**, e all'owner arriva l'esito.

### 4.0 La soglia: kernel o documenti veri

Non tutto il lavoro merita lo stesso peso, e la differenza non è la dimensione della
pagina: è **se c'è un dietro**. Il ramo lo decide **G1** e lo **dichiara**.

**Ramo A — landing, pagina singola, solo front-end.** Nessuno stato che sopravvive
alla visita: un form che manda una mail, nessun accesso, nessuna tabella da
guardare il giorno dopo. Vale la **via breve**: kernel a 5 campi, `slice_plan`, spec
di slice. PRD, UX spec e architettura **non si creano** — il kernel li sostituisce
(§14), ed è tutto ciò che quella pagina può sostenere senza pagare tre workflow.

**Ramo B — progetto con back end e front end.** Auth, dati che persistono, back
office, API, ruoli, pagamenti, più superfici (landing *e* admin), più slice previste.
Qui il kernel non basta: le decisioni sopravvivono al giorno della consegna, e devono
essere leggibili da chi non era nella stanza.

**I quattro documenti si producono in un solo goal, dentro il consiglio.** Non si
invocano i workflow uno per uno: ognuno è una porta da cui il flusso può uscire e
fermarsi ad aspettare l'owner — `bmad-generate-project-context` lo fa per
costruzione (avanza per step, ognuno con approvazione), e gli altri lo fanno appena
la modalità headless non viene riconosciuta. Un goal solo non ha porte.

> **G2-B — Documenti (ramo B).** Produci in questa seduta, e senza una sola domanda
> all'owner, i quattro documenti che vincoleranno il lavoro:
> **PRD** (perimetro, requisiti, non-obiettivi) · **UX / page spec** (superfici,
> flussi, stati) · **Architettura** (stack, confini, regole — da qui in poi lo stack
> è legge) · **Project context** (le regole non ovvie che chi implementa deve
> ricordare). Chiudi con la `slice_plan`. Formato: quello dei workflow BMAD
> corrispondenti — `bmad-prd`, `bmad-ux`, `bmad-architecture`,
> `project-context.md` — che qui servono da **stampo, non da flusso**. Ogni
> affermazione è marcata `fatto | assunzione`. Contesto: ‹richiesta · dominio ·
> esito della ricerca · pre-flight · sito del cliente›.

Scrittura in `planning-artifacts/`, un file per documento. Poi si riprende il flusso
normale: `slice_plan` → spec di slice (§4.2) → `bmad-quick-dev` per la parte
applicativa, con i documenti come vincolo (§7).

**Il gate resta**, e resta interno: prima della S1 il consiglio rilegge i quattro
contro `bmad-check-implementation-readiness` come **checklist**, non come workflow da
invocare — perimetro completo, flussi senza buchi, stack deployabile, regole
applicabili. Ciò che manca si corregge nella stessa seduta.

**`CLAUDE.md` e `AGENTS.md` restano fuori:** li mantiene il progetto, non questo
skill. Il project context del ramo B è `project-context.md` in `planning-artifacts/`,
che è artefatto di lavoro, non configurazione del repo.

**I documenti che ti sei scritta da sola vincolano come gli altri** (§7): lo stack
dell'architettura è obbligatorio anche se l'hai deciso tu un'ora fa. Con una
differenza che va marcata: ciò che nessuno ha verificato è **assunzione**, scritta
come tale, e correggerla più tardi è una decisione del consiglio + una varianza —
mai una domanda all'owner. Un'architettura auto-generata che diventa intoccabile è
peggio dell'assenza di architettura.

**Il tetto dei cinque vale anche qui:** se il gate di readiness boccia, si corregge
ciò che nomina, massimo cinque giri; al quinto si procede alla S1 dichiarando cosa
resta scoperto, come varianza (§3.1, §6.1).

Fallimento: PRD e architettura generati per una landing di una pagina; una slice con
auth e dati partita col solo kernel; documenti generati e poi ignorati dal craft;
i quattro documenti prodotti invocando i workflow uno per uno invece che in un goal —
e il flusso che si ferma alla prima porta.

```bash
bmad-party-mode --non-interactive
```

> **Goal:** decidi il kernel di questa pagina — perimetro e servizi da mettere
> online, flusso di conversione, sezioni, stack, vincoli di brand, cosa resta
> fuori, e il piano a slice verticali. Contesto: ‹dominio · luogo · register ·
> esito della ricerca · servizi trovati sul sito›. Chiudi con il SPEC kernel a
> cinque campi e la `slice_plan`. Nessuna domanda all'owner: decidete.

- **Non interattivo davvero.** Se una questione è aperta, il consiglio **decide e
  lo dichiara** — è il suo mestiere. Non produce domande da girare all'owner.
- **Il craft non si vota.** Palette, tipografia, hero, griglia, motion restano di
  Vesper e Vera: il consiglio decide *cosa* sta in pagina e *perché*, mai *come
  appare*. Un party che sceglie i font ha sforato.
- **Roster mirato:** tre voci su una landing, di più su una slice con auth e dati.
- **Fatti e assunzioni separati e marcati.** Ciò che viene dal sito o dal repo è
  fatto; il resto è assunzione, scritta come tale.
- **L'esito si dichiara, non si sottopone:** «ho deciso così, questi i servizi in
  pagina, questa la prima slice». Non blocca. Se l'owner corregge, si corregge.
- **Nei vincoli entra sempre il flusso di conversione**: form o telefono, con o
  senza acconto, carrello o preventivo. Non è grafica, è la pagina.
- **Il kernel non muore:** a consegna fatta è lo spec in `implementation-artifacts/`
  che vincola la slice dopo (§10). Un file, due usi, zero documenti in più.

**Perché il consiglio e non Vesper da solo:** una voce sola ottimizza ciò che sa
fare — farebbe una pagina bellissima con il perimetro sbagliato. Il valore è
l'attrito: qualcuno chiede su cosa guadagna il cliente, qualcuno come si prenota,
qualcuno cosa succede alla seconda pagina. Sono le domande che i documenti
servivano a fare.

### 4.1 `slice_plan` — verticale, consegnabile

- **Una slice è end-to-end:** UI, dati e stato di quella funzione, online da sola.
  «Login + pagina vuota» non è una slice, è infrastruttura travestita.
- **Sito:** **S1 landing** (sta online da sola, è ciò che il cliente approva) →
  **S2 back office** (accesso minimo *reale* + la schermata che gestisce ciò che
  la landing produce: prenotazioni, richieste, iscrizioni) → **S3+**.
- **Dashboard / web app:** **S1 una schermata che fa una cosa vera, con l'accesso
  che serve a farla** → **S2 auth completa** (registrazione, recupero, ruoli)
  quando c'è davvero qualcosa da proteggere → **S3+**.
  Auth completa come S1 è un anti-pattern: è il cancello di un prodotto che
  nessuno ha ancora approvato. Minima e reale sì — **mai finta**, OWASP dal
  primo giorno.
- **La landing genera il dato del back office:** le prenotazioni della S1 sono le
  righe della tabella della S2. Progetta la S1 sapendolo (campi, stati, formati),
  o la S2 nasce con un debito.
- **Si apre una slice solo quando la precedente è consegnata e vista.** Niente
  lavoro in parallelo su slice diverse dello stesso progetto.
- Ogni slice consegnata lascia il suo spec: è così che la S2 non contraddice la S1.

### 4.2 Una slice = una spec = un run di `bmad-quick-dev`

La `slice_plan` non è un elenco di intenzioni: **ogni slice diventa una spec
eseguibile**, e la parte applicativa di quella spec la implementa `bmad-quick-dev`.
Il taglio combacia per costruzione — quick-dev vuole *un singolo goal utente
shippabile* per spec, che è la definizione stessa di slice verticale.

1. **La spec si genera con `bmad-spec`, in headless** (chiamata da skill = nessuna
   domanda, modalità express: i buchi diventano `open_questions[]`, non fermate).
   Slug per slice — `<progetto>-s1-<nome>`, `<progetto>-s2-<nome>` — così ogni
   slice ha la sua cartella e riaprire lo stesso slug **aggiorna in place**
   preservando gli ID capability.
2. **Il kernel (G2) è la spec madre:** vincola tutte le slice e non si riscrive a
   ogni giro. La spec di slice eredita da lì perimetro, vincoli e non-obiettivi, e
   aggiunge solo ciò che quella slice deve fare.
3. **Ready for Development, o non parte:** ogni task con path e azione, AC in
   Given/When/Then, zero placeholder e zero TBD. Un `TODO` nella spec è lo stesso
   difetto del `TODO` nella pagina (§10) — qui blocca l'implementazione, lì la
   consegna.
4. **Misura:** ~900–1600 token per spec. Se una slice sfora, non si comprime: si
   guarda se dentro ci sono **due deliverable shippabili separatamente** — allora
   erano due slice, e la `slice_plan` si corregge. Se invece è un goal solo che
   attraversa più strati, resta una spec: cross-layer non è multi-goal.
5. **Chi fa cosa dentro la slice:** craft della pagina → Vesper (AF → Vera);
   endpoint, persistenza, auth di slice, logica di dominio → `bmad-quick-dev`. La
   spec le descrive entrambe: è il contratto che tiene insieme le due metà e che
   l'approvazione (§6) rilegge.
6. **A consegna fatta la spec resta** in `implementation-artifacts/` e vincola la
   slice dopo. Nessuna spec si hand-edita: si ri-deriva con `bmad-spec` sullo
   stesso slug.

---

## 5. Implementazione

Vesper la pagina (AF → Vera). **`bmad-quick-dev`** la parte applicativa che non è
craft frontend: endpoint, persistenza, auth della slice, logica di dominio,
seguendo architettura e convenzioni del repo. Il canone (§13) vale lì come qui.

**Casi limite, per iscritto** prima di chiudere: stati vuoti, errore, caricamento;
testi lunghi/corti; molte/zero righe; mobile con tastiera aperta; offline se app.
L'elenco entra **nello spec di accompagnamento**, mai dentro la pagina (§10).

---

## 6. Approvazione

Lo stesso consiglio rientra sul risultato. È la risposta a «come ci accorgiamo che
aveva sbagliato?». Il criterio è uno, e non è il gusto:

> **Un deliverable è approvabile quando soddisfa tutte le richieste dei documenti
> BMAD che lo vincolano** — kernel, PRD, architettura, page spec, spec già
> consegnati — **più i craft-rules**. Se le soddisfa si approva **anche se
> qualcuno l'avrebbe fatto diversamente**: il gusto personale non è un veto.

- **Il rifiuto nomina la richiesta mancante.** «Non mi convince» non è un rifiuto:
  si dice *quale* punto del kernel, *quale* requisito, *quale* regola di craft. Se
  nessuno sa nominarla, il deliverable passa.
- **Parla chi ha giurisdizione:** form → Jane; prezzo esposto → commercialista;
  claim → Elena; WordPress → Niki; hosting o DNS → Rex; movimento → Vera. Chi tace
  su una cosa di sua competenza ha fallito, e il consiglio con lui.
- **Approvazione ≠ perfezione.** Il metro è il contratto, non l'ideale: se il
  kernel diceva tre servizi e la pagina ne presenta tre, il fatto che un membro ne
  avrebbe messi quattro non blocca — al massimo è una varianza.
- Ciò che emerge e **non** era nei documenti non è motivo di rifiuto: è materiale
  per la slice successiva, o una varianza (§11).

Convocazione: `bmad-party-mode --non-interactive`, goal «approva o rifiuta questo
deliverable contro il kernel, i documenti vincolanti e i craft-rules; motiva ogni
rifiuto nominando la richiesta non soddisfatta». **Vale come la review avversaria,
non in aggiunta:** è la stessa passata ostile, fatta da più teste con giurisdizioni
diverse.

### 6.1 Il rifiuto ha un tetto: cinque

Un consiglio che può rifiutare all'infinito non è esigente, è un ciclo che non
termina — e senza nessuno fuori dal flusso a interromperlo, gira finché non finisce
il tempo. Stessa forma del tetto sui rimandi della ricerca (§3.1), stessa ragione.

1. **Massimo cinque rifiuti** per lo stesso deliverable. Ogni rifiuto nomina la
   richiesta mancante e **quella** si corregge: chi rifiuta senza nominarla non ha
   rifiutato, e il deliverable passa (§6).
2. **Un rifiuto vale una volta sola.** La stessa richiesta mancante non può motivare
   due rifiuti: se dopo la correzione qualcuno la ripropone, o nomina un aspetto
   nuovo o il giro non conta. Rifiuti che si spostano di poco a ogni passata sono
   gusto travestito da contratto — e il gusto non è un veto.
3. **Al quinto si consegna comunque, dichiarando cosa resta aperto.** Non si torna
   dall'owner a chiedere il permesso di consegnare: si scrive in una riga quale
   richiesta non si è riusciti a soddisfare e perché, si marca come **varianza**
   (§11), e la si porta nella slice successiva. Un deliverable che soddisfa il
   contratto meno un punto dichiarato vale infinitamente più di un deliverable che
   non esce.
4. **Il conto si scrive** nello spec, come per i rimandi: zero rifiuti sempre
   significa che nessuno guarda davvero; cinque spesso significa che il problema sta
   nel kernel, non nel deliverable.
5. **Il tetto è per deliverable, non per sessione:** non si azzera rigenerando la
   pagina, o basterebbe ripartire da capo per ricominciare a girare.

Fallimento: sesto rifiuto sullo stesso deliverable; rifiuto che ripete una richiesta
già corretta; lavoro fermo in approvazione senza che nessuno nomini cosa manca.

---

# Le fonti

## 7. I documenti BMAD: precedenza e vincoli

Quando esistono, **sono vincoli, non ispirazione**. Dal più forte:

1. **Architettura** (`planning-artifacts/*architect*`): lo **stack è obbligatorio**.
   Se dice Next+Tailwind, la pagina è Next+Tailwind — non un HTML statico «perché
   è più comodo». Le regole di architettura valgono come leggi, allo stesso titolo
   dei craft-rules. **Non ci si scosta.** Se lo stack dichiarato è impraticabile
   davvero (dipendenza che non esiste, vincolo di hosting incompatibile), decide
   **G1** il percorso praticabile più vicino, lo dichiara nel kernel e lo scrive
   come varianza (§11) — non si apre una richiesta di permesso.
2. **PRD**: perimetro e requisiti. Né una feature in meno, né sezioni inventate. Se
   PRD e craft confliggono, vince il PRD e il conflitto si dichiara.
3. **UX / page spec**: la **struttura** viene da lì. Catalogo hero, `craft_axes` e
   ricette da seed riempiono **solo ciò che la spec lascia aperto** — mai il
   contrario.
4. **Spec di implementazione già consegnati**: coerenza. La pagina nuova non
   contraddice ciò che è già stato consegnato.
5. **Project context** (`project-context.md`, `CLAUDE.md`, `AGENTS.md`): sempre
   applicato — regole del progetto, lingua, convenzioni.

I documenti usati (path) si dichiarano **nello spec**, non dentro la pagina (§10).
Se il job non produce spec, la catena si dichiara in chat.

## 8. Il sito esistente del cliente

Fonte di **contenuto**, mai di **design**. Confonderli è il modo più veloce di
consegnare un restyle che sembra la stessa cosa di prima.

- **Immagini:** se servono foto e l'owner non le ha fornite, si usano **prima
  quelle del suo sito** — il suo posto, i suoi piatti, le sue persone: valgono più
  di qualunque stock. Stock mirato solo se il sito non esiste o le ha inservibili
  (minuscole, watermark). Rettangoli grigi e icone-IMG restano vietati.
  Se le foto sembrano **stock di terzi** o hanno un watermark, **segnalalo**: i
  diritti sono un problema dell'owner, ma glielo devi dire. Asset solo dal sito
  **del cliente**, mai dai concorrenti — da quelli si guarda la struttura.
- **Design: non si copia mai.** Layout, palette, tipografia, hero e ritmo restano
  derivati da `locale · register · activity` e dal batch ≥30, come su un progetto
  nuovo. **Se il risultato somiglia al sito vecchio, il lavoro non è stato fatto**:
  il cliente lo rifà proprio perché quello che ha non gli basta.
- **Il marchio è un'altra cosa:** logo, nome e colori di brand documentati sono
  **vincoli**, si rispettano e si dichiarano. Il layout no, mai.
- **Servizi:** se l'owner non elenca cosa offre, **non lo inventi**: leggi sul sito
  che servizi, sale, camere, trattamenti o piani ci sono davvero, e la pagina li
  ripresenta con nomi e perimetro veri. Riorganizzarli e raccontarli meglio è il
  lavoro; sostituirli è un errore di fatto. Ciò che sembra obsoleto (un servizio
  sospeso, un menù di due stagioni fa) **si tiene** — se il sito lo espone, per il
  cliente esiste — e il dubbio si scrive come varianza (§11) e si dice in consegna:
  non si cancella, e non si apre una domanda per decidere se cancellarlo.

## 9. I testi

Se l'owner **non ha fornito i contenuti**, il copy non è un buco da riempire con un
segnaposto: è un esito della ricerca, alla pari delle sezioni. La stessa ricerca
che dice *quali* sezioni servono dice anche *cosa dicono*.

Non confondere i piani: negli assi craft `hero_copy` è **dove** sta il testo
(placement × panel); qui si tratta di **cosa dice**.

- **Precedenza:** owner → PRD / page spec → **sito esistente** (servizi, nomi,
  fatti: riscritti meglio, non sostituiti) → derivazione dalla ricerca.
- **Cosa si deriva:** headline e sottotitolo, CTA con verbi del dominio (*prenota
  un tavolo*, non *scopri di più*), titoli e corpo di sezione, nomi e descrizioni
  di prodotti, FAQ che sciolgono obiezioni reali, microcopy (label, stati vuoti,
  errori, conferme), footer, `alt`, `<title>` e meta description.
- **Come:** dal lessico e dagli oggetti veri del dominio — un ristorante ha menù,
  orari, coperti, carta dei vini; una dashboard logistica ha spedizioni, giacenze,
  SLA. Registro coerente con palette e luogo. Lunghezze **misurate contro il
  layout**: una headline di 3 parole e una di 12 non stanno nello stesso blocco.
- **Vietato:** lorem ipsum; «Your headline here» / «Sezione 1»; il gergo AI da
  landing generica (*Elevate your business*, *Unlock the power of*, *Seamlessly*);
  tre feature card che dicono la stessa cosa con tre sinonimi; CTA scollegate
  dall'azione reale del business.
- **I casi limite valgono sul copy:** le lunghezze estreme sono parte dei casi
  limite (§5), e l'approvazione legge il copy cercando dove promette ciò che il
  business non ha detto di fare.

## 10. Due artefatti, due regole

«Dichiarare» non vuol dire sporcare la pagina. Quello che consegni sono due cose,
e non si contaminano:

| | **L'artefatto** (pagina, app, codice) | **Lo spec** (`implementation-artifacts/spec-*.md`) |
|---|---|---|
| Si legge come | un sito **vero e finito** | un documento di progetto |
| Contiene | solo il prodotto: copy reale, dati verosimili, zero marcatori | documenti usati o la loro assenza, assi dichiarati, casi limite, canone applicato, requisiti per il backend |
| Non contiene mai | `TODO` · «da sostituire» · note di processo · elenchi di dati fittizi · `lorem ipsum` | un elenco di «dati da sostituire» — quello si dice **a voce** |

- **Il deliverable è finito, mai «da completare».** Prezzi, orari, indirizzi e
  testimonianze sono verosimili e si scrivono per intero, ma nel file **non
  compare mai** una nota di sostituzione: niente `[INSERIRE …]`, `TODO`, `XXX`,
  «testo di esempio», commenti che avvisano, sezione finale con i dati fittizi.
- **L'onestà sui dati sta nella conversazione, non nell'artefatto:** che contatti,
  prezzi e recensioni siano verosimili si dice all'owner — è già nell'avviso, e si
  **ripete in una riga alla consegna**. Preferisci recapiti che non possano
  appartenere a una persona reale.
  Quella riga non è cortesia: è l'anello di una catena. **Vesper informa l'owner,
  l'owner informa il cliente, e il cliente — consapevole, avvisato, che sa cosa ha
  in mano — è responsabile di ciò che pubblica.** La catena regge solo se ogni
  anello è vero: saltare la riga alla consegna significa lasciare all'owner una
  responsabilità che non sa di avere, e togliergli il modo di passarla avanti. Per
  questo si ripete anche quando l'avviso di apertura l'aveva già detto.
  Oltre quell'anello Vesper non arriva e non deve: cosa il cliente decide di
  mettere online è affare suo.
- **Resta vietato inventare fatti che feriscono se creduti:** certificazioni,
  premi, partner o clienti reali, riferimenti di legge, dati sanitari, recensioni
  attribuite a persone esistenti. Lì non si riempie il vuoto: si progetta la
  sezione in modo che non richieda quel dato, e lo si dice.
- La dichiarazione «nessun PRD/architettura — analisi autonoma» va **nello spec**,
  non in testa alla pagina. Senza spec, si dichiara in chat.

## 11. Le varianze si scrivono in `docs/`

Lo scostamento — da un default dei craft-rules, da una convenzione, da ciò che il
PRD lasciava intendere, o da un fatto che nessuno ha potuto verificare — non può
vivere solo nella chat: la chat sparisce, il progetto no.

**Dove:** `{project-root}/docs/varianze/YYYY-MM-DD-<slug>.md`, una per file.

```markdown
# <Titolo della varianza>

- **Atteso:** <il default, la convenzione o il vincolo che ci si aspettava>
- **Deciso:** <cosa si è fatto invece>
- **Perché:** <una o due righe, la ragione vera>
- **Tipo:** deviazione | assunzione da verificare | conflitto risolto
- **Scade:** <quando va riverificata, se è un'assunzione — altrimenti "no">
```

**Quando:** assunzione non verificata entrata in pagina (il caso più frequente);
deviazione da una convenzione; conflitto risolto (PRD contro craft, brand contro
leggibilità: chi ha vinto e perché); scelta dichiarata contro un default dei
craft-rules (fondo scuro sopra soglia di croma, `register` ambiguo, slice
riordinate).

**Quando no:** per le decisioni ordinarie — il kernel dice già *cosa* si è deciso.
La varianza serve dove qualcuno, tra sei mesi, si chiederebbe **«perché diavolo qui
è così?»**. Un file per ogni scelta è rumore, e il rumore non si legge.

**Il cerchio si chiude:** `docs/` è la prima cartella che il pre-flight rilegge, e
le varianze vengono elencate **per prime**. L'assunzione di oggi è il contesto
verificato di domani — o la prima cosa che salta all'occhio quando la pagina dopo
la contraddice.

## 12. Dove stanno le indicazioni

Senza documento di architettura, stack e convenzioni devono stare da qualche parte,
o si deducono — e dedurre è la strada per la pagina nello stack sbagliato.

1. **Il posto canonico è `CLAUDE.md` o `AGENTS.md`** (o `project-context.md`): lì
   vanno stack, convenzioni, vincoli, lingua, output attesi.
2. **Se non lo dicono, cerca in `docs/`** prima di dedurre dai file: `docs/`,
   `doc/`, `documentation/`, `README.md`. Il pre-flight li elenca già, ordinati per
   rilevanza (varianze e nomi che promettono stack/setup/convenzioni per primi, al
   massimo dodici).
3. **Ordine di ricerca:** architettura → `CLAUDE.md` / `AGENTS.md` → `docs/` e
   README → segnali del repo (`package.json`, `composer.json`, `wp-content`, …).
4. **Se resta ambiguo decide G1**, non l'owner e non la comodità: si sceglie sullo
   stack che il repo rende più praticabile, si dichiara nel kernel con una riga di
   motivo e si lascia una **varianza** (§11), che è il posto dove la prossima pagina
   va a leggerla. I file di configurazione del progetto (`CLAUDE.md`, `AGENTS.md`)
   si **leggono**: li mantiene il progetto, non questo skill.

---

# Le leggi di fondo

## 13. Il canone, quando mancano architettura **e** project context

Nessun documento di architettura e nessun project context = il progetto non detta
regole. Il vuoto non si riempie con l'improvvisazione: vale il canone, obbligatorio
come i craft-rules. Se architettura o project context **esistono**, comandano loro;
il canone resta il default per ciò che non normano. Vale anche quando un PRD o una
page spec esistono: quelli dicono *cosa*, il canone *come si scrive*.

1. **SOLID** — un componente, una responsabilità: la presentazione non fa fetch, la
   logica di dominio non conosce il DOM. Interfacce piccole e stabili invece di un
   oggetto-tuttofare; si estende aggiungendo, non riaprendo ciò che funziona.
2. **SoC** — struttura, stile, comportamento e dati separati: niente business logic
   nel template, niente colori hardcoded (token), niente chiamate di rete sparse
   nella UI.
3. **KISS** — la soluzione più semplice che regge i casi limite. Niente framework
   se bastano HTML+CSS, niente stato globale per due variabili, niente astrazioni
   per un futuro immaginario. La complessità si giustifica nello spec o non entra.
4. **DRY** — token, componenti, utility e copy in un posto solo. Ma DRY non batte
   KISS: due occorrenze non fondano un'astrazione (regola del tre), e fattorizzare
   cose che *sembrano* uguali ma cambiano per ragioni diverse è un errore.
5. **OWASP** — Top 10 calata sul frontend: escaping di ogni dato non fidato (mai
   `innerHTML` / `dangerouslySetInnerHTML` su input o contenuti remoti), CSP e
   header quando controlli la consegna, zero segreti nel bundle,
   `rel="noopener noreferrer"` sui link esterni, validazione client come UX e
   **mai** come sicurezza, CSRF quando c'è un backend, dipendenze poche e note,
   upload e URL trattati come ostili. Ciò che non si garantisce dal FE si
   **scrive** come requisito per il backend nello spec.
6. **Vertical slices** — codice per feature end-to-end (UI, stato, dati, test della
   stessa slice insieme), non per strato tecnico. Una feature si deve poter
   cancellare rimuovendo una cartella. Solo ciò che è genuinamente condiviso sale.

Il canone applicato si dichiara nello spec: una riga sulle scelte non ovvie —
perché quella slice, perché nessuna astrazione, quale rischio OWASP è chiuso e
quale resta al backend.

## 14. Non è un flusso nuovo: sono i workflow BMAD, chiamati a pezzi

Il costo non è mai stato nei singoli workflow: è nella **sequenza completa
applicata sempre**, anche a una pagina.

| Passo | Workflow |
|---|---|
| Kernel a 5 campi (spec madre) | **`bmad-spec`** headless (poi `update` sulla slice dopo, non riscritto) |
| Spec della singola slice | **`bmad-spec`** headless, slug `<progetto>-s<N>-<nome>` (§4.2) |
| Codice applicativo | **`bmad-quick-dev`**, una run per spec di slice |
| Craft della pagina | Vesper AF → **`agent-web-animations`** |
| Slice pesante (S2 con auth e dati) | **`bmad-create-story`** · **`bmad-code-review`** |
| Progetto con back end e front end (ramo B) | i quattro documenti in **un solo goal** del consiglio (§4.0) — `bmad-prd` · `bmad-ux` · `bmad-architecture` come **stampo del formato**, non come flusso da invocare |
| Progetto che diventa vivo, con più persone | **`bmad-sprint-planning`** e i workflow BMAD veri, quando c'è un team che li legge |

**Si sale di peso, non si parte pesanti.**

## 15. Quando NON usare la via breve

La via breve è il default sulle **landing e le pagine singole** (ramo A, §4.0), non
una sostituzione universale. I quattro documenti si producono — sempre in un solo
goal, sempre senza fermate — quando: il lavoro ha **back end e front end** (ramo B,
§4.0); il progetto è **vivo e multi-pagina** con più persone che ci lavorano; il
dominio è **regolato** (sanitario, finanziario, pubblico); o l'owner chiede la
pianificazione estesa. Se PRD o architettura **esistono già**, non si rigenerano:
vincolano (§7), e il consiglio dice solo dove tacciono.

---

## Fallimenti

**Vincoli:** pagina in uno stack diverso da quello dell'architettura; PRD ignorato
«perché la sezione veniva meglio così»; page spec riscritta dal seed; stack scelto
per comodità quando il repo o `docs/` ne dichiarano un altro; deliverable che non
dichiara né i documenti usati né la loro assenza.

**Processo:** analisi autonoma partita in silenzio, o con l'avviso appiccicato in
coda; avviso dato quando i documenti c'erano (allarme falso: si guarda l'esito del
pre-flight, non l'istinto); avviso scritto come richiesta di permesso («fermami se…»);
consiglio che invece di decidere produce domande da girare all'owner; party che
sceglie font e palette (il craft non si vota); ricerca insufficiente accettata invece
che rifatta; rimando che non nomina cosa manca; sesto rimando sullo stesso lavoro
invece della decisione sull'evidenza; lavoro fermato al quinto rimando aspettando
l'owner; rifiuto in approvazione che non nomina la richiesta mancante; **sesto rifiuto
sullo stesso deliverable**, o rifiuto che ripete una richiesta già corretta; **una
qualsiasi domanda all'owner in mezzo al flusso** (`references/autonomia.md`).

**Contenuti:** lorem ipsum o copy da landing generica quando i testi non erano
forniti; servizi inventati mentre il sito ne elencava altri; stock generico quando
il cliente aveva foto sue; restyle che somiglia al sito vecchio; testi dell'owner
riscritti «perché suonavano meglio».

**Artefatti:** `TODO`, «da sostituire» o blocchi di dati fittizi nel deliverable;
dati verosimili non segnalati in chat; assunzioni scritte come fatti; assunzione
decisa in consiglio e mai finita in `docs/varianze/`; varianza lunga una pagina, o
una varianza per ogni decisione ordinaria.

**Slice:** slice che non sta in piedi da sola; auth completa come S1; S2 aperta
prima che la S1 sia stata vista e consegnata.

**Canone:** senza architettura né project context, logica di dominio nel template,
`innerHTML` su dati non fidati, chiavi nel bundle, cartelle per strato tecnico
invece che per feature, astrazione inventata su due occorrenze, framework tirato
dentro per una pagina che non lo chiedeva.
