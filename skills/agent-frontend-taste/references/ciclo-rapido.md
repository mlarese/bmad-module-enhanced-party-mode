# Ciclo rapido — la bozza grafica subito, dalle specifiche

*(«ciclo» = tutto quello che succede fra la richiesta dell'owner e la pagina
consegnata. Ce ne sono due, e li sceglie l'owner in una riga, prima che parta
niente.)*

Il flusso completo (`implementation-handoff.md`) scrive **sei documenti**, li
passa a tre controlli e li fa approvare da un consiglio: è il modo giusto di
costruire un prodotto, e su un back office non si tratta. Ma su una landing
l'owner spesso non vuole un prodotto documentato: vuole **vedere** come viene, e
vuole vederlo adesso.

Per quello c'è il **ciclo rapido**: le stesse decisioni si prendono lo stesso —
solo **a mente**, condensate in sei righe invece che in sei file — e il primo
artefatto che l'owner riceve è la **bozza grafica**, non il PRD.

Il craft non cambia di una virgola. Quello che si taglia è il **procedimento
attorno**, non la qualità di ciò che esce.

---

## 1. La domanda d'ingresso — l'unica, e sta prima del lavoro

Su un **lavoro nuovo di craft** (una landing, una pagina, un sito, una app: le
capability DX e AF) la prima cosa che esce non è il lavoro: è **una riga con due
opzioni**.

> **Rapido o completo?**
> **① Rapido** — niente PRD, niente consiglio, niente review avversaria: decido
> io, ti dichiaro le scelte in sei righe e ti do la **bozza grafica** subito.
> **② Completo** — sei documenti, controlli e approvazione del consiglio prima
> della pagina: più lento, ma resta scritto tutto ciò che vincola le slice dopo.

- **Due opzioni, non un menù.** Nessuna terza via, nessun sotto-menù, nessuna
  domanda di contorno («che colori preferisci?», «quale hero?»): quelle restano
  vietate in entrambi i cicli.
- **Si chiede una volta per lavoro.** Scelto il ciclo, vale fino alla consegna e
  **anche per le correzioni** che l'owner chiede su quella pagina. Richiedere a
  ogni giro è la fermata a metà lavoro che la legge vieta.
- **Non si chiede quando la risposta c'è già.** «Fammi una bozza al volo»,
  «veloce», «buttami giù la grafica» → rapido, si parte e lo si dichiara.
  «Fammelo per bene», «col consiglio», «voglio i documenti», o una richiesta che
  porta back end, auth o dati che persistono → completo, si parte e lo si
  dichiara. La domanda esiste per l'ambiguo, non per riconfermare l'ovvio.
- **Non si chiede sulle correzioni piccole.** Un ritocco su una pagina che esiste
  già non apre un ciclo: si fa.
- **Se l'owner risponde altro** (aggiunge specifiche invece di scegliere), quella
  è la risposta: **decidi tu** dalla lettura più probabile — pagina sola → rapido,
  back end → completo — e lo dichiari in una riga. Non si ri-chiede.
- **Se non c'è nessuno che possa rispondere, non si chiede.** Chiamata headless o
  non interattiva, `--non-interactive`, invocazione da un altro skill, o una
  richiesta che dice «senza farmi domande» / «edit files now»: lì la domanda non
  è un gate, è una fermata che nessuno scioglierà. Si sceglie **rapido** su una
  pagina e **completo** se la richiesta porta il dietro, lo si dichiara in una
  riga e si va. Una domanda fatta a un chiamante che non parla è il fallimento
  peggiore dei due, perché blocca senza nemmeno lasciare una decisione.

**Perché questa domanda non viola la legge di autonomia.** La legge
(`autonomia.md`) vieta di **fermarsi in mezzo** a un lavoro per far rispondere un
umano. Qui non c'è niente in mezzo: non è ancora partito niente, la domanda costa
una riga, ha due opzioni e riguarda **quanto deve costargli il lavoro** — che è
l'unica cosa che l'owner non può decidere leggendo il risultato dopo. Dentro il
ciclo scelto la legge vale intera: nessuna domanda, nessun menù, nessuna attesa,
fino alla consegna.

---

## 2. Cosa cambia, e cosa no

| Passo | Ciclo completo | Ciclo rapido |
|---|---|---|
| Pre-flight `bmad_context.py` | sì | **sì** — se documenti vincolanti esistono, vincolano lo stesso |
| Avviso di apertura (§1.1) | sì | **sì**, in due righe (§4) |
| Ricerca dominio + marketing | due file in `planning-artifacts/` | **a mente**, condensata nel blocco `brief:` del `DESIGN.md` |
| Batch ≥30 in rete | sì (`hero_sample.py`) | **no**: cataloghi locali, e il numero vero si dichiara come batch mancante |
| Consiglio (G1 · G2 · G3) | tre sedute `bmad-party-mode` | **nessuna**: decide Vesper, e dichiara |
| I sei documenti | sei file | **sei righe** dentro il `DESIGN.md` (§3) |
| Controllo dei documenti — casi limite · elicitazione · adversarial | tre passate per documento | **nessuna** |
| `slice_plan` · `bmad-spec` · `bmad-quick-dev` | sì | **no**: il ciclo rapido copre la pagina, non il dietro (§5) |
| **`craft_lock.py` prima di scrivere** | sì | **sì** |
| **Cataloghi eseguiti** (`accent_pool` · `font_pool` · `shape_pool` · `hero_gallery --suggest` · `craft_axes`) | sì | **sì** |
| **`repeat_guard` + `close_check` a `0`** | sì | **sì** |
| **`palette.html`** | sì | **sì** |
| **Responsive · cookie · copy vero · zero `TODO`** | sì | **sì** |
| Movimento | Vera invocata (`agent-web-animations`) | **movimento essenziale scritto da Vesper** (reveal allo scroll + hover, `prefers-reduced-motion`); Vera si invoca se l'owner la chiede |
| Registro del consiglio | una riga per seduta | **una riga sola**, `--goal rapido` (§6) |
| Riga di onestà sui dati verosimili | sì | **sì** |

**La regola sotto la tabella:** si taglia ciò che costa **sedute e file**, non ciò
che costa **secondi**. Lock, cataloghi e `close_check` sono secondi di macchina e
sono l'intera differenza fra una bozza e un template AI; il consiglio e i sei
documenti sono la mezza giornata. Un «ciclo rapido» che salta il lock ha tagliato
la cosa sbagliata: è tornato a indovinare.

---

## 3. Il brief mentale: sei righe, non sei file

Le decisioni dei sei documenti **si prendono lo stesso** — è la parte «valutando
mentalmente come generarlo in maniera completa». Quello che cambia è dove
finiscono: sei righe in testa al `DESIGN.md`, sotto `brief:`, ognuna marcata
`fatto | assunzione`.

```yaml
ciclo: rapido        # ← in un posto solo: fuori dal brief, che in ciclo completo non c'è
brief:
  cosa: <cosa fa davvero il business, con le parole del settore>        # assunzione
  per_chi: <chi compra, e l'obiezione che lo blocca>                    # assunzione
  perimetro: <le sezioni che ci sono — e le due o tre che NON ci sono>  # fatto
  conversione: <form | telefono | prenotazione, con o senza acconto>    # fatto
  stack: <come si apre: HTML statico, o quello che il repo impone>      # fatto
  sicurezza: <cosa raccoglie la pagina · cosa resta requisito del back end>
```

- **Sei righe, non sei paragrafi.** Se una non sta in una riga, quel lavoro non
  era da ciclo rapido.
- **Perché si scrivono, se il ciclo è rapido:** una decisione presa a mente e non
  scritta non è verificabile fra sei mesi, e la chat sparisce. Costano due minuti
  e sono ciò che separa una bozza rapida da una pagina improvvisata.
- **I non-obiettivi valgono quanto il perimetro.** «Niente blog, niente
  e-commerce, niente area riservata» in una riga evita l'unico equivoco che una
  bozza produce davvero: l'owner che pensa manchi qualcosa.
- **Il flusso di conversione non è grafica, è la pagina.** Se non lo decidi qui,
  lo decide il layout per caso (`implementation-handoff.md` §4.0).

---

## 4. L'avviso di apertura, versione corta

Resta obbligatorio (`implementation-handoff.md` §1.1), e dice **cosa** e
**quanto** — ma in due righe, perché altrimenti l'avviso costa più del ciclo:

> **Ciclo rapido.** Niente PRD, niente consiglio, niente review avversaria:
> perimetro, testi e stack li decido io e te li scrivo in sei righe nel
> `DESIGN.md`. **Quello che perdi:** il controllo incrociato, i casi limite che
> nessuno ha camminato, la ricerca scritta per le slice dopo.
> Contatti, prezzi e orari saranno **verosimili ma non veri** — te lo dico qui
> perché nella pagina non ci sarà scritto.

- **Si dice cosa si perde, non solo cosa si risparmia.** Un owner che sceglie
  «rapido» senza sapere che sta rinunciando ai casi limite ha scelto un'etichetta,
  non un ciclo.
- **È una dichiarazione:** si dice e si prosegue nella stessa risposta.
- **Se il pre-flight *trova* dei documenti, «niente PRD» è falso e non si dice.**
  L'avviso si restringe a ciò che manca davvero, come in ciclo completo
  (`implementation-handoff.md` §1.1 → *Vale anche parzialmente*): con un PRD già in `planning-artifacts/` la riga
  diventa «il PRD c'è e vincola; quello che non faccio è il consiglio, i casi
  limite e la review avversaria». Un avviso che annuncia l'assenza di un
  documento che esiste è la sola cosa peggiore di non darlo: è falso, e il
  documento poi vincola comunque.

---

## 5. Il confine: il ciclo rapido copre la pagina, non il dietro

**Copre:** landing, pagina singola, piccolo insieme di pagine statiche, restyle,
bozza grafica di una schermata.

**Non copre:** autenticazione, dati che persistono, API, ruoli, pagamenti, back
office. Lì i sei documenti non sono burocrazia: sono la differenza fra un back end
progettato e uno indovinato, e OWASP dal primo giorno non si taglia
(`implementation-handoff.md` §4.0b → *Il peso si alza quando arriva il back end*).

Se la richiesta porta il dietro **e** l'owner ha scelto rapido:

1. si consegna la **pagina** in ciclo rapido — è ciò che ha chiesto e la vede oggi;
2. si **dichiara** in una riga che la parte con auth/dati resta fuori e chiede il
   ciclo completo: «la landing è qui; il back office non lo apro in rapido, perché
   auth e dati senza architettura si pagano dopo — dimmi e parte il completo».
   È uno **stato**, non una domanda: detto quello, il lavoro è chiuso.

**Il passaggio da rapido a completo non butta via niente.** Se l'owner poi vuole
il ciclo completo su quella stessa pagina: lock, `DESIGN.md` e pagina restano e
valgono, il `brief:` diventa il punto di partenza dei sei documenti, e la pagina
si rilegge in G3 contro di loro. Il contrario — completo che si degrada a rapido a
metà strada — non esiste: i documenti già scritti vincolano (§7).

---

## 6. Quello che il ciclo rapido non taglia mai

Sono gesti da secondi, e sono l'intera ragione per cui la bozza non sembra fatta
da un generatore:

1. **Il seed col progetto dentro:** `YYYYMMDDHH-<slug>`, passato a tutti i
   cataloghi. Senza lo slug, due bozze fatte nella stessa ora escono identiche.
2. **Il lock prima di scrivere una riga:**
   `uv run scripts/craft_lock.py --project <slug> --seed … --surface marketing --out apps/<slug>/craft-lock.json`.
   **Senza lock non si consegna**, in nessuno dei due cicli.
3. **I cataloghi si eseguono, non si citano:** `accent_pool --suggest`,
   `font_pool`, `shape_pool`, `hero_gallery --suggest`, `craft_axes`. Se non li
   lanci decide il pregiudizio, ed è misurato dove va a finire — terracotta,
   pillola, `DM Mono`, griglia a rail. Sono i cataloghi a rendere *possibile* il
   ciclo rapido: la decisione non è veloce perché è superficiale, è veloce perché
   il sorteggio è già fatto.
4. **La hero si firma** `data-hero="<id>"`, o l'archetipo del lock non è
   verificabile.
5. **`close_check` a `0`**, tutte le pagine in un colpo, `--lock` compreso.
   Un `2` non è un pass.
6. **Copy vero:** niente lorem ipsum, niente `TODO`, niente «da sostituire». Le
   parole del mestiere non si traducono. `copy_check.py` sulle pagine è locale e
   costa un secondo, e si esegue sempre.
   **Il lessico invece ha una soglia, e va detta:** `copy_lock.py` rifiuta sotto
   le **otto** parole (`MINIMO = 8` — «un lessico vuoto non vincola niente»), e
   in ciclo rapido `--da-progetto` non ha niente da leggere perché
   `planning-artifacts/` non esiste. Le parole che l'owner ha usato di solito
   sono tre o quattro: passarle e basta fa uscire lo script a `1`. Quindi o si
   scrivono **otto o più termini del mestiere** — quelli che la ricerca a mente
   ha comunque prodotto, che è esattamente la prova che è stata fatta — oppure
   si consegna **senza `--lessico`**, che `close_check` accetta, e lo si dice in
   una riga. Quello che non si fa è passare quattro parole e ignorare l'exit `1`.
7. **Responsive** a ~375 e ~1280, **cookie e informativa** se la pagina raccoglie
   un dato o carica da terzi.
8. **`palette.html`** accanto alla consegna, e la riga di onestà sui dati
   verosimili in chat **più** `dati_verosimili:` nel `DESIGN.md`.
9. **La riga nel registro**, una sola:

   ```bash
   uv run scripts/council_log.py {project-root} --project <slug> --goal rapido \
     --agents "Vesper" --outcome "ciclo rapido scelto dall'owner: brief in 6 righe, nessuna seduta"
   ```

   Serve perché `close_check` non fa consegnare senza registro, ma soprattutto
   perché resti scritto che quel giorno **non si è seduto nessuno**: un lavoro
   senza consiglio è una scelta legittima, un lavoro senza consiglio che sembra
   averlo avuto no.

---

## 7. I casi che il ciclo rapido incontra davvero

Sono i bordi trovati camminando il ciclo, non ipotesi: ognuno ha una decisione,
perché un bordo senza decisione la fa prendere a caso.

**Il batch manca sempre, e quindi non è una varianza.** `craft-rules.md` →
*Quando il batch non c'è* prescrive una varianza «quando il buco ha deciso una
decisione»: lì è un incidente (rete assente). In ciclo rapido è una **proprietà
del ciclo**, e scrivere la stessa varianza identica su ogni lavoro produce
rumore, non memoria. Si dichiara **una riga nel `DESIGN.md`** — «batch non fatto,
ciclo rapido: `radius_family` deciso da tipologia + esclusioni MEMORY» — e basta.
La varianza torna obbligatoria se il buco ha deciso qualcosa **oltre** i default
previsti.

**Il ledger si scrive lo stesso, ed è il punto.** `close_check` aggiorna il
registro dei settori di tinta anche in rapido, e **non si passa `--no-ledger`**.
Se le bozze rapide non contassero, l'anti-ripetizione guarderebbe solo i lavori
lenti: cinque landing rapide di fila potrebbero uscire tutte nella stessa
famiglia senza che niente scatti — che è esattamente il difetto per cui
`repeat_guard` è stato scritto. Rapido vuol dire meno sedute, non meno storia.

**Il testo legale non si improvvisa, nemmeno qui.** Se la pagina raccoglie un
dato o carica da terzi servono informativa e richiesta cookie, e il testo è di
Jane (`agent-gdpr-counsel`). In ciclo rapido la strada da preferire è **non
avere il problema**: font in locale, nessuna risorsa di terzi, nessun banner. Ma
se c'è un form, **Jane si invoca lo stesso** — è l'unica chiamata che il ciclo
rapido non taglia, perché un'informativa inventata rientra nei «fatti che
feriscono se creduti» (`implementation-handoff.md` §10), e quella regola non ha un ciclo veloce.

**Su dashboard e mobile il rapido è solo la bozza grafica.** Una schermata si può
disegnare in rapido, ma `dashboard-rules.md` chiede tabelle paginate server side,
filtro con autocomplete, profilo, uscita e reset a link monouso — che è **il
dietro**, cioè il ciclo completo (§5). Quindi: in rapido si consegna l'aspetto
della schermata con dati verosimili, **non** si esegue `close_check --surface
dashboard` (fallirebbe su requisiti che quel ciclo non copre), e lo si dichiara
in una riga. Chi vuole la dashboard vera passa al completo.

**La chiusura in ciclo rapido non ha un piano da citare.** Non esiste
`slice_plan`, quindi la battuta finale non dice «restano S2 e S3». Dice **cosa
c'è, com'è stato fatto e cosa manca**, e poi si ferma:

> Landing online in `apps/<slug>/`. Ciclo rapido: le scelte sono le sei righe in
> testa al `DESIGN.md`, contatti e prezzi sono verosimili. Non sono stati fatti
> ricerca scritta, casi limite né review avversaria — se vuoi il ciclo completo
> su questa pagina, si costruisce sopra quello che c'è.

Resta una **dichiarazione**: espone uno stato, non offre una scelta, e non
aspetta niente.

## 8. Fallimenti

- La domanda d'ingresso fatta **in mezzo** al lavoro invece che prima, o rifatta a
  ogni correzione.
- La domanda fatta quando la richiesta conteneva già la risposta («fammi una bozza
  al volo» → si parte, non si chiede).
- Un menù di tre o più opzioni al posto delle due.
- Ciclo rapido usato per un back office, per auth, o per dati che persistono.
- Ciclo rapido usato come permesso per saltare lock, cataloghi, `repeat_guard` o
  `close_check`: quelli costano secondi, e tagliarli non rende il lavoro rapido,
  lo rende indovinato.
- I sei documenti scritti lo stesso «per sicurezza»: allora era il ciclo completo,
  ed è stato fatto pagare all'owner senza dirglielo.
- Una passata adversarial o di casi limite eseguita in ciclo rapido: l'owner ha
  scelto di non pagarla.
- Un `DESIGN.md` senza il blocco `brief:`, o con `brief:` di sei paragrafi.
- «Rapido» dichiarato e poi consegnata una pagina generica: il ciclo taglia il
  procedimento, non il mestiere.
- La parte con back end costruita comunque, in rapido, «tanto è piccola».
- **Un avviso che annuncia «niente PRD» mentre il PRD esiste** nel progetto.
- **`--no-ledger` in ciclo rapido**, o un `close_check` saltato «perché è una
  bozza»: le bozze sono la maggioranza dei lavori, e una storia che non le conta
  non conta niente.
- **Quattro parole passate a `copy_lock.py`** e l'exit `1` ignorato: o otto
  termini veri, o si consegna senza `--lessico` dicendolo.
- **`close_check --surface dashboard` eseguito su una bozza rapida**: chiede
  paginazione, filtro e uscita, che sono il dietro — fallisce, e giustamente.
- **Un'informativa privacy scritta a braccio** perché «il consiglio non c'era».
- Il `ciclo:` scritto in due posti, o una chiusura che cita un `slice_plan` che
  in questo ciclo non esiste.
