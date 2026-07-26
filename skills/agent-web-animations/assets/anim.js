/* anim.js - runtime animazioni senza dipendenze.
   Attiva: reveal [data-anim], parallasse [data-parallax], counter [data-count],
   curtain [data-curtain], header .hdr, accordion .acc, marquee duplicato automatico.

   REPEAT di default: enter → .is-visible, leave → rimuove .is-visible.
   One-shot solo con data-anim-once sull'elemento. */
(function () {
  'use strict';
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.documentElement.classList.remove('no-js');

  /* ---------- Reveal (repeat default) ---------- */
  var els = document.querySelectorAll('[data-anim]');
  if (reduce) {
    els.forEach(function (el) { el.classList.add('is-visible'); });
  } else if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var el = e.target;
        if (e.isIntersecting) {
          el.classList.add('is-visible');
          if (el.dataset.animOnce !== undefined) io.unobserve(el);
        } else if (el.dataset.animOnce === undefined) {
          el.classList.remove('is-visible');
        }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });

    var groups = {};
    els.forEach(function (el) {
      var key = el.dataset.animGroup || 'g';
      groups[key] = (groups[key] || 0);
      el.style.setProperty('--i', groups[key]++ % 10);
      io.observe(el);
    });
  } else {
    els.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------- Curtain (repeat) ---------- */
  var curtains = document.querySelectorAll('[data-curtain]');
  if (curtains.length) {
    if (reduce) {
      curtains.forEach(function (el) { el.classList.add('is-open'); });
    } else if ('IntersectionObserver' in window) {
      var curtainIo = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          e.target.classList.toggle('is-open', e.isIntersecting);
        });
      }, { threshold: 0.2, rootMargin: '0px 0px -10% 0px' });
      curtains.forEach(function (el) { curtainIo.observe(el); });
    }
  }

  /* ---------- Parallasse ---------- */
  var px = [].slice.call(document.querySelectorAll('[data-parallax]'));
  if (px.length && !reduce && innerWidth > 768) {
    var ticking = false;
    var run = function () {
      var vh = innerHeight;
      px.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < -100 || r.top > vh + 100) return;
        var speed = parseFloat(el.dataset.parallax) || 0.18;
        var off = (r.top + r.height / 2 - vh / 2) * -speed;
        el.style.transform = 'translate3d(0,' + off.toFixed(1) + 'px,0)';
      });
      ticking = false;
    };
    addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(run); }
    }, { passive: true });
    run();
  }

  /* ---------- Counter (repeat: azzera in uscita) ---------- */
  var counters = document.querySelectorAll('[data-count]');
  if (counters.length) {
    var ease = function (t) { return 1 - Math.pow(1 - t, 3); };
    var start = function (el) {
      var to = parseFloat(el.dataset.count) || 0;
      var dur = parseInt(el.dataset.countDur, 10) || 1600;
      if (reduce) { el.textContent = to.toLocaleString(); return; }
      var t0 = performance.now();
      (function step(now) {
        var p = Math.min((now - t0) / dur, 1);
        el.textContent = Math.round(to * ease(p)).toLocaleString();
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    };
    var cio = new IntersectionObserver(function (en) {
      en.forEach(function (e) {
        if (e.isIntersecting) start(e.target);
        else if (e.target.dataset.animOnce === undefined) e.target.textContent = '0';
      });
    }, { threshold: 0.4 });
    counters.forEach(function (c) { cio.observe(c); });
  }

  /* ---------- Header ---------- */
  var hdr = document.querySelector('.hdr');
  if (hdr) {
    var last = 0, hTick = false;
    addEventListener('scroll', function () {
      if (hTick) return; hTick = true;
      requestAnimationFrame(function () {
        var y = scrollY;
        hdr.classList.toggle('is-scrolled', y > 60);
        hdr.classList.toggle('is-hidden', y > last && y > 220);
        last = y; hTick = false;
      });
    }, { passive: true });
  }

  /* ---------- Accordion ---------- */
  document.querySelectorAll('.acc__trigger').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var acc = btn.closest('.acc');
      var open = acc.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  /* ---------- Marquee: duplica il track ---------- */
  document.querySelectorAll('.marquee').forEach(function (m) {
    var track = m.querySelector('.marquee__track');
    if (track && m.children.length === 1) m.appendChild(track.cloneNode(true));
  });
})();
