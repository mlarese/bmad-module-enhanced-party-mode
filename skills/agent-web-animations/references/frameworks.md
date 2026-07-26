# Framework e CMS

## React (Framer Motion / Motion)

```jsx
import { motion, useScroll, useTransform, useInView } from 'motion/react';

const fadeUp = {
  hidden: { opacity: 0, y: 28 },
  show: (i = 0) => ({ opacity: 1, y: 0,
    transition: { duration: .8, delay: i * .09, ease: [.22, 1, .36, 1] } })
};

<motion.div variants={fadeUp} initial="hidden" whileInView="show"
            viewport={{ once: true, amount: .2 }} custom={i} />
```

Parallasse:
```jsx
const ref = useRef(null);
const { scrollYProgress } = useScroll({ target: ref, offset: ['start end','end start'] });
const y = useTransform(scrollYProgress, [0,1], ['-12%','12%']);
<motion.img ref={ref} style={{ y }} />
```

Uscita e route transition: `<AnimatePresence mode="wait">` con `key` sulla route.
Layout animations: `layout` e `layoutId` per shared element (equivalente FLIP gratis).
Reduced motion: `useReducedMotion()` e disattivare le variants.

## Vue / Nuxt

- `<Transition>` e `<TransitionGroup>` per enter/leave e riordino liste.
- `@vueuse/motion` per direttive `v-motion-fade-visible`.
- GSAP funziona identico dentro `onMounted`, ricordarsi `ScrollTrigger.refresh()` dopo il fetch dei dati.

## WordPress

### Strategia consigliata (child theme, zero plugin)

1. `wp_enqueue_style` e `wp_enqueue_script` in `functions.php` del child theme:

```php
add_action('wp_enqueue_scripts', function () {
  $v = filemtime(get_stylesheet_directory() . '/assets/anim.css');
  wp_enqueue_style('anim', get_stylesheet_directory_uri() . '/assets/anim.css', [], $v);
  wp_enqueue_script('anim', get_stylesheet_directory_uri() . '/assets/anim.js', [], $v, true);
});
```

2. Aggiungere `data-anim` agli elementi via template, blocchi (attributo "Additional CSS class" non basta: usare un blocco HTML custom o un filtro `render_block`).

```php
add_filter('render_block', function ($content, $block) {
  if (in_array($block['blockName'], ['core/heading','core/image','core/paragraph'], true)) {
    return preg_replace('/<(h\d|figure|p)\b/', '<$1 data-anim', $content, 1);
  }
  return $content;
}, 10, 2);
```

### Elementor

- Advanced > Motion Effects: Scrolling Effects (vertical/horizontal scroll, transparency, blur, rotate, scale), Mouse Effects (mouse track, 3D tilt), Sticky.
- Advanced > Entrance Animation: catalogo animate.css, con Duration e Delay.
- Per effetti fuori catalogo: HTML widget con `<style>` e `<script>`, oppure custom CSS per widget (Pro).
- Attenzione: molte motion effects usano listener su scroll, su mobile disattivarle (breakpoint toggle) per non perdere fps.

### WPBakery / Visual Composer

- `css_animation` sul row/column usa animate.css con classe `wpb_animate_when_almost_visible wpb_<anim>`.
- Per effetti custom, aggiungere Extra class e definire keyframes nel child theme.

### Slider

- Swiper (usato da Elementor e da molti temi): `effect: 'fade'`, `parallax: true`, `autoplay: {delay, disableOnInteraction:false}`, `speed`.
- Slider Revolution: markup con classi `rs-`, effetti configurati nel pannello, difficile da replicare a mano: valutare sostituzione con Swiper.

### Performance su WordPress

- Disattivare i plugin di animazione ridondanti (spesso ne coesistono 2 o 3: animate.css + WOW + AOS).
- Caricare i JS in footer con `defer`.
- Evitare animazioni su elementi above the fold che ritardano LCP: il testo hero deve essere visibile subito o comparire entro 300ms.

## Lottie

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
<div id="lot"></div>
<script>
const a = lottie.loadAnimation({ container: lot, renderer: 'svg', loop: false,
  autoplay: false, path: '/anim.json' });
new IntersectionObserver(([e]) => e.isIntersecting && a.play(), {threshold:.4}).observe(lot);
</script>
```
Scroll-linked: `a.goToAndStop(progress * a.totalFrames, true)`.
Rive: preferibile a Lottie per animazioni interattive con stati (state machine), file piu' leggeri.

## three.js (minimo utile)

```js
const renderer = new THREE.WebGLRenderer({ antialias:true, alpha:true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));   // mai oltre 2
// render solo quando visibile
const io = new IntersectionObserver(([e]) => running = e.isIntersecting);
```
Regole: caricare three solo su desktop o dietro dynamic import, fornire sempre un fallback statico (poster) e rispettare reduced motion.
