---
name: design-md-landing
description: Modello di DESIGN.md per landing / brand home (marketing)
type: template
---

# DESIGN.md — Landing (modello)

Copia in `{output}/DESIGN.md` e riempi i token. Spec: Google Labs design.md (vedi `bmad-ux/references/design-md-spec.md`).

```yaml
---
name: '{Brand}'
description: '{Una riga: chi è e cosa offre}'
colors:
  surface-base: '#______'
  ink-primary: '#______'
  accent: '#______'
  # … da locale + register + activity (craft-rules); non hex da Envato
typography:
  display:
    fontFamily: '{Display}'
    fontWeight: 500
  body:
    fontFamily: '{Body}'
    fontSize: 1rem
rounded:
  sm: '{from radius_family}'
  md: '{…}'
spacing:
  gutter: '{…}'
  section: '{…}'
---
```

## Il ciclo, e il brief quando il ciclo è rapido

Il ciclo scelto dall'owner si scrive sempre, in una riga: `ciclo: rapido` o
`ciclo: completo` (`implementation-handoff.md` §0). Senza, fra sei mesi «qui manca
il PRD» sembra una dimenticanza invece che una scelta.

**In un posto solo.** `ciclo:` sta a livello alto, **fuori** dal blocco `brief:`
— che in ciclo completo non esiste — e non si ripete dentro. Due posti dove
scrivere la stessa cosa sono due posti dove può diventare falsa
(`implementation-handoff.md` §4.2 punto 5).

**In ciclo completo** il perimetro sta nei sei documenti di `planning-artifacts/`
e qui basta il rimando. **In ciclo rapido quei documenti non esistono**, e le
stesse decisioni stanno qui — sei righe, ognuna marcata `fatto | assunzione`
(`ciclo-rapido.md` §3). Una riga che non ci sta è un lavoro che non era da ciclo
rapido.

```yaml
ciclo: rapido        # ← qui, e in nessun altro posto
brief:
  cosa: '{cosa fa davvero il business, con le parole del settore}'        # assunzione
  per_chi: '{chi compra, e l''obiezione che lo blocca}'                   # assunzione
  perimetro: '{le sezioni che ci sono — e le due o tre che NON ci sono}'  # fatto
  conversione: '{form | telefono | prenotazione, con o senza acconto}'    # fatto
  stack: '{come si apre: HTML statico, o quello che il repo impone}'      # fatto
  sicurezza: '{cosa raccoglie la pagina · cosa resta requisito del back end}'
```

## Brand & Style

{Postura editoriale. Hero = brand dominante. Una headline, una frase, un gruppo CTA. No dashboard in hero.}

## Layout & Spacing

- `grid_system` · `alignment_map` · `bleed_rhythm` da `craft_axes.py` + batch
- Full-bleed hero (salvo archetipo scelto dal catalogo)
- Responsive desktop + mobile obbligatorio

## Dati verosimili (obbligatorio quando i contenuti non erano forniti)

Elenca **cosa è inventato e dove** — telefono, email, indirizzo, P.IVA, prezzi,
orari, recensioni. Non è la nota di sostituzione vietata nella pagina: lì
sporcherebbe il lavoro consegnato, qui documenta. La riga di onestà all'owner in chat
si dà comunque: questa risponde fra sei mesi a «ma questo numero è vero?».

```yaml
dati_verosimili:
  - campo: telefono
    valore: '{quello scritto in pagina}'
    nota: 'inventato — prefisso non assegnato'
  - campo: prezzi
    valore: '{range esposto}'
    nota: 'plausibili per {activity} a {locale}, non confermati dal cliente'
```

Se i contenuti li ha forniti l'owner o il sito del cliente, scrivi
`dati_verosimili: nessuno — contenuti dal cliente`.

## Do's and Don'ts

- **Do:** ispirazione strutturale dal batch `--surface marketing --activity …`
- **Don't:** Inter/system display; purple-indigo AI; cream+serif+terracotta di default; card spam in hero; clone Envato
