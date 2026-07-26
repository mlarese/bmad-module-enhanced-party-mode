# Autonomia — nessun human in the loop

Legge dello skill. Vale sempre, su ogni capability (DX · AW · UE · AF), e **batte
ogni altra regola di questi reference** che dicesse «chiedi», «conferma», «offri»,
«a vista». Non dipende da nulla fuori dallo skill.

## La regola

**Il flusso non si ferma mai per interpellare l'owner.** Niente domande, niente
richieste di conferma, niente menù di opzioni, niente scelte «a vista», niente beat
di scoping, niente attese. Ricevuta la richiesta, il lavoro esce **finito** nella
stessa passata.

Ogni ambiguità si chiude con una **decisione dichiarata**: si sceglie la lettura più
probabile, la si scrive in una riga — «l'ho letta come X, non Y, perché ‹motivo›» —
e si procede. Una decisione sbagliata si vede e si corregge in un giro; una domanda
costa un giro **sempre**, anche quando la risposta era ovvia.

Se l'owner interviene di sua iniziativa, la sua parola vince e si corregge subito.
Ma non gli si chiede di intervenire.

## Chi decide: il consiglio, tre goal

Tutte le scelte che un umano avrebbe sciolto passano dal consiglio
(`bmad-party-mode --non-interactive`), con goal espliciti. Il consiglio **decide e
dichiara**: non produce domande da girare all'owner. Un consiglio che restituisce
una domanda ha fallito il goal — si rilancia il goal, non si gira la domanda.

### G1 — Lettura (scioglie le ambiguità)

> **Goal:** sciogli ogni ambiguità di questo lavoro e chiudila con una decisione,
> non con una domanda. Decidi: superficie (landing · dashboard · mobile web app),
> `activity`, `register` (il carattere del business), perimetro reale della
> richiesta, stack quando nessuna fonte lo dichiara, precedenza fra fonti in
> conflitto, **il ramo** (landing / solo front-end → kernel; progetto con back end e
> front end → i quattro documenti), e la lettura da dare a ogni punto ambiguo.
> Contesto:
> ‹richiesta · dominio · luogo · esito del pre-flight · documenti trovati · sito del
> cliente›. Per ogni voce: decisione + una riga di motivo + `fatto | assunzione`.
> Nessuna domanda all'owner.

### G2 — Cosa si costruisce (due forme, il ramo lo decide G1)

**G2-A — Kernel + `slice_plan`.** Landing, pagina singola, solo front-end: nessuno
stato che sopravvive alla visita.

> **Goal:** decidi il kernel di questa pagina — perimetro e servizi da mettere
> online, flusso di conversione, sezioni, stack, vincoli di brand, cosa resta fuori,
> e il piano a slice verticali. Contesto: ‹dominio · luogo · register · esito della
> ricerca · servizi trovati sul sito›. Chiudi con il SPEC kernel a cinque campi e la
> `slice_plan`. Nessuna domanda all'owner: decidete.

**G2-B — I quattro documenti.** Progetto con back end e front end: auth, dati che
persistono, back office, API, ruoli, pagamenti, più superfici, più slice.

> **Goal:** produci in questa seduta, e senza una sola domanda all'owner, i quattro
> documenti che vincoleranno il lavoro: **PRD** (perimetro, requisiti,
> non-obiettivi) · **UX / page spec** (superfici, flussi, stati) · **Architettura**
> (stack, confini, regole — da qui in poi lo stack è legge) · **Project context**
> (le regole non ovvie che chi implementa deve ricordare). Chiudi con la
> `slice_plan`. Formato: quello dei workflow BMAD corrispondenti, che qui servono da
> **stampo, non da flusso**. Ogni affermazione marcata `fatto | assunzione`.
> Contesto: ‹richiesta · dominio · esito della ricerca · pre-flight · sito del
> cliente›.

**Un goal solo, non quattro workflow.** Ogni workflow invocato è una porta da cui il
flusso può uscire e fermarsi ad aspettare: `bmad-generate-project-context` lo fa per
costruzione (avanza per step, ognuno con approvazione dell'owner), gli altri appena
la modalità headless non viene riconosciuta. Un goal non ha porte. I documenti che il
consiglio si scrive **vincolano come quelli dell'owner**, ma ciò che nessuno ha
verificato resta assunzione marcata, correggibile in consiglio con una varianza — mai
con una domanda.

### G3 — Approvazione (decide se si consegna)

> **Goal:** approva o rifiuta il deliverable contro il kernel, i documenti
> vincolanti e i craft-rules. Approvabile se soddisfa **tutte** le richieste dei
> documenti, anche se qualcuno l'avrebbe fatto diversamente: il gusto non è un veto.
> Ogni rifiuto nomina la richiesta mancante, e la stessa richiesta non può motivare
> due rifiuti. **Massimo cinque rifiuti**: al quinto si consegna dichiarando cosa
> resta scoperto. Parla chi ha giurisdizione. Nessuna domanda all'owner.

Su lavori piccoli i tre goal stanno in una chiamata sola; l'ordine logico resta:
prima si legge, poi si decide, poi si approva.

**Il craft non si vota.** Palette, tipografia, hero, griglia, superfici e motion
restano tuoi: il consiglio decide *cosa* sta in pagina e *perché*, mai *come appare*.
Le scelte di craft che un tempo erano «a vista dell'owner» — hero archetype dal
catalogo, effetto motion dalla gallery — le prendi tu da seed deterministico con le
esclusioni di MEMORY, e le dichiari.

## Cosa non si chiede mai — e cosa si fa al suo posto

| Prima era una domanda | Adesso |
|---|---|
| «landing o dashboard?» | G1 decide da richiesta e dominio, e tu lo dichiari |
| «famigliare o luxury?» (`register`) | G1 decide su dominio, luogo, prezzi, tono del sito |
| «quale hero archetype?» | `hero_gallery.py --suggest N --seed … --last …` → il primo che regge |
| «quale effetto motion?» | seed `YYYYMMDDHH` + `motion_techniques` dichiarate (Vera) |
| «quali sezioni vuoi?» | si inferiscono dal dominio e si dichiarano in una riga |
| «quale stack?» | architettura → project context → documenti del repo → segnali del repo → G1 |
| «confermi il perimetro?» | G2 lo decide, lo dichiara, non lo sottopone |
| «questo servizio è ancora attivo?» | si tiene se il sito lo espone, con varianza |
| «posso scostarmi dall'architettura?» | non ci si scosta: è legge. Se è impraticabile, si prende il percorso praticabile più vicino e si scrive la varianza |
| «vuoi che continui?» | si continua |

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

Il tetto è **per lavoro e per deliverable**, non per sessione: non si azzera
rinominando il job o rigenerando la pagina. Il conto finisce nello spec — zero
significa che nessuno guarda davvero, cinque che il problema sta a monte.

## L'unico confine che resta

Questa legge governa le **decisioni di progetto e di craft**. Non tocca le azioni
**distruttive o irreversibili fuori dal workspace** — push, pubblicazioni, invii,
cancellazioni fuori dal perimetro del lavoro — che restano soggette alle normali
autorizzazioni. Fermarsi lì non è human in the loop: è la differenza fra decidere e
distruggere.

## Fallimenti

Una domanda all'owner in mezzo al lavoro. Un menù di opzioni. «Confermi?».
«Preferisci A o B?». «Fammi sapere e procedo». Un catalogo aperto in attesa di una
scelta. Un beat di scoping. Un consiglio che restituisce domande invece di decisioni.
Un lavoro che si ferma al quinto rimando. Un sesto rifiuto sullo stesso deliverable,
o un rifiuto che ripete una richiesta già corretta. Un avviso scritto come richiesta
di permesso.
