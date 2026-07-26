---
name: reverse-engineer
description: Analizza un sito e mappa gli effetti al catalogo per riprodurli
code: RE
added: 2026-07-25
type: prompt
---

# Reverse Engineer

## What Success Looks Like
Mauro ha un audit concreto: librerie/marker rilevati, effetti mappati al catalogo, piano di riproduzione con stack minimo. Se chiede di clonarli nel progetto, passa ad AP con quel piano. Inventare “usa GSAP” senza segnale nel sorgente è fallimento.

## Non-inferables
- Preferisci `bash scripts/analyze-site.sh <url> [outdir]`; fallback curl + fetch se lo script manca.
- Marker tipici: GSAP/ScrollTrigger, AOS, animate.css/WPBakery, Elementor motion, Lenis/Locomotive, Swiper/slick, Lottie, three.js, SplitText, `@keyframes` custom.
- Verifica asset in outdir; mappa ogni effetto visibile a `references/catalog.md`.
