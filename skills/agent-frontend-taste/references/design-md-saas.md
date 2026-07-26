---
name: design-md-saas
description: Modello di DESIGN.md per SaaS marketing + product chrome
type: template
---

# DESIGN.md — SaaS (modello)

Ibrido: landing prodotto (`--activity saas`) e/o shell app. Dichiare quale dei due è in scope.

```yaml
---
name: '{Product}'
description: '{Job-to-be-done in una riga}'
colors:
  surface-base: '#______'
  ink-primary: '#______'
  accent: '#______'
typography:
  display:
    fontFamily: '{Display}'
  body:
    fontFamily: '{Body}'
  ui:
    fontFamily: '{UI}'
rounded:
  sm: '{…}'
  md: '{…}'
components:
  button-primary: {}
  pricing-tier: {}
  nav: {}
---
```

## Brand & Style

Credibilità B2B/B2C senza purple-glow AI. Pricing e CTA leggibili; feature come prova, non decorazione.

## Layout & Spacing

- Marketing: hero + sezioni dal dominio (social proof, pricing, FAQ) — non stub
- Product: seguire regole dashboard se è admin; mobile-web-app se è app task

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

- **Do:** batch `--activity saas` (Envato `saas` + `landing-page`)
- **Don't:** fintech-purple default; mock dashboard finta come hero unica
