# Ricette CSS

## Token base

```css
:root{
  --ease-out-expo: cubic-bezier(.22,1,.36,1);
  --ease-in-out: cubic-bezier(.65,0,.35,1);
  --ease-back: cubic-bezier(.34,1.56,.64,1);
  --d-fast: .18s; --d-base: .32s; --d-slow: .8s; --d-hero: 1.4s;
}
```

## Reveal con stato iniziale in CSS

```css
[data-anim]{opacity:0;transform:translateY(28px);
  transition:opacity var(--d-slow) var(--ease-out-expo),
             transform var(--d-slow) var(--ease-out-expo);}
[data-anim="left"]{transform:translateX(-40px)}
[data-anim="zoom"]{transform:scale(.92)}
[data-anim="blur"]{filter:blur(12px)}
[data-anim].is-visible{opacity:1;transform:none;filter:none}
/* stagger */
[data-anim].is-visible{transition-delay:calc(var(--i,0)*90ms)}
```

## Clip-path wipe e mask reveal

Il wipe si fa con `mask-size`, non con `clip-path`: se l'elemento osservato da
IntersectionObserver ha un `clip-path` che ne azzera l'area, l'observer non scatta
mai e il reveal resta invisibile. Usa `clip-path` solo su un figlio non osservato.

```css
.wipe{
  -webkit-mask:linear-gradient(90deg,#000 0 0) 0 0/0% 100% no-repeat;
          mask:linear-gradient(90deg,#000 0 0) 0 0/0% 100% no-repeat;
  transition:mask-size 1s var(--ease-out-expo)
}
.wipe.is-visible{-webkit-mask-size:100% 100%;mask-size:100% 100%}

.mask{overflow:hidden}
.mask img{transform:scale(1.25);transition:transform 1.2s var(--ease-out-expo)}
.mask.is-visible img{transform:scale(1)}
```

## Ken Burns

```css
@keyframes kenburns{
  from{transform:scale(1) translate3d(0,0,0)}
  to{transform:scale(1.14) translate3d(-1.5%,-1.5%,0)}
}
.hero__bg{animation:kenburns 18s var(--ease-in-out) infinite alternate}
```

## Crossfade slider (solo CSS, N slide)

```css
.slider img{position:absolute;inset:0;object-fit:cover;opacity:0;
  animation:fadeCycle 18s infinite}
.slider img:nth-child(2){animation-delay:6s}
.slider img:nth-child(3){animation-delay:12s}
@keyframes fadeCycle{0%,28%{opacity:1}33%,100%{opacity:0}}
```

## Header sticky che si riduce

```css
.site-header{position:fixed;inset:0 0 auto;transition:
  transform var(--d-base) var(--ease-in-out),
  background-color var(--d-base), padding var(--d-base)}
.site-header.is-scrolled{padding-block:.5rem;background:rgba(255,255,255,.92);backdrop-filter:blur(10px)}
.site-header.is-hidden{transform:translateY(-100%)}
```

## Hover: zoom immagine + caption

```css
.card{overflow:hidden;position:relative}
.card img{transition:transform .7s var(--ease-out-expo)}
.card:hover img{transform:scale(1.07)}
.card__cap{transform:translateY(100%);opacity:0;
  transition:transform .45s var(--ease-out-expo),opacity .45s}
.card:hover .card__cap{transform:none;opacity:1}
```

## Bottone: riempimento e underline

```css
.btn{position:relative;overflow:hidden;isolation:isolate}
.btn::before{content:"";position:absolute;inset:0;background:currentColor;
  transform:scaleY(0);transform-origin:bottom;z-index:-1;
  transition:transform .35s var(--ease-out-expo)}
.btn:hover::before{transform:scaleY(1)}

.link{background-image:linear-gradient(currentColor,currentColor);
  background-size:0 1px;background-position:0 100%;background-repeat:no-repeat;
  transition:background-size .4s var(--ease-out-expo)}
.link:hover{background-size:100% 1px}
```

## Hamburger che diventa X

```css
.burger span{display:block;height:2px;background:currentColor;
  transition:transform .35s var(--ease-out-expo),opacity .2s}
.burger.is-open span:nth-child(1){transform:translateY(8px) rotate(45deg)}
.burger.is-open span:nth-child(2){opacity:0}
.burger.is-open span:nth-child(3){transform:translateY(-8px) rotate(-45deg)}
```

## Accordion fluido senza JS di misura

```css
.acc__body{display:grid;grid-template-rows:0fr;
  transition:grid-template-rows .4s var(--ease-in-out)}
.acc[open] .acc__body,.acc.is-open .acc__body{grid-template-rows:1fr}
.acc__body>div{overflow:hidden}
```

## Marquee infinito

```css
.marquee{overflow:hidden;display:flex;gap:2rem}
.marquee__track{display:flex;gap:2rem;flex:0 0 auto;animation:marquee 24s linear infinite}
@keyframes marquee{to{transform:translateX(-100%)}}
.marquee:hover .marquee__track{animation-play-state:paused}
```
Duplicare il track due volte nel markup.

## Skeleton shimmer

```css
.skeleton{background:linear-gradient(90deg,#eee 25%,#f5f5f5 37%,#eee 63%);
  background-size:400% 100%;animation:shimmer 1.4s ease infinite}
@keyframes shimmer{from{background-position:100% 0}to{background-position:0 0}}
```

## Scroll-driven animations native (no JS)

```css
@supports (animation-timeline: view()){
  .reveal{animation:fadeUp linear both;animation-timeline:view();
    animation-range:entry 10% cover 35%}
  .progress{animation:grow linear;animation-timeline:scroll(root)}
}
@keyframes fadeUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
```
Supporto: Chromium e Safari recenti. Tenere il fallback IntersectionObserver.

## View Transitions

```css
@view-transition{navigation:auto}          /* cross document */
.hero-img{view-transition-name:hero}       /* shared element */
::view-transition-old(root){animation:fadeOut .3s both}
::view-transition-new(root){animation:fadeIn .35s both}
```
```js
document.startViewTransition(() => updateDOM()); // same document
```

## Reduced motion (obbligatorio)

```css
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;
    transition-duration:.01ms!important;scroll-behavior:auto!important}
  [data-anim]{opacity:1!important;transform:none!important;filter:none!important}
}
```
