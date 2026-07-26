# Ricette JavaScript

## 1. Reveal universale (vanilla, ~15 righe)

```js
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const els = document.querySelectorAll('[data-anim]');
if (reduce) els.forEach(el => el.classList.add('is-visible'));
else {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-visible');
      io.unobserve(e.target);              // one shot
    });
  }, { threshold: .15, rootMargin: '0px 0px -10% 0px' });
  els.forEach((el, i) => { el.style.setProperty('--i', i % 8); io.observe(el); });
}
```

## 2. Parallasse leggera (rAF, no scroll listener pesante)

```js
const items = [...document.querySelectorAll('[data-parallax]')];
let ticking = false;
addEventListener('scroll', () => {
  if (ticking) return; ticking = true;
  requestAnimationFrame(() => {
    const vh = innerHeight;
    items.forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      const speed = parseFloat(el.dataset.parallax) || .2;
      const offset = (r.top + r.height / 2 - vh / 2) * -speed;
      el.style.transform = `translate3d(0,${offset.toFixed(1)}px,0)`;
    });
    ticking = false;
  });
}, { passive: true });
```

## 3. Counter

```js
function countTo(el, to, dur = 1600) {
  const t0 = performance.now();
  const ease = t => 1 - Math.pow(1 - t, 3);
  const step = now => {
    const p = Math.min((now - t0) / dur, 1);
    el.textContent = Math.round(to * ease(p)).toLocaleString('it-IT');
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
```

## 4. Header shrink + hide on scroll down

```js
let last = 0;
addEventListener('scroll', () => {
  const y = scrollY;
  const h = document.querySelector('.site-header');
  h.classList.toggle('is-scrolled', y > 60);
  h.classList.toggle('is-hidden', y > last && y > 200);
  last = y;
}, { passive: true });
```

## 5. Split text senza librerie

```js
function split(el, by = 'char') {
  const words = el.textContent.trim().split(/\s+/);
  el.innerHTML = words.map(w => {
    const inner = by === 'char'
      ? [...w].map(c => `<span class="ch">${c}</span>`).join('')
      : w;
    return `<span class="wd"><span class="wd__in">${inner}</span></span>`;
  }).join(' ');
  return el.querySelectorAll(by === 'char' ? '.ch' : '.wd__in');
}
```
CSS: `.wd{overflow:hidden;display:inline-block}` e animare `.wd__in` con `translateY(100%) -> 0` in stagger.

## 6. Cursore custom con lerp

```js
let mx = 0, my = 0, cx = 0, cy = 0;
addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });
(function loop(){
  cx += (mx - cx) * .15; cy += (my - cy) * .15;
  cursor.style.transform = `translate3d(${cx}px,${cy}px,0) translate(-50%,-50%)`;
  requestAnimationFrame(loop);
})();
```

## 7. Bottone magnetico

```js
btn.addEventListener('mousemove', e => {
  const r = btn.getBoundingClientRect();
  const x = e.clientX - r.left - r.width / 2;
  const y = e.clientY - r.top - r.height / 2;
  btn.style.transform = `translate(${x * .25}px, ${y * .35}px)`;
});
btn.addEventListener('mouseleave', () => btn.style.transform = '');
```

---

# GSAP

Da usare quando servono timeline, scrub, pin, FLIP o morph. CDN:
`gsap.min.js` + `ScrollTrigger.min.js`.

## Setup + reduced motion

```js
gsap.registerPlugin(ScrollTrigger);
ScrollTrigger.config({ ignoreMobileResize: true });
if (matchMedia('(prefers-reduced-motion: reduce)').matches) gsap.globalTimeline.timeScale(1000);
```

## Reveal in batch

```js
ScrollTrigger.batch('[data-anim]', {
  start: 'top 85%',
  onEnter: b => gsap.to(b, { opacity: 1, y: 0, duration: .9, stagger: .09, ease: 'expo.out' })
});
```

## Timeline di sezione

```js
gsap.timeline({ scrollTrigger: { trigger: '.about', start: 'top 70%' } })
  .from('.about__title .ch', { yPercent: 110, stagger: .02, duration: .8, ease: 'expo.out' })
  .from('.about__text', { opacity: 0, y: 24 }, '-=.4')
  .from('.about__cta', { opacity: 0, scale: .9, ease: 'back.out(1.6)' }, '-=.3');
```

## Scrub e pin

```js
gsap.to('.panel-inner', {
  xPercent: -100 * (panels.length - 1), ease: 'none',
  scrollTrigger: {
    trigger: '.panels', pin: true, scrub: 1,
    end: () => '+=' + document.querySelector('.panels').offsetWidth
  }
});
```

## Parallasse

```js
gsap.utils.toArray('[data-parallax]').forEach(el => {
  gsap.fromTo(el, { yPercent: -12 }, {
    yPercent: 12, ease: 'none',
    scrollTrigger: { trigger: el.parentElement, scrub: true }
  });
});
```

## Smooth scroll con Lenis

```js
const lenis = new Lenis({ duration: 1.1, smoothWheel: true });
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add(t => lenis.raf(t * 1000));
gsap.ticker.lagSmoothing(0);
```

## FLIP per filtri

```js
const state = Flip.getState('.grid .item');
applyFilter();                        // modifica DOM / display
Flip.from(state, { duration: .6, ease: 'power2.inOut', stagger: .03,
  absolute: true, onEnter: e => gsap.fromTo(e, {opacity:0,scale:.8},{opacity:1,scale:1}) });
```

## Image sequence su canvas

```js
const frames = 120, img = new Image(), seq = { i: 0 };
gsap.to(seq, { i: frames - 1, snap: 'i', ease: 'none',
  scrollTrigger: { trigger: '.seq', pin: true, scrub: .5, end: '+=3000' },
  onUpdate: () => { img.src = `/frames/${String(seq.i).padStart(4,'0')}.webp`; }
});
img.onload = () => ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
```
Precaricare tutti i frame in un array prima di avviare.
