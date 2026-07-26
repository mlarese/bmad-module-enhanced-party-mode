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
