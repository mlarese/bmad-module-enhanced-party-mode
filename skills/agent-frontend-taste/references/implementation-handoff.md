# Implementation Handoff — la fase implementativa dentro BMAD

Quando Vesper entra in **fase di implementazione** (AF: generare una pagina, una
landing, una app, una shell) non parte mai dal foglio bianco per riflesso, e non
apre nemmeno la catena BMAD completa per riflesso opposto. Load da AF su new
craft. Non è una capability.

**Dove sta cosa** — §1 pre-flight · §2 ricerca (dominio + marketing, scritte) ·
§3 valutazione e G1 (+3.1 tetto rimandi) · **§4.0 i sei documenti** · **§4.0b la
controllo dei documenti** · §4.1 slice_plan · §4.2 spec di slice · **§4.3 una slice
per volta** · **§4.4 l'orchestratore** · §5 implementazione · §6
approvazione (+6.1 tetto rifiuti) · §7 precedenza dei documenti (+7.1 quelli
auto-scritti) · §8 sito del cliente · §9 testi · §10 due artefatti · §11 varianze ·
§12 dove stanno le indicazioni · §13 canone · §14 mappa dei workflow.

**Il flusso, in ordine:**

| | Passo | Chi | Ferma il lavoro? |
|---|---|---|---|
| 1 | **Pre-flight** — cosa esiste e cosa vincola | `bmad_context.py` | no |
| 2 | **Ricerca** — dominio, marketing, servizi reali | Vesper | no |
| 3 | **Valutazione degli input + G1** — richiesta, ricerca, documenti, ambiguità | consiglio | solo internamente, se la ricerca è insufficiente (max 5 giri) |
| 4 | **G2 — i sei documenti + `slice_plan`** (§4.0), poi il **controllo dei documenti** (tre passate) (§4.0b) | consiglio | no: si dichiara, non si chiede |
| 5 | **Apertura della S1** — spec eseguibile della **prima slice sola** (§4.2) | John orchestra (§4.4) | no |
| 6 | **Implementazione della S1** — pagina e codice | Vesper · Vera · **`bmad-quick-dev` invocato** (§4.2) | no |
| 7 | **Approvazione (G3)** — contro i documenti | consiglio | solo internamente, se una richiesta non è soddisfatta (max 5 rifiuti) |
| 8 | **Consegna della S1 — e qui il lavoro finisce** (§4.3) | Vesper | **sì, e non è una domanda:** le slice successive partono quando l'owner le chiede |

**Nessun passo si ferma sull'owner** — e il passo 8 non fa eccezione, perché non
gli chiede niente: **consegna**. Le uniche fermate interne sono la ricerca che
torna indietro e il lavoro consegnato che torna in lavorazione, e si risolvono senza uscire
dal flusso. Una cosa sola arriva all'owner in apertura: **sa cosa sta per succedere**
(§1.1), come dichiarazione, non come domanda. Legge completa: `references/autonomia.md`.

**Il flusso copre una slice, non il progetto.** Dal passo 5 in poi si parla sempre
della slice aperta: la S2 rifà i passi 5–8 quando l'owner la chiede, sugli stessi
sei documenti (§4.3).

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
> avversaria prima di consegnarti. **Profilo leggero:** sei documenti corti, una
> passata di controllo ciascuno, poi la pagina. **Ti consegno la S1 — la landing —
> e mi fermo lì:** il back office è la S2, sta nel piano, e parte quando me lo
> dici. Perimetro, stack **e i testi** li
> decido io: il copy lo scrivo dal dominio, e contatti, prezzi e orari che
> leggerai sono verosimili ma non veri — te lo dico qui perché nella pagina non
> ci sarà scritto (l'elenco di cosa è inventato lo trovi nel `DESIGN.md`).
> Senza architettura né project context scrivo sul canone: SOLID · SoC · KISS ·
> DRY · OWASP · vertical slices.

- **Prima del lavoro, non dopo.** Un avviso in coda al lavoro consegnato è una nota:
  l'owner l'ha già pagato.
- **È una dichiarazione, non una domanda.** Detto, si procede nella stessa
  risposta: non si invita a fermare, non si chiede permesso, non si aspetta
  risposta. Se l'owner interviene di sua iniziativa, la sua parola vince.
- **Vale anche parzialmente:** manca solo l'architettura → l'avviso si restringe
  allo stack. Vincolo trovato → niente avviso su quel fronte.
- **Dice anche *quanto*, non solo *cosa*.** Il profilo di giri deciso da G1
  (`autonomia.md` → *I tetti non si sommano*) sta nell'avviso in mezza riga: un
  owner che legge «procedo in autonomia» senza sapere se il lavoro dura due
  minuti o due ore non è stato informato. È l'unica leva che gli resta, visto
  che non gli si chiede niente.
- **Dice anche *fin dove*.** Quando il `slice_plan` ha più di una slice, l'avviso
  nomina **quale arriva adesso e quali restano** (§4.3): «ti consegno la landing,
  il back office è la S2 e parte quando me lo dici». Un owner che ha chiesto «una
  landing con back office» e riceve solo la landing senza saperlo pensa che il
  lavoro sia monco, non che sia una slice — ed è l'unico modo in cui la consegna
  a slice si legge come un difetto invece che come il metodo.
- **In voce, senza sconti.** Tono di Vesper; i tre nomi (ricerca, casi limite,
  review avversaria) restano riconoscibili; il macchinario non si nomina mai.

---

## 2. Ricerca — di dominio e di marketing, e si scrive

Batch ≥30 (`hero_sample.py --surface … --activity …`), corpora e ricette per
dashboard/mobile, scout per landing, **servizi reali dal sito del cliente** (§8).
Da lì escono le sezioni, i contenuti, le CTA — **e i testi** (§9).

**Due ricerche, non una.** *Dominio*: cosa fa davvero questo business, con quali
oggetti (menù, camere, spedizioni, SLA), quali servizi reali, quali vincoli del
settore. *Marketing*: leve, obiezioni e prove di **questo** mercato — perché uno
sceglie lui e non il concorrente, cosa lo blocca, cosa lo rassicura. Generiche non
valgono: «qualità e passione» non è una leva, è un riempitivo.

**Entrambe si scrivono** in `planning-artifacts/` (§4.0): una ricerca usata e persa
va rifatta identica alla slice dopo, e nessuno può controllarla. È il primo dei sei
artefatti, non il preambolo.

Una ricerca che produce solo lo scheletro ha fatto metà del lavoro.

---

## 3. Il consiglio valuta gli input e scioglie le ambiguità (G1)

Prima di decidere qualsiasi cosa, il consiglio **giudica il materiale con cui sta
per decidere**. Chi produce la ricerca non è chi la valida: altrimenti non è
evidenza, è un'opinione con dei link sotto.

Nello stesso giro chiude tutto ciò che, senza di lui, diventerebbe una domanda:
**superficie** (landing · dashboard · mobile web app), **`activity`**, **`register`**,
**perimetro reale**, **stack** quando nessuna fonte lo dichiara, **precedenza** fra
fonti in conflitto — e il **peso** dei documenti (§4.0): corti su una landing, pieni
quando c'è un back end. Per ogni voce: decisione + una riga di motivo + `fatto |
assunzione`. Testo dell'obiettivo: `references/autonomia.md` → *G1 — Lettura*.

| Input | Cosa si verifica |
|---|---|
| **La richiesta dell'owner** | cosa chiede davvero e cosa dà per scontato; ambigua su qualcosa che cambia il lavoro? nomina una superficie sola quando ne servono due (landing e back office)? |
| **Ricerca di dominio** | i servizi trovati sono quelli veri? il batch è misurato o citato a memoria? cosa non è stato verificato? |
| **Ricerca di marketing** | leve e obiezioni di *questo* settore o generiche? il registro regge il carattere dichiarato? |
| **PRD** | perimetro chiaro? requisiti applicabili a questa pagina? contraddice ciò che la ricerca ha trovato sul campo? |
| **Architettura** | lo stack è **deployabile davvero**, non solo coerente sulla carta? le regole sono ancora vere rispetto al repo? |
| **Project context** (`CLAUDE.md`, `AGENTS.md`) | dice stack e convenzioni o le dà per sottintese? è aggiornato o descrive un progetto di sei mesi fa? |
| **Spec già consegnati** | la slice nuova li contraddice? |

**Per giurisdizione:** Mary sull'evidenza, John sul perimetro, Rex sulla
deployabilità, Niki sullo stack quando è WordPress, Jane sui dati personali dati
per scontati, Elena su claim e promesse, Dan Arrow su prezzi e fiscale,
Murat su ciò che nessuno ha verificato, Sally sul flusso, Winston sulla coerenza
tecnica, Amelia sulla fattibilità implementativa, Vesper e Vera sul craft. Chi
non ha giurisdizione tace.

**Chi c'è, però, non si ricorda: si deriva.** `uv run scripts/council_roster.py
{project-root}` elenca gli agenti installati — **ognuno è membro di diritto** — e
nomina chi il gruppo `super-esperti` ha lasciato fuori. Questa riga qui sopra è
un'istantanea delle giurisdizioni, non l'elenco dei convocati: quando le due cose
divergono vince lo script, perché è l'unica delle due che si aggiorna da sola
(`autonomia.md` → *Convoca tutto il consiglio*).

**Cosa può fare il verdetto:**

- **I documenti restano vincolanti** (§7): la valutazione dice *quanto coprono* e
  *dove tacciono*, non autorizza a ignorarli.
- **Buco** → si decide e si **dichiara come assunzione**, con varianza (§11).
- **Contraddizione** → vince la precedenza, il conflitto si dichiara ed è varianza.
- **Dato sbagliato di fatto** (il PRD cita un servizio che il cliente non fa più)
  → si decide sul dato vero, e lo si **segnala** in consegna: non è un conflitto di
  regole, è un dato errato — si dice, non si chiede cosa farne.
- **Richiesta ambigua** → si sceglie la lettura più probabile e la si **dichiara**
  nei documenti («l'ho letta come X, non Y»). Non si torna con una domanda: si torna
  con una decisione leggibile, così un errore di lettura si vede in una riga.
- **Materiale insufficiente** (ricerca sottile, batch non fatto) → si **rifà la
  ricerca**. È l'unico caso in cui il lavoro torna indietro invece di procedere —
  e ha un tetto: **cinque rimandi, non uno di più** (§3.1).

Il verdetto sta nei documenti: una riga per input — *copre · tace su X · contraddice Y*.

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

## 4. I documenti e il piano a slice (G2)

Le decisioni che PRD, UX spec e architettura prendono vanno prese, e quei documenti
vanno scritti. Non si chiedono all'owner: si producono **in consiglio**, prima del
codice, e all'owner arriva l'esito.

### 4.0 I documenti si producono, sempre, prima del codice

**Se il pre-flight non li trova, il consiglio li scrive.** Non è una scelta legata al
peso del lavoro: è la condizione per scrivere codice sapendo cosa si sta scrivendo.
Sei artefatti, in `planning-artifacts/`, un file l'uno:

| | Artefatto | Come si produce |
|---|---|---|
| 1 | **Ricerca di dominio** | Vesper (§2), scritta — non solo usata e persa |
| 2 | **Ricerca di marketing** | Vesper (§2), scritta: leve e obiezioni di *questo* settore |
| 3 | **PRD** — perimetro, requisiti, non-obiettivi | `bmad-prd` **invocato in headless** |
| 4 | **Documento UX / page spec** — superfici, flussi, stati | `bmad-ux` **invocato in headless** |
| 5 | **Architettura** — stack, confini, regole | `bmad-architecture` **invocato in headless** |
| 6 | **Project context** — le regole non ovvie per chi implementa | **scritto dal consiglio** come `project-context.md`: il suo workflow avanza per step con approvazione dell'owner e pianterebbe il flusso |

Tutto dentro **un solo obiettivo del consiglio, con tutto l'elenco di chi siede al tavolo convocato** — testo in
`autonomia.md` → *G2 — I sei documenti*. Il party è il contenitore che tiene insieme la
seduta: dentro, i workflow headless si invocano davvero; quelli con checkpoint si
usano come modello (`autonomia.md` → *I procedimenti che si fermano*). Nessuna domanda
all'owner in nessun passaggio.

**Tre criteri attraversano ogni documento**, e si dichiarano voce per voce:

- **Architettura dell'app** — confini, responsabilità, cosa sta dove. Non «useremo
  Next»: dove vive la logica di dominio, cosa tocca il database, cosa è pubblico.
- **Sicurezza** — OWASP dal primo giorno (§13, punto 5): superficie d'attacco della slice,
  dati personali raccolti *davvero*, autenticazione proporzionata, e ciò che il front
  end non può garantire scritto come **requisito per il back end**. Un form di
  contatto è già raccolta di dati personali: Jane parla lì, non alla slice dopo.
- **Vertical slice** — ogni pezzo end-to-end e consegnabile da solo (§4.1). Il piano
  esce da qui, non dopo.

**Nei vincoli entra sempre il flusso di conversione**: form o telefono, con o senza
acconto, carrello o preventivo. Non è grafica, è la pagina — e se non lo decide il
PRD lo decide il layout per caso.

**Il peso cambia, l'esistenza no.** Una landing ha un PRD di mezza pagina e
un'architettura di dieci righe — il perimetro è piccolo, non assente; un progetto con
back end, auth e back office li ha pieni. Un documento corto e vero batte un
documento mancante, e su una landing costa una seduta di consiglio, non tre workflow.

**Il gate è interno:** prima della S1 il consiglio rilegge i sei contro
`bmad-check-implementation-readiness` come **checklist** — perimetro completo, flussi
senza buchi, stack deployabile, regole applicabili, sicurezza indirizzata. Ciò che
manca si corregge nella stessa seduta, col tetto dei cinque giri (§3.1, §6.1); al
quinto si procede alla S1 dichiarando cosa resta scoperto.

**`CLAUDE.md` e `AGENTS.md` restano fuori:** li mantiene il progetto, non questo
skill. Il project context prodotto qui è `project-context.md` in
`planning-artifacts/`, artefatto di lavoro e non configurazione del repo.

**Se i documenti esistono già, non si rigenerano:** vincolano (§7), e il consiglio
dice solo dove tacciono. Si producono solo i mancanti — il pre-flight dice quali.

Fallimento: codice scritto prima che i sei esistano; documenti prodotti dopo la
pagina, per copertura; ricerca fatta e non scritta; sicurezza rimandata alla slice
dopo; un elenco di convocati scelto a tavolino invece del consiglio intero; un workflow con
checkpoint invocato dentro il flusso.

### 4.0b Il controllo dei documenti: nessuno passa così com'è uscito

*(«controllo dei documenti», come per l'acciaio: si scalda e si raffredda il documento finché non
regge. In pratica tre passate di controllo — casi limite, domande di
approfondimento, lettura ostile — prima che quel documento valga come vincolo.)*

Un documento scritto in una seduta è una prima stesura, e una prima stesura entra in
produzione con dentro tutto ciò che nessuno ha ancora provato a rompere. Prima di
valere come vincolo, **i sei passano tre passate**, tutte in consiglio, tutte senza
una domanda all'owner.

| | Passata | Come |
|---|---|---|
| 1 | **Casi limite** | `bmad-review-edge-case-hunter` **invocato** su ogni documento: cammina ogni ramo e ogni confine e restituisce solo ciò che non è gestito. Si ferma solo su input vuoto — non è una domanda, è un errore |
| 2 | **Elicitazione — tutti i metodi applicabili** | `methods.csv` di `bmad-advanced-elicitation` come **modello**: quel workflow *è* un menu che chiede «scegli un numero da 1 a 5», e non si invoca. Si prendono i 71 metodi, si tengono **tutti quelli applicabili** a quel documento — non cinque proposti — e si applicano |
| 3 | **Review adversarial** | `bmad-review-adversarial-general` **invocato**, un passaggio ostile per documento. **Zero findings → si ri-analizza**, mai «ask for guidance»: se dopo la seconda passata resta zero, è un esito, si dichiara e si va |

**Quali metodi sono applicabili** lo decide il tipo di documento, e si dichiara:
pre-mortem e red team sull'architettura e sulla sicurezza; first principles e
Socratic sul PRD; percorsi utente e stati limite sull'UX; *Tree of Thoughts* dove le
strade sono più d'una e vanno confrontate, non scelte a naso. Un metodo scartato si
nomina in una riga — «non applicabile perché…» — così si vede la differenza fra
scartato e dimenticato.

**Gli esiti rientrano nel documento**, non in un elenco di note a margine: un caso
limite trovato e non recepito è peggio di uno non cercato, perché adesso qualcuno
sapeva. Ciò che si decide di non recepire diventa **varianza** (§11) con il perché.

**Il tetto dei cinque vale anche qui** (§3.1, §6.1): le tre passate girano fino a
cinque volte sullo stesso documento; al quinto si prende ciò che regge, si dichiara
cosa resta scoperto, e si va avanti. Il controllo dei documenti non è un cancello: è una forgiatura
che finisce.

**E il profilo lo restringe** (`autonomia.md` → *I tetti non si sommano*): sul
profilo `leggero` — landing, pagina singola, restyle — le tre passate girano
**una volta sola** per documento, ed è già più di quanto avesse chiunque prima.
Il giro successivo si guadagna: si riapre un documento solo se la passata
precedente ha prodotto una modifica **sostanziale**. Cinque per sei documenti,
moltiplicati per tre passate, non sono rigore: sono un pomeriggio di sedute che
l'owner paga senza vedere una riga.

Fallimento: documenti usati come vincolo senza le tre passate; il menu
dell'elicitazione presentato a qualcuno; cinque metodi invece di tutti quelli
applicabili; adversarial che restituisce zero findings e lo si prende per buono al
primo giro; casi limite trovati e archiviati fuori dal documento.

#### Il peso si alza quando arriva il back end — e non torna giù

I sei artefatti esistono dalla prima riga di codice, ma su una landing sono corti: il
perimetro è piccolo, non assente. Quando una slice introduce **il dietro** — auth
reale, dati che persistono, un'API, un ruolo, un pagamento — quei documenti non
bastano più nella forma in cui sono, e il piano a slice prescrive proprio **S2 back
office con accesso minimo reale** (§4.1): il salto è previsto dal piano, non è un
imprevisto.

1. **Il salto scatta quando la slice porta davvero il back end**, non quando qualcuno
   lo ipotizza. La S1 landing resta leggera anche se la S2 è già scritta nel piano.
2. **Prima di aprire quella slice, i sei si riaprono e si approfondiscono**
   (`bmad-spec`-style: stesso artefatto, non un secondo file) — architettura con
   confini veri, sicurezza con la superficie d'attacco della slice, UX con gli stati
   di errore e di accesso. Non si apre la slice e poi si documenta: sarebbe il back
   office costruito senza architettura.
3. **Il peso non torna giù:** le slice successive non tornano alla forma corta perché
   «la S3 è solo una pagina».
4. **G1 dichiara il salto** con una riga — cosa l'ha fatto scattare — e resta una
   **varianza** (§11).

Fallimento: S2 con auth e tabelle aperta sui documenti della landing; documenti
approfonditi *dopo* che il back office esiste; peso alzato «perché prima o poi
servirà».

### 4.1 `slice_plan` — verticale, consegnabile

*(una «slice» è una fetta verticale di prodotto: schermo, dati e logica di quella
funzione insieme, finita e utilizzabile da sola. «Verticale» perché taglia tutti
gli strati, invece di fare prima tutta l'impalcatura e poi tutto il resto.)*

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
- **Si apre una slice solo quando la precedente è consegnata *e l'owner l'ha
  chiesta*** (§4.3). Niente lavoro in parallelo su slice diverse dello stesso
  progetto, e niente S2 attaccata in coda alla S1 nella stessa passata.
- Ogni slice consegnata lascia il suo spec: è così che la S2 non contraddice la S1.
- **Il `slice_plan` si scrive tutto in G2, ma si *esegue* una riga per volta.**
  Pianificare tutte le slice costa una seduta e serve a progettare la S1 sapendo
  cosa arriva dopo; costruirle tutte prima che l'owner ne abbia vista una è la
  cosa che il vertical slice esiste per evitare.

### 4.2 Una slice = una spec eseguibile

La `slice_plan` non è un elenco di intenzioni: **ogni slice diventa una spec
eseguibile**, e il codice applicativo si scrive contro quella. Il taglio è quello di
`bmad-quick-dev` — *un singolo obiettivo utente shippabile* per spec — che è la definizione
stessa di slice verticale.

1. **La spec si genera con `bmad-spec`, in headless** (chiamata da skill = nessuna
   domanda, modalità express), **solo per la slice che si sta aprendo** — mai per
   tutto il piano in anticipo: una spec scritta oggi per una slice che parte fra
   due settimane è già vecchia quando serve, perché la slice prima le ha insegnato
   qualcosa (§4.3). Slug per slice — `<progetto>-s1-<nome>`,
   `<progetto>-s2-<nome>` — così ogni slice ha la sua cartella e riaprire lo stesso
   slug **aggiorna in place** preservando gli ID capability.
   **Headless non chiede, ma può rifiutare:** risponde con
   `error_code: "missing_slug"` se lo slug non arriva e `insufficient_intent` se
   l'input è troppo sottile. Non sono domande travestite e non si girano
   all'owner: `missing_slug` è un errore di chiamata e si corregge passando lo
   slug; `insufficient_intent` dice che i sei documenti non coprivano quella
   slice — si torna a G2 per il pezzo mancante (dentro il tetto dei cinque) e si
   richiama. Lo stesso vale per gli `HALT` su **input vuoto o illeggibile** dei
   due workflow di review nella controllo dei documenti: input vuoto è un bug di chiamata, si
   ripassa il documento, non si chiede niente a nessuno.
2. **Le `open_questions[]` non sopravvivono alla generazione.** In express ogni buco
   diventa una domanda aperta nel file: lì non può restare, perché non ha nessuno a
   cui andare (nessuna domanda all'owner) e perché una spec con domande aperte non è
   *Ready for Development*. Ognuna si chiude nello stesso giro — decisione del
   consiglio, marcata **assunzione**, con varianza (§11) se pesa. Una spec si dichiara
   pronta solo a `open_questions` vuote.
3. **I sei documenti (G2) sono la fonte:** vincolano tutte le
   slice e non si riscrivono a ogni giro. La spec di slice eredita perimetro, vincoli
   e non-obiettivi, e aggiunge solo ciò che quella slice deve fare.
4. **Ready for Development, o non parte:** ogni task con path e azione, AC in
   Given/When/Then, zero placeholder e zero TBD. Un `TODO` nella spec è lo stesso
   difetto del `TODO` nella pagina (§10) — qui blocca l'implementazione, lì la
   consegna.
5. **Il craft non entra nella spec eseguibile.** Le decisioni dichiarate — palette,
   `hue_sector`, `ink_family`, tipografia, griglia, superfici, hero, motion — vivono
   nel **DESIGN.md / spec di accompagnamento** (§10), e la spec di slice li
   **referenzia** in una riga. Duplicarli non aggiunge contratto: aggiunge un secondo
   posto dove diventano falsi, e fa sforare la misura per un motivo che non c'entra
   con il perimetro.
6. **Misura:** ~900–1600 token per spec, **contati sul contratto applicativo**, non
   sul craft (punto 5). Se sfora davvero, si guarda se dentro ci sono **due
   lavoro consegnato shippabili separatamente** — allora erano due slice, e la `slice_plan`
   si corregge. Se è un obiettivo solo che attraversa più strati, resta una spec:
   cross-layer non è multi-obiettivo.
7. **Chi fa cosa dentro la slice:** craft della pagina → Vesper (AF → Vera);
   endpoint, persistenza, auth di slice, logica di dominio → **`bmad-quick-dev`,
   invocato** sulla scheda eseguibile della slice (§4.2b). L'orchestrazione è di
   John (§4.4). Se è l'owner a lanciare quick-dev di sua iniziativa, si esegue
   com'è, dall'inizio: le fermate se le è scelte lui.
8. **A consegna fatta la spec resta** in `implementation-artifacts/` e vincola la
   slice dopo. Nessuna spec si hand-edita: si ri-deriva con `bmad-spec` sullo
   stesso slug.

### 4.2b Lo sviluppo si fa con `bmad-quick-dev` — invocato, entrando da `step-03`

Il codice applicativo della slice **lo scrive `bmad-quick-dev`**, e si invoca
davvero. Non è un'eccezione alla legge sui workflow che si fermano
(`autonomia.md`): è che **le sue fermate stanno tutte prima del punto in cui
entriamo**. Le sue porte sono in `step-01` (quale spec riprendere · chiarimento
dell'intento · albero sporco · multi-goal) e in `step-02` (gap · split ·
`[A] Approve | [E] Edit`); da `step-03` in poi l'unico `HALT` è su spec mancante
— che è un errore di chiamata, non una domanda.

Il ponte che ci porta lì è il **formato**, e va costruito o l'invocazione ricade
in `step-01`:

1. **La scheda eseguibile sta in `{implementation_artifacts}/spec-<progetto>-s<N>-<nome>.md`**
   e usa il `spec-template.md` **di quick-dev** (non il kernel di `bmad-spec`, che
   ha un altro formato e vive in `specs/spec-<slug>/`). Il kernel resta il
   **contratto** della slice; la scheda è la sua forma eseguibile, e ne è derivata,
   non un secondo contratto: dove divergono vince il kernel.
2. **`status: ready-for-dev` nel frontmatter.** È il campo su cui `step-01` instrada:
   con quel valore fa **EARLY EXIT diretto a `step-03-implement.md`**, e tutte le
   fermate di `step-01` e `step-02` non vengono mai raggiunte. Con `draft` finisce
   in `step-02` e si pianta sul `[A] Approve`.
3. **`Ask First:` resta vuoto** — o meglio, dice `nessuna: le decisioni si chiudono
   in consiglio`. Quel campo del template *genera* checkpoint («if any of these
   trigger during execution, HALT and ask the user»): scriverci dentro una
   decisione significa piazzare da soli, dentro la spec, la domanda all'owner che
   tutto il resto del flusso esiste per evitare. Le stesse decisioni vanno in
   **Always** (se sono invarianti) o in **Never** (se sono fuori perimetro).
4. **`open_questions` chiuse, zero `TODO`, zero TBD** (punti 2 e 4 sopra): una scheda
   che non è *Ready for Development* non regge l'ingresso da `step-03`, perché lì
   nessuno le chiuderà più.
5. **`step-04` fa la sua review** (Blind Hunter + Edge Case Hunter in subagent): è
   lavoro in più, non in conflitto con G3 — quella guarda il contratto e la
   richiesta dell'owner, questa guarda il codice. Se i subagent non fossero
   disponibili quel passo si ferma: allora si eseguono i due ruoli **inline**, non
   si gira il prompt all'owner.
6. **`step-04` escala all'umano oltre il quinto `review_loop_iteration`.** Lì vale
   il **tetto dei cinque** di questo skill (§6.1): non si escala — si prende ciò che
   regge, si dichiara cosa resta scoperto, si scrive la varianza (§11), si consegna.
7. **`step-05` offre push e PR.** L'offerta si lascia cadere: il push sta oltre
   il confine (`autonomia.md` → *L'unico confine che resta*) e non si fa senza che
   l'owner lo chieda. Non è una fermata — arriva a lavoro finito.

**Se la scheda non si riesce a portare a *Ready for Development*** (il contratto
non copre abbastanza), non si invoca quick-dev sperando che chieda: si torna a G2
per il pezzo mancante, dentro il tetto dei cinque, e si richiama. La disciplina di
quick-dev — `spec-template.md` e lo standard *Ready for Development* — vale
**anche** quando per qualunque ragione il workflow non parte: era già obbligatoria
quando era solo un modello.

Fallimento: quick-dev invocato senza spec file, e quindi entrato da `step-01` con
le sue domande; `status: draft` sulla scheda; una riga in `Ask First`; il prompt di
review di `step-04` girato all'owner perché mancavano i subagent; escalation al
sesto giro invece del tetto dei cinque; codice applicativo scritto a mano quando
quick-dev era invocabile.

### 4.3 Una slice per volta: si consegna la S1 e ci si ferma lì

Un progetto con landing e back office non si consegna a fine costruzione. **Si
apre la S1, si finisce, si consegna, e il lavoro finisce.** Le slice successive
partono quando l'owner le chiede.

Non è una deroga alla legge di autonomia: la legge vieta di **fermarsi in mezzo**
a un lavoro per chiedere qualcosa. Qui non si chiede niente e non si è in mezzo a
niente — la S1 è **finita**: documentata, implementata, approvata in G3, passata
al `close_check`, online da sola. Il flusso non si è fermato: è arrivato in fondo
a ciò che stava facendo. Quello che segue è un lavoro **nuovo**, e i lavori nuovi
li apre l'owner.

1. **Il piano è intero, l'esecuzione è di una riga.** G2 scrive tutto il
   `slice_plan` (§4.1) — serve a progettare la S1 sapendo cosa arriva dopo. Poi si
   apre **solo la S1**: una spec (§4.2), una implementazione, una approvazione, una
   consegna.
2. **La chiusura è una dichiarazione, mai una domanda.** Si dice cosa è consegnato,
   cosa resta nel piano e come riparte — in una riga, in voce:

   > Landing online in `apps/<slug>/`. Nel piano restano **S2 back office**
   > (accesso minimo reale + la schermata delle richieste che questa landing
   > genera) e **S3 <…>**. La S2 parte quando me lo dici.

   Vietato: «vuoi che proceda con la S2?», «confermi il piano?», «fammi sapere e
   continuo», un elenco di slice da spuntare. Quelle sono le domande di sempre con
   un cappello nuovo. La forma giusta espone **uno stato**, non una scelta:
   l'owner guarda la landing e decide da sé, che è il punto per cui esiste la
   consegna a slice.
3. **Come riparte.** Basta che l'owner nomini la slice, in qualunque forma («vai
   con il back office», «fai la S2», «ora l'area riservata»). Allora:
   - il `slice_plan` e i sei documenti **non si rifanno**: vincolano già (§7). Il
     pre-flight li ritrova, e G1 rilegge per prime le righe marcate `assunzione`
     (§7.1) e ciò che la S1 ha insegnato;
   - **se la slice porta il back end, il peso si alza prima di aprirla** — i sei si
     approfondiscono, non si duplicano (§4.0b → *Il peso si alza quando arriva il
     back end*). È la S2 back office il caso tipico: non è un imprevisto, è scritto
     nel piano;
   - spec della slice (§4.2), scheda eseguibile, `bmad-quick-dev` (§4.2b), G3,
     consegna, e **di nuovo stop**.
4. **Una slice per volta vale anche se l'owner ne chiede due.** «Fai S2 e S3»
   → si fa la S2, si consegna, si dichiara che la S3 è pronta a partire. La
   verifica intermedia è il motivo per cui esistono le slice; saltarla su richiesta
   generica le riduce a un modo di numerare i capitoli. Se l'owner insiste dopo
   averlo letto, vince la sua parola e si tirano dritte.
5. **Il tetto dei cinque non attraversa la consegna** (§6.1): la S2 è un contratto
   diverso, quindi il contatore dei rifiuti riparte. Correggere la S1 dopo la
   consegna, invece, eredita il conto — è lo stesso lavoro consegnato contro lo
   stesso contratto.

Fallimento: S2 costruita nella stessa passata della S1; landing consegnata senza
dire cosa resta nel piano; una domanda («procedo?») al posto della dichiarazione;
tutte le spec del piano generate in anticipo; la S2 aperta sui documenti della
landing senza alzare il peso; il `slice_plan` rifatto da zero a ogni ripresa.

### 4.4 L'orchestratore della slice è John

Dentro la slice qualcuno deve tenere l'ordine: quale agente parte, con cosa, e
quando la slice è chiusa. **Quel ruolo è di John (`bmad-agent-pm`), come
giurisdizione dentro il consiglio** — la stessa con cui presidia il perimetro in
G1. Non è una persona che prende la sessione: invocare `bmad-agent-pm` come skill
sostituirebbe la persona attiva e saluterebbe l'owner come John. John orchestra
**al tavolo**; la voce resta di Vesper, e le chiamate le esegue Vesper.

Cosa tiene John:

- **il `slice_plan`** — quale slice è aperta, quali sono chiuse, quali restano;
- **la sequenza dentro la slice** — spec (`bmad-spec`) → scheda eseguibile →
  craft (Vesper AF → Vera) e applicativo (`bmad-quick-dev`, §4.2b) → G3 → consegna;
- **chi si convoca su questa slice** — dal roster (`council_roster.py`), con le
  giurisdizioni che quella slice tocca davvero: un form porta Jane, un prezzo porta
  Dan Arrow, un login porta Rex e Jane insieme;
- **la chiusura** — è John a dire che la slice è finita, e la dichiarazione di
  §4.3 esce da lì.

Cosa **non** tiene John: **il craft non si vota** (`autonomia.md`), e non si
orchestra nemmeno. Palette, tipografia, griglia, hero, superfici e motion restano
di Vesper e Vera; John decide *l'ordine*, non *l'aspetto*. E non tiene il
perimetro nuovo: se durante la slice emerge qualcosa che non era nei documenti,
non lo aggiunge — è materiale per la slice dopo, o una varianza (§6).

Fallimento: una slice aperta senza che nessuno tenga la sequenza; `bmad-agent-pm`
invocato come skill dentro il flusso, con Vesper che sparisce dalla conversazione;
John che decide un font; due slice orchestrate insieme.

---

## 5. Implementazione

**Una slice sola, quella aperta** (§4.3). Vesper la pagina (AF → Vera); la parte
applicativa che non è craft frontend — endpoint, persistenza, auth della slice,
logica di dominio — la scrive **`bmad-quick-dev`, invocato** sulla scheda
eseguibile `ready-for-dev` così da entrare da `step-03` (§4.2b), seguendo
architettura e convenzioni del repo. Il canone (§13) vale lì come qui.

**Casi limite, per iscritto** prima di chiudere: stati vuoti, errore, caricamento;
testi lunghi/corti; molte/zero righe; mobile con tastiera aperta; offline se app.
L'elenco entra **nello spec di accompagnamento**, mai dentro la pagina (§10).

---

## 6. Approvazione

Lo stesso consiglio rientra sul risultato. È la risposta a «come ci accorgiamo che
aveva sbagliato?». Il criterio è uno, e non è il gusto:

> **Un lavoro consegnato è approvabile quando soddisfa tutte le richieste dei documenti
> BMAD che lo vincolano** — PRD, UX, architettura, project context, spec già
> consegnati — **più i craft-rules**. Se le soddisfa si approva **anche se
> qualcuno l'avrebbe fatto diversamente**: il gusto personale non è un veto.

- **Il rifiuto nomina la richiesta mancante.** «Non mi convince» non è un rifiuto:
  si dice *quale* punto dei documenti, *quale* requisito, *quale* regola di craft. Se
  nessuno sa nominarla, il lavoro consegnato passa.
- **Sul craft è rifiutabile solo ciò che si conta.** «Il craft non si vota»
  (`autonomia.md`) e «si rifiuta nominando la regola di craft» convivono a una
  condizione: la regola dev'essere **verificabile senza discutere di gusto** —
  un numero, una presenza, un esito di script. Rifiutabile: `viewport` assente ·
  overflow-x a 375 · più di 2 sezioni centrate · mono-allineamento · meno di 2
  `grid-column` espliciti · `clamp` degenere · `TODO` nel file · `palette_guard`
  che esce ≠ 0 (**exit 2 compreso: non misurato ≠ approvato**) · `register` o
  `ink_family` non dichiarati · tre job di fila nello stesso settore · nessuna
  `surface_texture`. **Non** rifiutabile: «quella palette non mi convince per un
  ristorante», «avrei usato un altro font», «l'hero è troppo scura». Il secondo
  elenco è gusto, e il gusto non è un veto: al massimo è una varianza. Un
  rifiuto che non si può verificare con uno script o con un conteggio **non
  conta nei cinque** — perché altrimenti i cinque giri si consumano a discutere.
- **Parla chi ha giurisdizione:** form → Jane; prezzo esposto → Dan Arrow;
  claim → Elena; WordPress → Niki; hosting o DNS → Rex; movimento → Vera. Chi tace
  su una cosa di sua competenza ha fallito, e il consiglio con lui.
- **Approvazione ≠ perfezione.** Il metro è il contratto, non l'ideale: se il
  PRD diceva tre servizi e la pagina ne presenta tre, il fatto che un membro ne
  avrebbe messi quattro non blocca — al massimo è una varianza.
- Ciò che emerge e **non** era nei documenti non è motivo di rifiuto: è materiale
  per la slice successiva, o una varianza (§11).

Convocazione: `bmad-party-mode --non-interactive`, obiettivo «approva o rifiuta questo
lavoro consegnato contro i documenti vincolanti e i craft-rules; motiva ogni
rifiuto nominando la richiesta non soddisfatta». **Vale come la review avversaria,
non in aggiunta:** è la stessa passata ostile, fatta da più teste con giurisdizioni
diverse.

### 6.0 La richiesta dell'owner è il primo documento

Quando i sei li ha scritti il consiglio (§4.0), G3 approva contro un contratto
che **il consiglio stesso si è dato**: se l'errore sta nel documento, il
lavoro consegnato gli è coerente e passa all'unanimità. §7.1 rimanda la correzione a
G1 «alla passata successiva» — ma su una landing one-shot quella passata non
arriva mai, e allora nessuno se ne accorge, mai.

Per questo l'approvazione ha **due metri, non uno**:

1. **Il contratto** — i documenti vincolanti + i craft-rules (§6).
2. **La richiesta originale dell'owner, testuale**, riletta com'è arrivata: il
   lavoro consegnato fa la cosa che l'owner ha chiesto? Le letture dichiarate in G1
   («l'ho letta come X, non Y») reggono ancora, ora che la pagina esiste?

Se i due metri divergono, **non vince il documento**: vince la richiesta, il
documento si **emenda** (§7.1) e la divergenza è una **varianza** — perché è la
prova che una lettura di G1 era sbagliata, ed è l'unico momento in cui si può
vedere. Un lavoro consegnato perfettamente conforme a un PRD che ha frainteso la
richiesta è il fallimento più caro di tutto il flusso, ed è invisibile a
chiunque guardi solo il contratto.

Fallimento: G3 che rilegge solo i documenti; una lettura dichiarata in G1 mai
più verificata contro la pagina finita; un'assunzione promossa a fatto perché
il lavoro consegnato la rispetta.

### 6.1 Il rifiuto ha un tetto: cinque

Un consiglio che può rifiutare all'infinito non è esigente, è un ciclo che non
termina — e senza nessuno fuori dal flusso a interromperlo, gira finché non finisce
il tempo. Stessa forma del tetto sui rimandi della ricerca (§3.1), stessa ragione.

1. **Massimo cinque rifiuti** per lo stesso lavoro consegnato. Ogni rifiuto nomina la
   richiesta mancante e **quella** si corregge: chi rifiuta senza nominarla non ha
   rifiutato, e il lavoro consegnato passa (§6).
2. **Un rifiuto vale una volta sola — ma una regressione non è una ripetizione.**
   La stessa richiesta mancante non può motivare due rifiuti: se dopo la correzione
   qualcuno la ripropone tale e quale, il giro non conta. Rifiuti che si spostano di
   poco a ogni passata sono gusto travestito da contratto, e il gusto non è un veto.
   **Diverso è quando la correzione l'ha rotta di nuovo:** se sistemare Y ha
   ririotto X, quel rifiuto è valido — X ora è davvero mancante, e trattarlo come
   ripetizione significherebbe consegnare X rotto senza che nessuno lo dica.
2b. **L'oscillazione si chiude alla seconda andata e ritorno.** Se X e Y si
   escludono a vicenda — sistemare l'uno rompe l'altro, due volte — il problema non
   è il lavoro consegnato: è che il contratto chiede due cose incompatibili. Si sceglie
   **quale delle due cede**, si dichiara perché, e la scelta è una **varianza**
   (§11). Continuare a girare tra X e Y consuma i cinque giri per scoprire una cosa
   che si sapeva al secondo.
3. **Al quinto si consegna comunque, dichiarando cosa resta aperto.** Non si torna
   dall'owner a chiedere il permesso di consegnare: si scrive in una riga quale
   richiesta non si è riusciti a soddisfare e perché, si marca come **varianza**
   (§11), e la si porta nella slice successiva. Un lavoro consegnato che soddisfa il
   contratto meno un punto dichiarato vale infinitamente più di un lavoro consegnato che
   non esce.
4. **Il conto si scrive** nello spec, come per i rimandi: zero rifiuti sempre
   significa che nessuno guarda davvero; cinque spesso significa che il problema sta
   nei documenti, non dentro quello che consegni.
5. **Il tetto è per lavoro consegnato, non per sessione:** non si azzera rigenerando la
   pagina, o basterebbe ripartire da capo per ricominciare a girare. **Il contatore
   riparte solo quando cambia il contratto:** una richiesta nuova dell'owner, una
   slice diversa, un documento emendato. Una correzione dello stesso lavoro consegnato contro
   lo stesso contratto eredita il conto — anche se arriva mezz'ora dopo la consegna.

Fallimento: sesto rifiuto sullo stesso lavoro consegnato; rifiuto che ripete una richiesta
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
   **G1** il percorso praticabile più vicino, lo dichiara nei documenti e lo scrive
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

### 7.1 I documenti che ti sei scritta da sola

Quelli prodotti dal consiglio in G2 (§4.0) **vincolano come gli altri**: lo stack
è obbligatorio anche se l'hai deciso tu ieri. Ma sono nati pieni di **assunzioni
marcate**, e un'assunzione promossa a legge senza che nessuno la guardi più è peggio
dell'assenza del documento.

- **Il pre-flight le rilegge per prime**, insieme alle varianze: le righe marcate
  `assunzione` nei documenti generati sono la prima cosa che G1 vede alla passata
  successiva.
- **G1 le riconferma o le emenda**, sull'evidenza nuova (il repo è cresciuto, il sito
  del cliente dice altro, la S1 ha insegnato qualcosa). Riconfermare è una riga;
  emendare è una decisione + una varianza (§11) — mai una domanda all'owner.
- **Un'assunzione verificata smette di essere tale:** si riscrive come fatto, e la
  varianza che la portava si chiude. È l'unico modo in cui quei documenti migliorano
  invece di irrigidirsi.
- **G3 approva contro i documenti, non li giudica** (§6): se un documento è sbagliato
  il posto per accorgersene è qui, non in approvazione — dove un errore di documento
  diventa un lavoro consegnato coerente con l'errore.

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

Non confondere i piani: nelle decisioni di design `hero_copy` è **dove** sta il testo
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
| Contiene | solo il prodotto: copy reale, dati verosimili, zero marcatori | documenti usati o la loro assenza, decisioni dichiarate, casi limite, canone applicato, requisiti per il backend, **`dati_verosimili:`** — cosa è inventato e dove |
| Non contiene mai | `TODO` · «da sostituire» · note di processo · elenchi di dati fittizi · `lorem ipsum` | istruzioni all'owner **al posto** della riga in chat: l'elenco documenta, l'avviso si dà comunque a voce |

- **Il lavoro consegnato è finito, mai «da completare».** Prezzi, orari, indirizzi e
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
- **La chat sparisce, il sito resta — quindi la riga vive anche nel DESIGN.md.**
  Dire i dati verosimili *solo* in conversazione appende la catena al canale più
  volatile che ci sia: sessione chiusa, e resta un `index.html` con recapiti
  inventati e nessuna traccia di **quali**. Perciò accanto al lavoro consegnato, nel
  `DESIGN.md` (o nello spec), sta una voce **`dati_verosimili:`** — elenco secco
  di cosa è stato inventato e dove: telefono, email, indirizzo, P.IVA, prezzi,
  orari, recensioni. Non è la nota di sostituzione vietata sopra: quella sporca
  **l'artefatto**, questa sta nel documento di accompagnamento, che è già il
  posto di documenti usati, decisioni e casi limite. La riga in chat resta comunque:
  l'una avvisa adesso, l'altro risponde fra sei mesi a «ma questo numero è
  vero?».
- **Il telefono si sceglie perché non possa squillare da nessuno:** prefissi non
  assegnati, `+39 0X XXXX` inventati fuori dai piani di numerazione reali, email
  sul dominio del brand fittizio. Un recapito verosimile *e* attribuito a una
  persona reale non è un dato di esempio: è il numero di qualcuno su un sito che
  non è suo.
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

**Quando no:** per le decisioni ordinarie — i documenti dicono già *cosa* si è deciso.
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
   stack che il repo rende più praticabile, si dichiara nei documenti con una riga di
   motivo e si lascia una **varianza** (§11), che è il posto dove la prossima pagina
   va a leggerla. I file di configurazione del progetto (`CLAUDE.md`, `AGENTS.md`)
   si **leggono**: li mantiene il progetto, non questo skill.

---

# Le leggi di fondo

## 13. Il canone, quando mancano architettura **e** project context

*(il «canone» sono le sei regole di scrittura del codice qui sotto: valgono
quando il progetto non ne detta di proprie.)*

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

## 14. Sono i workflow BMAD — invocati dove il percorso non si ferma, copiati dove si ferma

Il costo non è mai stato nei singoli workflow: è nella **sequenza completa applicata
sempre**, e nelle **fermate** che si incontrano **sul percorso che si usa** — non in
quelle che il workflow contiene da qualche altra parte. La tabella verificata vive in
`autonomia.md` → *I procedimenti che si fermano*; qui basta la mappa
di chi fa cosa:

| Passo | Chi |
|---|---|
| Ricerca dominio + marketing (scritte) | Vesper (§2) |
| PRD · documento UX · architettura | `bmad-prd` · `bmad-ux` · `bmad-architecture`, **invocati in headless** dentro l'obiettivo G2 |
| Project context | il consiglio, come `project-context.md` (§4.0) |
| Controllo dei documenti | `bmad-review-edge-case-hunter` e `bmad-review-adversarial-general` **invocati**; `methods.csv` dell'elicitazione come modello (§4.0b) |
| Spec di slice | **`bmad-spec`** headless, slug `<progetto>-s<N>-<nome>` (§4.2) — **solo la slice aperta** |
| Codice applicativo | **`bmad-quick-dev` invocato**, entrando da `step-03` con la scheda `ready-for-dev` (§4.2b) |
| Craft della pagina | Vesper AF → **`agent-web-animations`** |
| Orchestrazione della slice | **John** (`bmad-agent-pm`) come giurisdizione al tavolo, mai come persona invocata (§4.4) |
| Slice pesante (S2 con auth e dati) | **`bmad-create-story`** · **`bmad-code-review`** |
| Progetto con un team che li legge | **`bmad-sprint-planning`** e i workflow BMAD interi |

**Si sale di peso, non si parte pesanti** — ma i documenti esistono da subito (§4.0):
è il loro peso a crescere, non il loro numero.

---

## Fallimenti

**Vincoli:** pagina in uno stack diverso da quello dell'architettura; PRD ignorato
«perché la sezione veniva meglio così»; page spec riscritta dal seed; stack scelto
per comodità quando il repo o `docs/` ne dichiarano un altro; lavoro consegnato che non
dichiara né i documenti usati né la loro assenza.

**Processo:** analisi autonoma partita in silenzio, o con l'avviso appiccicato in
coda; avviso dato quando i documenti c'erano (allarme falso: si guarda l'esito del
pre-flight, non l'istinto); avviso scritto come richiesta di permesso («fermami se…»);
consiglio che invece di decidere produce domande da girare all'owner; party che
sceglie font e palette (il craft non si vota); ricerca insufficiente accettata invece
che rifatta; rimando che non nomina cosa manca; sesto rimando sullo stesso lavoro
invece della decisione sull'evidenza; lavoro fermato al quinto rimando aspettando
l'owner; rifiuto in approvazione che non nomina la richiesta mancante; **sesto rifiuto
sullo stesso lavoro consegnato**, o rifiuto che ripete tale e quale una richiesta già
corretta — ma anche una **regressione** scambiata per ripetizione e quindi taciuta;
due andate e ritorni fra richieste incompatibili senza scegliere quale cede; **un
workflow con checkpoint invocato dentro il flusso** — o **`bmad-quick-dev` invocato
senza scheda `ready-for-dev`**, che è lo stesso difetto: entra da `step-01` e chiede
—, o la sua disciplina saltata
perché non lo si è invocato; `bmad-agent-pm` invocato come persona e Vesper che
sparisce; una slice con back end aperta senza promuovere il ramo;
`open_questions` lasciate in una spec dichiarata pronta; assunzioni dei documenti
auto-generati mai più rilette; **una qualsiasi domanda all'owner in mezzo al flusso**
(`references/autonomia.md`).

**Contenuti:** lorem ipsum o copy da landing generica quando i testi non erano
forniti; servizi inventati mentre il sito ne elencava altri; stock generico quando
il cliente aveva foto sue; restyle che somiglia al sito vecchio; testi dell'owner
riscritti «perché suonavano meglio».

**Artefatti:** `TODO`, «da sostituire» o blocchi di dati fittizi dentro quello che consegni;
dati verosimili non segnalati in chat; assunzioni scritte come fatti; assunzione
decisa in consiglio e mai finita in `docs/varianze/`; varianza lunga una pagina, o
una varianza per ogni decisione ordinaria.

**Slice:** slice che non sta in piedi da sola; auth completa come S1; **S2
costruita nella stessa passata della S1**, o aperta prima che l'owner l'abbia
chiesta; consegna della S1 senza dichiarare cosa resta nel piano; «vuoi che
proceda con la S2?» al posto di quella dichiarazione; tutte le spec del piano
generate in anticipo.

**Canone:** senza architettura né project context, logica di dominio nel template,
`innerHTML` su dati non fidati, chiavi nel bundle, cartelle per strato tecnico
invece che per feature, astrazione inventata su due occorrenze, framework tirato
dentro per una pagina che non lo chiedeva.
