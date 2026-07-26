# Performance e accessibilita'

## Regole non negoziabili

1. Anima solo proprieta' compositate: `transform`, `opacity`. `filter` e `clip-path` sono accettabili ma piu' costosi.
2. Mai animare `width`, `height`, `top`, `left`, `margin`, `box-shadow` in continuo: causano layout e paint su ogni frame.
3. `will-change: transform` solo sugli elementi realmente animati e rimuoverlo a fine animazione. Abusarlo consuma memoria GPU.
4. Un solo `requestAnimationFrame` loop globale, non uno per elemento.
5. Listener di scroll e touch sempre `{ passive: true }`.
6. `IntersectionObserver` per attivare e disattivare loop, video, canvas e WebGL fuori viewport.
7. Immagini e video di sfondo: `loading="lazy"` tranne l'hero, formati moderni (webp/avif), `poster` sui video.
8. Su mobile ridurre o disattivare parallasse e WebGL: costano batteria e fps.

## Impatto sui Core Web Vitals

- **LCP**: l'elemento piu' grande above the fold non deve avere `opacity:0` iniziale prolungato. Se serve un fade, max 300ms e senza attendere JS.
- **CLS**: riservare sempre `aspect-ratio` o dimensioni; animazioni che spostano contenuto reale (non solo transform) generano layout shift.
- **INP**: animazioni pesanti durante l'interazione bloccano il main thread. Preferire Web Animations API o GSAP, non setInterval.

## Accessibilita'

- `prefers-reduced-motion: reduce` deve disattivare parallasse, autoplay, zoom continui, movimenti ampi. Fade e transizioni brevi possono restare.
- Nessun contenuto lampeggiante oltre 3 volte al secondo (rischio epilessia, WCAG 2.3.1).
- Contenuto in movimento automatico per oltre 5 secondi deve avere pausa (WCAG 2.2.2): vale per marquee e carousel autoplay.
- Il focus da tastiera deve restare visibile e l'ordine non deve dipendere da animazioni.
- Elementi rivelati allo scroll devono essere leggibili anche senza JS: prevedere `<noscript>` o classe `.no-js` che forza la visibilita'.

```html
<script>document.documentElement.classList.remove('no-js')</script>
```
```css
.no-js [data-anim]{opacity:1;transform:none}
```

## Debug

- Chrome DevTools > Rendering: Frame Rendering Stats, Paint flashing, Layer borders.
- Performance panel: cercare barre lunghe in Layout e Paint durante lo scroll.
- `ScrollTrigger.getAll().forEach(t => t.refresh())` dopo caricamenti asincroni o font swap.
- Font che caricano tardi possono spostare il testo dopo l'animazione: usare `font-display: swap` e size-adjust.

## Budget consigliato

| Voce | Limite |
|---|---|
| JS animazioni | < 40KB gzip (GSAP core + ScrollTrigger ~ 35KB) |
| Elementi animati simultanei | < 20 |
| Frame time | < 8ms per lasciare margine |
| Effetti WebGL per pagina | 1 |
