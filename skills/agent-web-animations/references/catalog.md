# Catalogo animazioni

> **Guardali muovere.** Questa è la tabella; la scelta a vista si fa sulla pagina:
> `uv run scripts/effects_gallery.py --build` → `open assets/effects-gallery.html`.
> Ogni riquadro esegue il suo effetto, con famiglia, tecnica e costo. Stessa numerazione
> (1-117), quindi i riferimenti qui sotto restano validi. Sorgente: `assets/effects-catalog.json`.
> Da riga di comando: `--filter cat=scroll`, `--filter cost=free`, `--show 27`, `--kit vetrina`,
> `--suggest 4 --seed YYYYMMDDHH`.

Legenda tecnica: `CSS` = keyframes/transition, `IO` = IntersectionObserver, `GSAP` = GSAP/ScrollTrigger, `WA` = Web Animations API, `WEBGL` = three.js/OGL/shader, `SVG` = SMIL o stroke-dasharray, `LIB` = libreria dedicata.

## 1. Reveal / entrata (11)

| # | Animazione | Tecnica |
|---|---|---|
| 1 | Fade in | CSS + IO |
| 2 | Fade up / down / left / right | CSS + IO |
| 3 | Zoom in / zoom out | CSS + IO |
| 4 | Blur in (da `filter: blur`) | CSS + IO |
| 5 | Clip-path wipe (tendina da un lato) | CSS + IO |
| 6 | Mask reveal immagine (overlay che scorre via) | CSS/GSAP |
| 7 | Flip 3D su X o Y | CSS + IO |
| 8 | Rotate in / swing | CSS + IO |
| 9 | Stagger di griglia (card a cascata) | CSS delay o GSAP |
| 10 | Reveal sequenziale di sezione (titolo, testo, CTA) | GSAP timeline |
| 11 | Curtain reveal (due meta' che si aprono) | CSS/GSAP |

## 2. Testo (12)

| # | Animazione | Tecnica |
|---|---|---|
| 12 | Split per lettera, entrata a cascata | SplitText/Splitting + GSAP |
| 13 | Split per parola | idem |
| 14 | Split per riga con mask (righe che salgono) | idem |
| 15 | Typewriter (scrittura a macchina) | JS/LIB (typed.js) |
| 16 | Scramble / decrypt text | GSAP ScrambleText o JS custom |
| 17 | Counter numerico (contatore 0 -> N) | JS + IO |
| 18 | Odometer a rullo | LIB/CSS |
| 19 | Marquee orizzontale infinito | CSS keyframes |
| 20 | Marquee con velocita' legata allo scroll | GSAP/JS |
| 21 | Testo su tracciato circolare rotante | SVG + CSS |
| 22 | Gradient text animato | CSS background-position |
| 23 | Highlight underline che si disegna | CSS scaleX |

## 3. Scroll (14)

| # | Animazione | Tecnica |
|---|---|---|
| 24 | Reveal on scroll (entra in viewport) | IO |
| 25 | Parallasse verticale multi livello | JS/GSAP |
| 26 | Parallasse su immagine di background | CSS/GSAP |
| 27 | Scrub timeline (animazione legata alla progressione) | GSAP ScrollTrigger |
| 28 | Pin di sezione (sticky mentre l'animazione avanza) | GSAP pin / CSS sticky |
| 29 | Scroll orizzontale di una galleria | GSAP |
| 30 | Progress bar di lettura | JS/CSS scroll-timeline |
| 31 | Header sticky che si rimpicciolisce | JS + CSS |
| 32 | Header che si nasconde scrollando giu' e riappare su | JS |
| 33 | Scroll snap tra sezioni fullscreen | CSS scroll-snap |
| 34 | Image sequence su canvas (stile Apple) | JS canvas |
| 35 | Scroll-driven animations native | CSS `animation-timeline: view()` |
| 36 | Smooth scroll / inerzia | Lenis o Locomotive |
| 37 | Cambio colore sezione allo scroll | IO + CSS variables |

## 4. Hero e sfondi (12)

| # | Animazione | Tecnica |
|---|---|---|
| 38 | Ken Burns (zoom lento su foto) | CSS |
| 39 | Slider hero con crossfade | CSS/Swiper |
| 40 | Video background con overlay e fade | HTML5 + CSS |
| 41 | Testo con maschera video | CSS `background-clip: text` |
| 42 | Gradient mesh animato | CSS/SVG/WEBGL |
| 43 | Aurora / blob morphing | CSS filter blur + keyframes |
| 44 | Particelle | tsParticles / canvas |
| 45 | Campo di stelle o rete di punti | canvas/WEBGL |
| 46 | Distorsione shader su immagine | WEBGL |
| 47 | Ripple d'acqua al mouse | WEBGL |
| 48 | Grana / noise animata | CSS overlay + keyframes |
| 49 | Split screen (due meta' che si aprono all'ingresso) | GSAP |

## 5. Hover e micro-interazioni (16)

| # | Animazione | Tecnica |
|---|---|---|
| 50 | Zoom immagine dentro contenitore overflow hidden | CSS |
| 51 | Overlay con caption che sale | CSS |
| 52 | Card lift (translateY + shadow) | CSS |
| 53 | Tilt 3D con il mouse | JS (vanilla-tilt) |
| 54 | Bottone con riempimento progressivo | CSS |
| 55 | Bottone magnetico (segue il cursore) | JS/GSAP |
| 56 | Underline animato su link | CSS |
| 57 | Testo che scorre in su sostituito dal duplicato | CSS |
| 58 | Ripple material al click | CSS/JS |
| 59 | Cursore custom follower | JS |
| 60 | Cursore che si espande su elementi interattivi | JS |
| 61 | Scia di immagini al movimento del mouse | JS |
| 62 | Preview immagine al hover su lista link | JS/GSAP |
| 63 | Icona che si trasforma (play/pausa, menu/close) | CSS/SVG |
| 64 | Glow o bordo animato | CSS conic-gradient |
| 65 | Shake su errore | CSS |

## 6. Navigazione (7)

| # | Animazione | Tecnica |
|---|---|---|
| 66 | Hamburger che diventa X | CSS |
| 67 | Menu fullscreen overlay con voci in stagger | GSAP/CSS |
| 68 | Off canvas laterale | CSS transform |
| 69 | Mega menu con fade e slide | CSS |
| 70 | Indicatore attivo che scorre tra le voci | JS/FLIP |
| 71 | Dock con magnificazione (stile macOS) | JS |
| 72 | Breadcrumb / step progress animato | CSS |

## 7. Layout e liste (10)

| # | Animazione | Tecnica |
|---|---|---|
| 73 | Filtro con riordino fluido | FLIP (GSAP Flip / Isotope) |
| 74 | Masonry con inserimento animato | LIB |
| 75 | Accordion apri/chiudi con altezza fluida | CSS grid-template-rows o JS |
| 76 | Tabs con crossfade e indicatore | CSS/JS |
| 77 | Carousel con autoplay e loop infinito | Swiper |
| 78 | Coverflow / carousel 3D | Swiper |
| 79 | Before / after slider comparativo | JS |
| 80 | Lightbox con zoom dall'elemento sorgente | LIB/FLIP |
| 81 | Drag and drop con transizioni | GSAP Draggable / dnd-kit |
| 82 | Lista infinita con skeleton in caricamento | CSS shimmer |

## 8. Transizioni di pagina (6)

| # | Animazione | Tecnica |
|---|---|---|
| 83 | View Transitions API (same document e cross document) | CSS/JS nativo |
| 84 | Shared element transition (morph tra pagine) | View Transitions / FLIP |
| 85 | Curtain wipe tra pagine | Barba.js + GSAP |
| 86 | Fade e slide su cambio route | Framer Motion / Barba |
| 87 | Preloader con percentuale | JS |
| 88 | Preloader con logo che si disegna | SVG |

## 9. Feedback e stato (9)

| # | Animazione | Tecnica |
|---|---|---|
| 89 | Skeleton shimmer | CSS |
| 90 | Spinner | CSS |
| 91 | Progress bar determinata | CSS/JS |
| 92 | Toast in entrata e uscita | CSS/WA |
| 93 | Modale con scale e backdrop blur | CSS |
| 94 | Checkmark di successo disegnato | SVG stroke |
| 95 | Errore con shake e colore | CSS |
| 96 | Confetti | canvas LIB |
| 97 | Pull to refresh | JS |

## 10. Loop ambientali (8)

| # | Animazione | Tecnica |
|---|---|---|
| 98 | Float / levitazione | CSS |
| 99 | Pulse / breathe | CSS |
| 100 | Rotazione lenta continua | CSS |
| 101 | Wave SVG | SVG + CSS |
| 102 | Blob che cambia forma | CSS border-radius morph |
| 103 | Gradient shift | CSS |
| 104 | Scroll hint (freccia che rimbalza) | CSS |
| 105 | Badge circolare rotante con testo | CSS + SVG |

## 11. SVG e vettoriali (6)

| # | Animazione | Tecnica |
|---|---|---|
| 106 | Line drawing (stroke-dasharray) | SVG + CSS/GSAP |
| 107 | Path morphing | GSAP MorphSVG / LIB |
| 108 | Riempimento progressivo | SVG mask |
| 109 | Animazione Lottie da After Effects | lottie-web |
| 110 | Animazione Rive interattiva | rive-js |
| 111 | Icone animate al hover | SVG + CSS |

## 12. 3D e WebGL (6)

| # | Animazione | Tecnica |
|---|---|---|
| 112 | Scena three.js con modello che ruota | three.js |
| 113 | Camera guidata dallo scroll | three.js + ScrollTrigger |
| 114 | Distorsione immagine al hover | shader |
| 115 | Transizione tra immagini con displacement map | shader |
| 116 | Testo 3D estruso | three.js |
| 117 | Card con effetto profondita' (layer separati) | CSS 3D transforms |

## Come scegliere

I kit vivono in `assets/effects-catalog.json` e sono selezionabili in pagina con un click
(`--kit <id>` da riga di comando):

- **vetrina** — sito vetrina, ristorante, hotel: 1, 2, 24, 38, 31, 50, 39, 67, 75.
- **landing** — landing marketing: 10, 17, 27, 28, 54, 89, 30, 92.
- **portfolio** — portfolio o agenzia: 14, 29, 46, 59, 62, 85, 113, 6.
- **dashboard** — dashboard o app: 75, 76, 82, 89, 92, 93, 94, 70.
- **editoriale** — long form e articoli: 30, 24, 5, 37, 23, 32.

Sono punti di partenza da tagliare, non liste da applicare intere.
