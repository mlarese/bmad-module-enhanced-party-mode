/* demo.js — pagina esemplificativa del catalogo (117 effetti).
   Ogni effetto e' visibile in tre modi:
   1. reveal on scroll in repeat (enter/leave viewport),
   2. replay all'hover / focus sulla card,
   3. loop continuo per gli effetti ambientali. */
(function () {
  'use strict';

  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  var CATEGORIES = [
    {
      id: 'reveal',
      title: '1. Reveal / entrata',
      items: [
        [1, 'Fade in', 'fade'],
        [2, 'Fade up / down / left / right', 'dirs'],
        [3, 'Zoom in / zoom out', 'zooms'],
        [4, 'Blur in', 'blur'],
        [5, 'Clip-path wipe', 'wipe'],
        [6, 'Mask reveal immagine', 'mask'],
        [7, 'Flip 3D', 'flip'],
        [8, 'Rotate in / swing', 'swing'],
        [9, 'Stagger di griglia', 'stagger'],
        [10, 'Reveal sequenziale sezione', 'seq'],
        [11, 'Curtain reveal', 'curtain-mini'],
      ],
    },
    {
      id: 'text',
      title: '2. Testo',
      items: [
        [12, 'Split per lettera', 'chars'],
        [13, 'Split per parola', 'words'],
        [14, 'Split per riga con mask', 'lines'],
        [15, 'Typewriter', 'type'],
        [16, 'Scramble / decrypt', 'scramble'],
        [17, 'Counter numerico', 'counter'],
        [18, 'Odometer a rullo', 'odo'],
        [19, 'Marquee infinito', 'marquee'],
        [20, 'Marquee scroll-linked', 'marquee-scroll'],
        [21, 'Testo su path circolare', 'path'],
        [22, 'Gradient text animato', 'gradtext'],
        [23, 'Highlight underline', 'underline'],
      ],
    },
    {
      id: 'scroll',
      title: '3. Scroll',
      items: [
        [24, 'Reveal on scroll', 'fade'],
        [25, 'Parallasse multi livello', 'parallax'],
        [26, 'Parallasse background', 'parallax-bg'],
        [27, 'Scrub timeline', 'scrub'],
        [28, 'Pin di sezione', 'pin-mini'],
        [29, 'Scroll orizzontale galleria', 'hscroll'],
        [30, 'Progress bar lettura', 'progress-mini'],
        [31, 'Header sticky shrink', 'hdr-shrink'],
        [32, 'Header hide / show', 'hdr-hide'],
        [33, 'Scroll snap', 'snap'],
        [34, 'Image sequence canvas', 'canvas-seq', 'canvas'],
        [35, 'Scroll-driven CSS', 'view'],
        [36, 'Smooth scroll / inerzia', 'lenis', 'Lenis'],
        [37, 'Cambio colore sezione', 'tint'],
      ],
    },
    {
      id: 'hero',
      title: '4. Hero e sfondi',
      items: [
        [38, 'Ken Burns', 'kenburns'],
        [39, 'Slider crossfade', 'slider'],
        [40, 'Video background', 'video-bg', 'video'],
        [41, 'Testo maschera video', 'video-text', 'video'],
        [42, 'Gradient mesh', 'mesh'],
        [43, 'Aurora / blob', 'aurora'],
        [44, 'Particelle', 'particles'],
        [45, 'Campo di stelle', 'stars'],
        [46, 'Distorsione shader', 'distort', 'WebGL'],
        [47, "Ripple d'acqua", 'water', 'WebGL'],
        [48, 'Grana / noise', 'grain'],
        [49, 'Split screen ingresso', 'split'],
      ],
    },
    {
      id: 'hover',
      title: '5. Hover e micro-interazioni',
      items: [
        [50, 'Zoom immagine', 'hv-zoom'],
        [51, 'Overlay caption', 'hv-cap'],
        [52, 'Card lift', 'hv-lift'],
        [53, 'Tilt 3D mouse', 'tilt'],
        [54, 'Bottone fill', 'hv-fill'],
        [55, 'Bottone magnetico', 'magnet'],
        [56, 'Underline link', 'hv-under'],
        [57, 'Testo swap su', 'hv-swap'],
        [58, 'Ripple click', 'ripple'],
        [59, 'Cursore custom', 'cursor'],
        [60, 'Cursore che si espande', 'cursor-x'],
        [61, 'Scia immagini', 'trail'],
        [62, 'Preview hover su lista', 'preview'],
        [63, 'Icona che si trasforma', 'icon'],
        [64, 'Glow bordo', 'glow'],
        [65, 'Shake errore', 'shake'],
      ],
    },
    {
      id: 'nav',
      title: '6. Navigazione',
      items: [
        [66, 'Hamburger → X', 'burger'],
        [67, 'Menu fullscreen stagger', 'menu-stagger'],
        [68, 'Off canvas', 'drawer'],
        [69, 'Mega menu', 'mega'],
        [70, 'Indicatore attivo', 'indicator'],
        [71, 'Dock magnify', 'dock'],
        [72, 'Breadcrumb progress', 'crumbs'],
      ],
    },
    {
      id: 'layout',
      title: '7. Layout e liste',
      items: [
        [73, 'Filtro con riordino FLIP', 'flip-grid', 'GSAP Flip'],
        [74, 'Masonry con insert', 'masonry', 'LIB'],
        [75, 'Accordion fluido', 'acc'],
        [76, 'Tabs crossfade', 'tabs'],
        [77, 'Carousel autoplay', 'carousel'],
        [78, 'Coverflow 3D', 'coverflow'],
        [79, 'Before / after', 'ba'],
        [80, 'Lightbox zoom', 'lightbox', 'FLIP'],
        [81, 'Drag and drop', 'dnd', 'dnd-kit'],
        [82, 'Lista con skeleton', 'skeleton'],
      ],
    },
    {
      id: 'page',
      title: '8. Transizioni di pagina',
      items: [
        [83, 'View Transitions API', 'vt', 'VT'],
        [84, 'Shared element morph', 'shared', 'VT / FLIP'],
        [85, 'Curtain wipe tra pagine', 'page-wipe', 'Barba'],
        [86, 'Fade / slide su route', 'route-fade', 'Motion'],
        [87, 'Preloader con percentuale', 'loader'],
        [88, 'Preloader logo SVG', 'logo'],
      ],
    },
    {
      id: 'feedback',
      title: '9. Feedback e stato',
      items: [
        [89, 'Skeleton shimmer', 'skeleton'],
        [90, 'Spinner', 'spinner'],
        [91, 'Progress determinata', 'bar'],
        [92, 'Toast', 'toast'],
        [93, 'Modale scale + blur', 'modal'],
        [94, 'Checkmark SVG', 'check'],
        [95, 'Errore shake', 'shake'],
        [96, 'Confetti', 'confetti'],
        [97, 'Pull to refresh', 'pull'],
      ],
    },
    {
      id: 'loops',
      title: '10. Loop ambientali',
      items: [
        [98, 'Float', 'float'],
        [99, 'Pulse', 'pulse'],
        [100, 'Spin lento', 'spin'],
        [101, 'Wave SVG', 'wave'],
        [102, 'Blob morph', 'blob'],
        [103, 'Gradient shift', 'gshift'],
        [104, 'Scroll hint', 'hint'],
        [105, 'Badge rotante', 'badge'],
      ],
    },
    {
      id: 'svg',
      title: '11. SVG e vettoriali',
      items: [
        [106, 'Line drawing', 'draw'],
        [107, 'Path morphing', 'morph', 'MorphSVG'],
        [108, 'Riempimento progressivo', 'fill'],
        [109, 'Lottie', 'lottie', 'lottie-web'],
        [110, 'Rive interattivo', 'rive', 'rive-js'],
        [111, 'Icone animate al hover', 'icon-hover'],
      ],
    },
    {
      id: 'webgl',
      title: '12. 3D e WebGL',
      items: [
        [112, 'Modello che ruota', 'cube', 'three.js'],
        [113, 'Camera guidata dallo scroll', 'camera', 'three.js'],
        [114, 'Distorsione al hover', 'distort', 'shader'],
        [115, 'Displacement tra immagini', 'displace', 'shader'],
        [116, 'Testo 3D estruso', 'text3d', 'three.js'],
        [117, 'Card con profondita', 'depth'],
      ],
    },
  ];

  /* ---------------- markup dei singoli effetti ---------------- */

  function badge(tech) {
    return tech ? '<span class="demo-badge-tech">' + tech + '</span>' : '';
  }

  function stageHTML(kind, id, tech) {
    switch (kind) {
      /* --- reveal --- */
      case 'fade':
        return '<div class="demo-stage" data-anim data-anim-group="g' + id + '">Fade</div>';
      case 'dirs':
        return (
          '<div class="demo-row">' +
          '<div class="demo-stage demo-stage--sm2" data-anim="up" data-anim-group="g' + id + '">Up</div>' +
          '<div class="demo-stage demo-stage--sm2" data-anim="left" data-anim-group="g' + id + '">Left</div>' +
          '<div class="demo-stage demo-stage--sm2" data-anim="right" data-anim-group="g' + id + '">Right</div>' +
          '</div>'
        );
      case 'zooms':
        return (
          '<div class="demo-row">' +
          '<div class="demo-stage demo-stage--sm2" data-anim="zoom" data-anim-group="g' + id + '">In</div>' +
          '<div class="demo-stage demo-stage--sm2" data-anim="zoom-out" data-anim-group="g' + id + '">Out</div>' +
          '</div>'
        );
      case 'blur':
        return '<div class="demo-stage" data-anim="blur" data-anim-group="g' + id + '">Blur</div>';
      case 'wipe':
        return '<div class="demo-stage demo-wipe" data-anim="wipe" data-anim-group="g' + id + '">Wipe</div>';
      case 'mask':
        return '<div class="anim-mask demo-mask" data-anim data-anim-group="g' + id + '"><div class="demo-photo"></div></div>';
      case 'flip':
        return '<div class="demo-stage" data-anim="flip" data-anim-group="g' + id + '">Flip</div>';
      case 'swing':
        return '<div class="demo-stage demo-swing" data-anim data-anim-group="g' + id + '">Swing</div>';
      case 'stagger':
        return (
          '<div class="demo-row">' +
          [0, 1, 2, 3]
            .map(function (i) {
              return '<div class="demo-stage demo-stage--sm" data-anim="up" data-anim-group="st' + id + '" style="--i:' + i + '"></div>';
            })
            .join('') +
          '</div>'
        );
      case 'seq':
        return (
          '<div class="demo-seq">' +
          '<div data-anim="up" data-anim-group="seq' + id + '">Titolo</div>' +
          '<div data-anim="up" data-anim-group="seq' + id + '">Testo di supporto</div>' +
          '<div class="demo-btn demo-btn--sm" data-anim="up" data-anim-group="seq' + id + '">CTA</div>' +
          '</div>'
        );
      case 'curtain-mini':
        return (
          '<div class="demo-mini demo-curtain-mini"><i class="l"></i><i class="r"></i><b>Reveal</b></div>'
        );

      /* --- testo --- */
      case 'chars':
        return (
          '<p class="demo-split demo-chars" data-anim data-anim-group="g' + id + '">' +
          'Lettere'.split('').map(function (c, i) {
            return '<span style="--i:' + i + '">' + c + '</span>';
          }).join('') +
          '</p>'
        );
      case 'words':
        return (
          '<p class="demo-split demo-words" data-anim data-anim-group="g' + id + '">' +
          ['Motion', 'on', 'scroll'].map(function (w, i) {
            return '<span style="--i:' + i + '">' + w + '</span>';
          }).join(' ') +
          '</p>'
        );
      case 'lines':
        return (
          '<div class="demo-lines" data-anim data-anim-group="g' + id + '">' +
          ['Righe che', 'salgono da', 'una maschera'].map(function (l, i) {
            return '<span class="anim-line" style="--i:' + i + '"><span>' + l + '</span></span>';
          }).join('') +
          '</div>'
        );
      case 'type':
        return '<p class="demo-type" data-anim data-anim-group="g' + id + '">Typewriter</p>';
      case 'scramble':
        return '<p class="demo-scramble" data-text="DECODE">······</p>';
      case 'counter':
        return '<p class="demo-counter" data-count="1280">0</p>';
      case 'odo':
        return (
          '<div class="demo-odo" data-anim data-anim-group="g' + id + '">' +
          [0, 1, 2].map(function (i) {
            return '<span style="--i:' + i + '"><b>0</b><b>4</b><b>9</b></span>';
          }).join('') +
          '</div>'
        );
      case 'marquee':
        return (
          '<div class="marquee demo-marquee"><div class="marquee__track">' +
          '<span>Marquee</span><span>·</span><span>Infinito</span><span>·</span><span>Repeat</span><span>·</span>' +
          '</div></div>'
        );
      case 'marquee-scroll':
        return (
          '<div class="demo-mini demo-marquee-scroll"><span data-parallax="0.12">velocita · legata · allo · scroll ·</span></div>'
        );
      case 'path':
        return (
          '<svg class="demo-path" viewBox="0 0 120 120"><defs><path id="c' + id +
          '" d="M60,60 m-40,0 a40,40 0 1,1 80,0 a40,40 0 1,1 -80,0"/></defs>' +
          '<text><textPath href="#c' + id + '">ROTATE · TEXT · PATH · </textPath></text></svg>'
        );
      case 'gradtext':
        return '<p class="demo-gradtext">Gradient</p>';
      case 'underline':
        return '<p class="demo-hl" data-anim data-anim-group="g' + id + '">Highlight underline</p>';

      /* --- scroll --- */
      case 'parallax':
        return (
          '<div class="demo-mini demo-parallax">' +
          '<div class="demo-stage demo-stage--sm2" data-parallax="0.04">1</div>' +
          '<div class="demo-stage demo-stage--sm2" data-parallax="0.08">2</div>' +
          '<div class="demo-stage demo-stage--sm2" data-parallax="0.12">3</div>' +
          '</div>'
        );
      case 'parallax-bg':
        return '<div class="demo-mini demo-parallax-bg"><div data-parallax="0.06"></div></div>';
      case 'scrub':
        return '<div class="demo-scrub" data-anim data-anim-group="g' + id + '"><i></i></div>';
      case 'pin-mini':
        return '<div class="demo-mini demo-pin"><b>PIN</b><i></i></div>';
      case 'hscroll':
        return '<div class="demo-mini demo-hscroll"><span></span><span></span><span></span><span></span><span></span></div>';
      case 'progress-mini':
        return '<div class="demo-mini demo-progress-mini"><i></i><em></em></div>';
      case 'hdr-shrink':
        return '<div class="demo-mini demo-hdr-mini"><header>Header</header><i></i></div>';
      case 'hdr-hide':
        return '<div class="demo-mini demo-hdr-mini is-hide"><header>Header</header><i></i></div>';
      case 'snap':
        return '<div class="demo-mini demo-snap"><span>A</span><span>B</span><span>C</span></div>';
      case 'canvas-seq':
        return '<div class="demo-canvas-wrap">' + badge(tech) + '<canvas class="demo-canvas" width="150" height="90"></canvas></div>';
      case 'view':
        return '<div class="demo-view" data-anim="up" data-anim-group="g' + id + '">Scroll-driven</div>';
      case 'lenis':
        return (
          '<div class="demo-lenis-wrap">' + badge(tech) +
          '<div class="demo-lenis"><i></i><i></i><i></i><i></i><i></i><i></i></div></div>'
        );
      case 'tint':
        return '<div class="demo-mini demo-tint"><b>Tint</b></div>';

      /* --- hero e sfondi --- */
      case 'kenburns':
        return '<div class="demo-mini"><div class="demo-photo demo-photo--full lp-kenburns"></div></div>';
      case 'slider':
        return '<div class="demo-mini demo-slider"><span></span><span></span><span></span></div>';
      case 'video-bg':
        return '<div class="demo-mini demo-videobg">' + badge(tech) + '<i></i><b>Play</b></div>';
      case 'video-text':
        return '<div class="demo-mini demo-videotext">' + badge(tech) + '<b>VIDEO</b></div>';
      case 'mesh':
        return '<div class="demo-mini demo-mesh"></div>';
      case 'aurora':
        return '<div class="demo-mini demo-aurora"><span></span><span></span></div>';
      case 'particles':
        return '<div class="demo-mini demo-particles"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>';
      case 'stars':
        return '<div class="demo-mini demo-stars"></div>';
      case 'distort':
        return '<div class="demo-mini demo-distort">' + badge(tech) + '<div class="demo-photo demo-photo--full"></div></div>';
      case 'water':
        return '<div class="demo-mini demo-water">' + badge(tech) + '<i></i><i></i><i></i></div>';
      case 'grain':
        return '<div class="demo-mini demo-grain-box"><span class="demo-grain-layer"></span></div>';
      case 'split':
        return '<div class="demo-mini demo-split-screen" data-anim data-anim-group="g' + id + '"><i></i><i></i><b>Open</b></div>';

      /* --- hover --- */
      case 'hv-zoom':
        return '<div class="hv-zoom demo-mini"><div class="demo-photo demo-photo--full"></div></div>';
      case 'hv-cap':
        return '<div class="demo-mini demo-hv-cap"><div class="demo-photo demo-photo--full"></div><span>Caption</span></div>';
      case 'hv-lift':
        return '<div class="hv-lift demo-stage">Lift</div>';
      case 'tilt':
        return '<div class="demo-tilt demo-stage" data-tilt>Tilt 3D</div>';
      case 'hv-fill':
        return '<button type="button" class="demo-btn hv-fill demo-fill-btn">Fill</button>';
      case 'magnet':
        return '<div class="demo-magnet-area"><button type="button" class="demo-btn demo-magnet" data-magnet>Magnet</button></div>';
      case 'hv-under':
        return '<a class="hv-underline demo-link" href="#catalogo">Underline</a>';
      case 'hv-swap':
        return '<span class="demo-swap"><span>Hover</span><span>Swap</span></span>';
      case 'ripple':
        return '<button type="button" class="demo-btn demo-ripple">Ripple</button>';
      case 'cursor':
        return '<div class="demo-mini demo-cursor"><i></i><b>muovi qui</b></div>';
      case 'cursor-x':
        return '<div class="demo-mini demo-cursor is-expand"><i></i><a class="demo-cursor-target">link</a></div>';
      case 'trail':
        return '<div class="demo-mini demo-trail"><b>muovi qui</b></div>';
      case 'preview':
        return (
          '<div class="demo-preview"><ul><li data-p="0">Sala Aurora</li><li data-p="1">Sala Boreale</li><li data-p="2">Sala Cirrus</li></ul>' +
          '<span class="demo-preview-img"></span></div>'
        );
      case 'icon':
      case 'icon-hover':
        return (
          '<button type="button" class="demo-icon-btn" aria-label="play/pausa">' +
          '<svg viewBox="0 0 24 24"><rect class="b1" x="6" y="4" width="4" height="16" rx="1"/>' +
          '<rect class="b2" x="14" y="4" width="4" height="16" rx="1"/></svg></button>'
        );
      case 'glow':
        return '<div class="demo-glow demo-stage">Glow</div>';
      case 'shake':
        return '<button type="button" class="demo-btn demo-shake-btn">Errore</button>';

      /* --- navigazione --- */
      case 'burger':
        return '<button type="button" class="demo-burger is-demo" aria-label="menu"><span></span><span></span><span></span></button>';
      case 'menu-stagger':
        return '<div class="demo-mini demo-menu-mini"><i style="--i:0"></i><i style="--i:1"></i><i style="--i:2"></i><i style="--i:3"></i></div>';
      case 'drawer':
        return '<div class="demo-mini demo-drawer"><aside></aside><b>Off canvas</b></div>';
      case 'mega':
        return '<div class="demo-mega"><button type="button">Menu ▾</button><div><span>Voce</span><span>Voce</span><span>Voce</span></div></div>';
      case 'indicator':
        return '<nav class="demo-indicator"><i></i><a class="is-on">A</a><a>B</a><a>C</a></nav>';
      case 'dock':
        return '<div class="demo-dock"><span></span><span></span><span></span><span></span><span></span></div>';
      case 'crumbs':
        return '<ol class="demo-crumbs"><li></li><li></li><li></li></ol>';

      /* --- layout e liste --- */
      case 'flip-grid':
        return '<div class="demo-flipgrid">' + badge(tech) + '<span></span><span></span><span></span><span></span></div>';
      case 'masonry':
        return '<div class="demo-masonry">' + badge(tech) + '<i></i><i></i><i></i><i></i><i></i></div>';
      case 'acc':
        return (
          '<div class="acc demo-acc"><button type="button" class="acc__trigger demo-btn demo-btn--sm" aria-expanded="false">Apri</button>' +
          '<div class="acc__body"><div><p>Contenuto con altezza fluida.</p></div></div></div>'
        );
      case 'tabs':
        return (
          '<div class="demo-tabs"><div class="demo-tabs-nav"><button type="button" class="is-on">Uno</button>' +
          '<button type="button">Due</button></div><div class="demo-tabs-panel is-on">Pannello 1</div>' +
          '<div class="demo-tabs-panel">Pannello 2</div></div>'
        );
      case 'carousel':
        return '<div class="demo-mini demo-carousel"><span></span><span></span><span></span></div>';
      case 'coverflow':
        return '<div class="demo-coverflow"><span></span><span></span><span></span></div>';
      case 'ba':
        return '<div class="demo-mini demo-ba"><div></div><i></i></div>';
      case 'lightbox':
        return '<div class="demo-mini demo-lightbox">' + badge(tech) + '<i></i></div>';
      case 'dnd':
        return '<div class="demo-dnd">' + badge(tech) + '<span class="slot"></span><span class="slot"></span><i class="chip"></i></div>';
      case 'skeleton':
        return '<div class="demo-skel-list"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div>';

      /* --- transizioni di pagina --- */
      case 'vt':
        return '<div class="demo-mini demo-vt">' + badge(tech) + '<b class="a">Page A</b><b class="b">Page B</b></div>';
      case 'shared':
        return '<div class="demo-mini demo-shared">' + badge(tech) + '<i></i></div>';
      case 'page-wipe':
        return '<div class="demo-mini demo-pagewipe">' + badge(tech) + '<i></i><b>Next</b></div>';
      case 'route-fade':
        return '<div class="demo-mini demo-routefade">' + badge(tech) + '<b class="a">/home</b><b class="b">/about</b></div>';
      case 'loader':
        return '<div class="demo-loader"><b>0%</b></div>';
      case 'logo':
        return '<svg class="demo-logo-draw" viewBox="0 0 64 64" data-anim data-anim-group="g' + id + '"><path d="M8 48 L32 8 L56 48 Z"/></svg>';

      /* --- feedback --- */
      case 'spinner':
        return '<div class="demo-spinner"></div>';
      case 'bar':
        return '<div class="demo-bar"><i></i></div>';
      case 'toast':
        return '<div class="demo-mini demo-toast-wrap"><span class="demo-toast">Salvato</span></div>';
      case 'modal':
        return '<div class="demo-mini demo-modal"><i></i><b>Modal</b></div>';
      case 'check':
        return '<svg class="demo-check" viewBox="0 0 48 48" data-anim data-anim-group="g' + id + '"><circle cx="24" cy="24" r="20"/><path d="M14 25 l7 7 l14-16"/></svg>';
      case 'confetti':
        return '<div class="demo-confetti"><i></i><i></i><i></i><i></i><i></i><i></i></div>';
      case 'pull':
        return '<div class="demo-mini demo-pull"><i></i><b>pull</b></div>';

      /* --- loop ambientali --- */
      case 'float':
        return '<div class="demo-stage lp-float">Float</div>';
      case 'pulse':
        return '<div class="demo-stage lp-pulse">Pulse</div>';
      case 'spin':
        return '<div class="demo-spin lp-spin"></div>';
      case 'wave':
        return '<svg class="demo-wave" viewBox="0 0 120 40" preserveAspectRatio="none"><path d="M0 20 Q30 4 60 20 T120 20 V40 H0Z"/></svg>';
      case 'blob':
        return '<div class="demo-blob"></div>';
      case 'gshift':
        return '<div class="demo-mini demo-gshift"></div>';
      case 'hint':
        return '<div class="demo-scroll-hint lp-bounce"><span></span></div>';
      case 'badge':
        return (
          '<svg class="demo-badge" viewBox="0 0 100 100"><path id="bp' + id +
          '" fill="none" d="M50,50 m-35,0 a35,35 0 1,1 70,0 a35,35 0 1,1 -70,0"/>' +
          '<text><textPath href="#bp' + id + '">BADGE · ROTATE · </textPath></text></svg>'
        );

      /* --- svg --- */
      case 'draw':
        return '<svg class="demo-draw" viewBox="0 0 80 80" data-anim data-anim-group="g' + id + '"><circle cx="40" cy="40" r="28"/></svg>';
      case 'morph':
        return '<div class="demo-morph">' + badge(tech) + '<i></i></div>';
      case 'fill':
        return '<svg class="demo-fill-svg" viewBox="0 0 80 80" data-anim data-anim-group="g' + id + '"><rect x="10" y="10" width="60" height="60" rx="10"/></svg>';
      case 'lottie':
      case 'rive':
        return (
          '<div class="demo-lottie">' + badge(tech) +
          '<svg viewBox="0 0 60 60"><circle class="c1" cx="30" cy="30" r="12"/><circle class="c2" cx="30" cy="30" r="22"/></svg></div>'
        );

      /* --- 3D --- */
      case 'cube':
        return (
          '<div class="demo-cube-wrap">' + badge(tech) +
          '<div class="demo-cube"><i></i><i></i><i></i><i></i><i></i><i></i></div></div>'
        );
      case 'camera':
        return '<div class="demo-mini demo-camera">' + badge(tech) + '<i></i><i></i><i></i></div>';
      case 'displace':
        return '<div class="demo-mini demo-displace">' + badge(tech) + '<i class="a"></i><i class="b"></i></div>';
      case 'text3d':
        return '<div class="demo-text3d">' + badge(tech) + '<b>3D</b></div>';
      case 'depth':
        return '<div class="demo-depth" data-anim data-anim-group="g' + id + '"><span></span><span></span><span></span></div>';

      default:
        return '<div class="demo-stage" data-anim data-anim-group="g' + id + '">#' + id + '</div>';
    }
  }

  /* ---------------- costruzione pagina ---------------- */

  function build() {
    var toc = document.getElementById('demo-toc');
    var tocGrid = document.getElementById('demo-toc-grid');
    var sections = document.getElementById('demo-sections');
    if (!sections) return;

    CATEGORIES.forEach(function (cat) {
      if (toc) {
        var a = document.createElement('a');
        a.href = '#' + cat.id;
        a.textContent = cat.title;
        toc.appendChild(a);
      }

      if (tocGrid) {
        var chip = document.createElement('a');
        chip.className = 'demo-toc-chip';
        chip.href = '#' + cat.id;
        chip.innerHTML = '<strong>' + cat.title + '</strong><span>' + cat.items.length + ' effetti</span>';
        tocGrid.appendChild(chip);
      }

      var section = document.createElement('section');
      section.className = 'demo-section';
      section.id = cat.id;
      section.innerHTML =
        '<header class="demo-section-head" data-anim="up"><h2>' + cat.title +
        '</h2><p>Reveal in repeat allo scroll. Passa il mouse su una card per rigiocare l’effetto.</p></header>';

      var grid = document.createElement('div');
      grid.className = 'demo-fx-grid';

      cat.items.forEach(function (item) {
        var id = item[0];
        var name = item[1];
        var kind = item[2];
        var tech = item[3];

        var card = document.createElement('article');
        card.className = 'demo-fx';
        card.id = 'fx-' + id;
        card.dataset.fx = kind;
        card.tabIndex = 0;
        card.innerHTML =
          '<header><span class="demo-fx-num">#' + id + '</span><h3>' + name +
          '</h3><span class="demo-fx-hover" aria-hidden="true">hover</span></header>' +
          '<div class="demo-fx-body">' + stageHTML(kind, id, tech) + '</div>';
        grid.appendChild(card);
      });

      section.appendChild(grid);
      sections.appendChild(section);
    });
  }

  /* ---------------- helper ---------------- */

  function restartAnimations(root) {
    root.querySelectorAll('*').forEach(function (el) {
      var name = getComputedStyle(el).animationName;
      if (!name || name === 'none') return;
      el.style.animation = 'none';
      void el.offsetWidth;
      el.style.animation = '';
    });
  }

  function replayReveals(card) {
    var els = card.querySelectorAll('[data-anim]');
    if (!els.length) return;
    els.forEach(function (el) { el.classList.remove('is-visible'); });
    void card.offsetWidth;
    els.forEach(function (el) { el.classList.add('is-visible'); });
  }

  function countTo(el) {
    var to = parseFloat(el.dataset.count) || 0;
    var dur = parseInt(el.dataset.countDur, 10) || 1400;
    if (reduce) { el.textContent = to.toLocaleString('it-IT'); return; }
    if (el._raf) cancelAnimationFrame(el._raf);
    var t0 = performance.now();
    var ease = function (t) { return 1 - Math.pow(1 - t, 3); };
    (function step(now) {
      var p = Math.min((now - t0) / dur, 1);
      el.textContent = Math.round(to * ease(p)).toLocaleString('it-IT');
      if (p < 1) el._raf = requestAnimationFrame(step);
    })(t0);
  }

  function scramble(el) {
    var target = el.dataset.text || 'TEXT';
    var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&';
    if (reduce) { el.textContent = target; return; }
    clearInterval(el._sc);
    var frame = 0;
    el._sc = setInterval(function () {
      el.textContent = target.split('').map(function (c, i) {
        return i < frame / 2 ? target[i] : chars[Math.floor(Math.random() * chars.length)];
      }).join('');
      frame++;
      if (frame > target.length * 2) {
        clearInterval(el._sc);
        el.textContent = target;
      }
    }, 45);
  }

  function drawSequence(canvas, progress) {
    var ctx = canvas.getContext('2d');
    var w = canvas.width;
    var h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#15202b';
    ctx.fillRect(0, 0, w, h);
    var angle = progress * Math.PI * 2;
    ctx.strokeStyle = '#9fd8d3';
    ctx.lineWidth = 3;
    for (var i = 0; i < 5; i++) {
      var r = 10 + i * 7;
      ctx.beginPath();
      ctx.arc(w / 2, h / 2, r, angle + i * 0.4, angle + i * 0.4 + Math.PI * 1.2);
      ctx.stroke();
    }
    ctx.fillStyle = '#0f6b66';
    ctx.beginPath();
    ctx.arc(w / 2 + Math.cos(angle) * 26, h / 2 + Math.sin(angle) * 26, 6, 0, Math.PI * 2);
    ctx.fill();
  }

  /* ---------------- play / stop per tipo ---------------- */

  var PLAY = {
    counter: function (card) { countTo(card.querySelector('[data-count]')); },
    scramble: function (card) { scramble(card.querySelector('.demo-scramble')); },
    burger: function (card) { card.querySelector('.demo-burger').classList.add('is-open'); },
    acc: function (card) {
      var acc = card.querySelector('.acc');
      acc.classList.add('is-open');
      acc.querySelector('.acc__trigger').setAttribute('aria-expanded', 'true');
    },
    drawer: function (card) { card.querySelector('.demo-drawer aside').classList.add('is-open'); },
    mega: function (card) { card.querySelector('.demo-mega > div').classList.add('is-open'); },
    tabs: function (card) {
      var buttons = card.querySelectorAll('.demo-tabs-nav button');
      var panels = card.querySelectorAll('.demo-tabs-panel');
      var next = buttons[0].classList.contains('is-on') ? 1 : 0;
      buttons.forEach(function (b) { b.classList.remove('is-on'); });
      panels.forEach(function (p) { p.classList.remove('is-on'); });
      buttons[next].classList.add('is-on');
      panels[next].classList.add('is-on');
    },
    indicator: function (card) {
      var links = card.querySelectorAll('.demo-indicator a');
      var current = 0;
      links.forEach(function (l, i) { if (l.classList.contains('is-on')) current = i; });
      var next = (current + 1) % links.length;
      links.forEach(function (l) { l.classList.remove('is-on'); });
      links[next].classList.add('is-on');
      card.querySelector('.demo-indicator i').style.transform = 'translateX(' + next * 42 + 'px)';
    },
    crumbs: function (card) {
      var steps = card.querySelectorAll('.demo-crumbs li');
      var done = card.querySelectorAll('.demo-crumbs .is-on').length;
      steps.forEach(function (s) { s.classList.remove('is-on'); });
      for (var i = 0; i <= done % steps.length; i++) steps[i].classList.add('is-on');
    },
    shake: function (card) {
      var btn = card.querySelector('.demo-shake-btn');
      btn.classList.remove('is-shake');
      void btn.offsetWidth;
      btn.classList.add('is-shake');
    },
    ripple: function (card) {
      var btn = card.querySelector('.demo-ripple');
      var wave = document.createElement('span');
      wave.className = 'demo-ripple-wave';
      wave.style.left = '50%';
      wave.style.top = '50%';
      btn.appendChild(wave);
      setTimeout(function () { wave.remove(); }, 700);
    },
    loader: function (card) {
      var el = card.querySelector('.demo-loader');
      if (reduce) return;
      if (el._raf) cancelAnimationFrame(el._raf);
      var t0 = performance.now();
      (function step(now) {
        var p = Math.min((now - t0) / 1600, 1);
        var pct = Math.round(p * 100);
        el.style.setProperty('--p', pct + '%');
        el.querySelector('b').textContent = pct + '%';
        if (p < 1) el._raf = requestAnimationFrame(step);
      })(t0);
    },
    'canvas-seq': function (card) {
      var canvas = card.querySelector('.demo-canvas');
      if (reduce) { drawSequence(canvas, 0.3); return; }
      if (canvas._raf) cancelAnimationFrame(canvas._raf);
      var t0 = performance.now();
      (function step(now) {
        var p = ((now - t0) / 2400) % 1;
        drawSequence(canvas, p);
        canvas._raf = requestAnimationFrame(step);
      })(t0);
    },
    lenis: function (card) {
      var box = card.querySelector('.demo-lenis');
      if (reduce) return;
      var target = box.scrollTop > 5 ? 0 : box.scrollHeight;
      var from = box.scrollTop;
      var t0 = performance.now();
      if (box._raf) cancelAnimationFrame(box._raf);
      (function step(now) {
        var p = Math.min((now - t0) / 900, 1);
        var e = 1 - Math.pow(1 - p, 3);
        box.scrollTop = from + (target - from) * e;
        if (p < 1) box._raf = requestAnimationFrame(step);
      })(t0);
    },
    hscroll: function (card) {
      var box = card.querySelector('.demo-hscroll');
      if (reduce) return;
      var target = box.scrollLeft > 5 ? 0 : box.scrollWidth;
      var from = box.scrollLeft;
      var t0 = performance.now();
      if (box._raf) cancelAnimationFrame(box._raf);
      (function step(now) {
        var p = Math.min((now - t0) / 900, 1);
        box.scrollLeft = from + (target - from) * (1 - Math.pow(1 - p, 3));
        if (p < 1) box._raf = requestAnimationFrame(step);
      })(t0);
    },
    snap: function (card) {
      var box = card.querySelector('.demo-snap');
      if (reduce) return;
      var w = box.clientWidth;
      var next = Math.round(box.scrollLeft / w) + 1;
      box.scrollTo({ left: (next % 3) * w, behavior: 'smooth' });
    },
    vt: function (card) {
      var el = card.querySelector('.demo-vt');
      var swap = function () { el.classList.toggle('is-b'); };
      if (document.startViewTransition && !reduce) document.startViewTransition(swap);
      else swap();
    },
  };

  var STOP = {
    burger: function (card) { card.querySelector('.demo-burger').classList.remove('is-open'); },
    acc: function (card) {
      var acc = card.querySelector('.acc');
      acc.classList.remove('is-open');
      acc.querySelector('.acc__trigger').setAttribute('aria-expanded', 'false');
    },
    drawer: function (card) { card.querySelector('.demo-drawer aside').classList.remove('is-open'); },
    mega: function (card) { card.querySelector('.demo-mega > div').classList.remove('is-open'); },
    'canvas-seq': function (card) {
      var canvas = card.querySelector('.demo-canvas');
      if (canvas._raf) cancelAnimationFrame(canvas._raf);
    },
  };

  function playCard(card) {
    card.classList.add('is-live');
    replayReveals(card);
    restartAnimations(card.querySelector('.demo-fx-body'));
    var fn = PLAY[card.dataset.fx];
    if (fn) fn(card);
  }

  function stopCard(card) {
    card.classList.remove('is-live');
    var fn = STOP[card.dataset.fx];
    if (fn) fn(card);
  }

  /* ---------------- interazioni ---------------- */

  function wire() {
    document.querySelectorAll('.demo-fx').forEach(function (card) {
      card.addEventListener('mouseenter', function () { playCard(card); });
      card.addEventListener('mouseleave', function () { stopCard(card); });
      card.addEventListener('focusin', function () { playCard(card); });
      card.addEventListener('focusout', function () { stopCard(card); });
      /* touch: tap = replay */
      card.addEventListener('click', function () {
        playCard(card);
        setTimeout(function () { stopCard(card); }, 2200);
      });
    });

    /* counter e scramble partono anche allo scroll, in repeat */
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var card = e.target;
          var fn = PLAY[card.dataset.fx];
          if (fn) fn(card);
        });
      }, { threshold: 0.5 });
      document.querySelectorAll('.demo-fx[data-fx="counter"], .demo-fx[data-fx="scramble"], .demo-fx[data-fx="canvas-seq"], .demo-fx[data-fx="loader"]')
        .forEach(function (c) { io.observe(c); });
    }

    /* tilt e magnet seguono il puntatore */
    document.querySelectorAll('[data-tilt]').forEach(function (el) {
      el.addEventListener('mousemove', function (ev) {
        var r = el.getBoundingClientRect();
        var x = (ev.clientX - r.left) / r.width - 0.5;
        var y = (ev.clientY - r.top) / r.height - 0.5;
        el.style.transform = 'perspective(600px) rotateY(' + x * 20 + 'deg) rotateX(' + -y * 20 + 'deg)';
      });
      el.addEventListener('mouseleave', function () { el.style.transform = ''; });
    });

    document.querySelectorAll('[data-magnet]').forEach(function (el) {
      var area = el.closest('.demo-magnet-area') || el.parentElement;
      if (!area) return;
      area.addEventListener('mousemove', function (ev) {
        var r = el.getBoundingClientRect();
        el.style.transform =
          'translate(' + (ev.clientX - (r.left + r.width / 2)) * 0.3 + 'px,' +
          (ev.clientY - (r.top + r.height / 2)) * 0.3 + 'px)';
      });
      area.addEventListener('mouseleave', function () { el.style.transform = ''; });
    });

    /* cursore custom e scia */
    document.querySelectorAll('.demo-cursor').forEach(function (box) {
      var dot = box.querySelector('i');
      box.addEventListener('mousemove', function (ev) {
        var r = box.getBoundingClientRect();
        dot.style.transform = 'translate(' + (ev.clientX - r.left) + 'px,' + (ev.clientY - r.top) + 'px)';
      });
    });

    document.querySelectorAll('.demo-trail').forEach(function (box) {
      var last = 0;
      box.addEventListener('mousemove', function (ev) {
        var now = performance.now();
        if (now - last < 70) return;
        last = now;
        var r = box.getBoundingClientRect();
        var chip = document.createElement('i');
        chip.style.left = ev.clientX - r.left + 'px';
        chip.style.top = ev.clientY - r.top + 'px';
        box.appendChild(chip);
        setTimeout(function () { chip.remove(); }, 700);
      });
    });

    /* preview su lista link */
    document.querySelectorAll('.demo-preview').forEach(function (box) {
      var img = box.querySelector('.demo-preview-img');
      box.querySelectorAll('li').forEach(function (li) {
        li.addEventListener('mouseenter', function () {
          box.classList.add('is-on');
          img.dataset.p = li.dataset.p;
        });
      });
      box.addEventListener('mouseleave', function () { box.classList.remove('is-on'); });
    });

    /* click diretti restano funzionanti */
    document.querySelectorAll('.demo-burger.is-demo').forEach(function (btn) {
      btn.addEventListener('click', function (ev) {
        ev.stopPropagation();
        btn.classList.toggle('is-open');
      });
    });

    document.querySelectorAll('.demo-ripple').forEach(function (btn) {
      btn.addEventListener('click', function (ev) {
        ev.stopPropagation();
        var r = btn.getBoundingClientRect();
        var wave = document.createElement('span');
        wave.className = 'demo-ripple-wave';
        wave.style.left = ev.clientX - r.left + 'px';
        wave.style.top = ev.clientY - r.top + 'px';
        btn.appendChild(wave);
        setTimeout(function () { wave.remove(); }, 700);
      });
    });

    document.querySelectorAll('.demo-tabs-nav button').forEach(function (btn) {
      btn.addEventListener('click', function (ev) {
        ev.stopPropagation();
        var root = btn.closest('.demo-tabs');
        var buttons = root.querySelectorAll('.demo-tabs-nav button');
        var panels = root.querySelectorAll('.demo-tabs-panel');
        buttons.forEach(function (b, i) {
          b.classList.toggle('is-on', b === btn);
          panels[i].classList.toggle('is-on', b === btn);
        });
      });
    });

    var burger = document.getElementById('demo-burger');
    var menu = document.getElementById('demo-menu');
    if (burger && menu) {
      burger.addEventListener('click', function () {
        var open = burger.classList.toggle('is-open');
        burger.setAttribute('aria-expanded', open ? 'true' : 'false');
        menu.hidden = !open;
        menu.classList.toggle('is-open', open);
      });
    }
  }

  build();
  wire();
  /* anim.js (caricato dopo) gestisce reveal repeat, parallax, curtain, marquee. */
})();
