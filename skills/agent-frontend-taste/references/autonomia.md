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
> conflitto, e la lettura da dare a ogni punto ambiguo della richiesta. Contesto:
> ‹richiesta · dominio · luogo · esito del pre-flight · documenti trovati · sito del
> cliente›. Per ogni voce: decisione + una riga di motivo + `fatto | assunzione`.
> Nessuna domanda all'owner.

### G2 — Kernel + `slice_plan` (decide cosa si costruisce)

> **Goal:** decidi il kernel di questa pagina — perimetro e servizi da mettere
> online, flusso di conversione, sezioni, stack, vincoli di brand, cosa resta fuori,
> e il piano a slice verticali. Contesto: ‹dominio · luogo · register · esito della
> ricerca · servizi trovati sul sito›. Chiudi con il SPEC kernel a cinque campi e la
> `slice_plan`. Nessuna domanda all'owner: decidete.

### G3 — Approvazione (decide se si consegna)

> **Goal:** approva o rifiuta il deliverable contro il kernel, i documenti
> vincolanti e i craft-rules. Approvabile se soddisfa **tutte** le richieste dei
> documenti, anche se qualcuno l'avrebbe fatto diversamente: il gusto non è un veto.
> Ogni rifiuto nomina la richiesta mancante. Parla chi ha giurisdizione. Nessuna
> domanda all'owner.

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

## Quando la ricerca non regge

Il rimando ha un tetto di **cinque** giri. Al quinto non si porta la questione
all'owner: si **decide con l'evidenza migliore disponibile**, si dichiara in una riga
quale delle tre cose mancava (domanda mal posta · fonti inesistenti · dato che solo
l'owner ha) e si scrive la varianza. Il lavoro esce comunque.

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
Un lavoro che si ferma al quinto rimando. Un avviso scritto come richiesta di
permesso.
