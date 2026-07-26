---
name: design-md-landing
description: Stampo DESIGN.md per landing / brand home (marketing)
type: template
---

# DESIGN.md — Landing (stampo)

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

## Do's and Don'ts

- **Do:** ispirazione strutturale dal batch `--surface marketing --activity …`
- **Don't:** Inter/system display; purple-indigo AI; cream+serif+terracotta di default; card spam in hero; clone Envato
