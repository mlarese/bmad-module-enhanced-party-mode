#!/usr/bin/env bash
# analyze-site.sh <url> [outdir]
# Scarica una pagina con i suoi CSS e JS e rileva le librerie di animazione usate.
set -euo pipefail

URL="${1:?uso: analyze-site.sh <url> [outdir]}"
OUT="${2:-/tmp/anim-audit}"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"
mkdir -p "$OUT/assets"

echo "==> Download $URL"
curl -sSL -A "$UA" "$URL" -o "$OUT/page.html" || { echo "download fallito"; exit 1; }

BASE=$(echo "$URL" | sed -E 's#(https?://[^/]+).*#\1#')

echo "==> Estrazione asset"
grep -oE '(href|src)="[^"]+\.(css|js)[^"]*"' "$OUT/page.html" \
  | sed -E 's/^(href|src)="//;s/"$//' \
  | sort -u > "$OUT/assets.txt"

while read -r a; do
  case "$a" in
    //*) u="https:$a" ;;
    http*) u="$a" ;;
    /*) u="$BASE$a" ;;
    *) u="$BASE/$a" ;;
  esac
  n=$(echo "$u" | md5sum 2>/dev/null | cut -c1-8 || echo "$u" | md5 -q | cut -c1-8)_$(basename "${u%%\?*}")
  curl -sSL --max-time 20 -A "$UA" "$u" -o "$OUT/assets/$n" 2>/dev/null || true
done < "$OUT/assets.txt"

echo "==> Librerie rilevate"
scan() { # "$1" pattern, "$2" etichetta
  if grep -rqiE "$1" "$OUT/page.html" "$OUT/assets" 2>/dev/null; then
    printf '  [x] %s\n' "$2"
  fi
  return 0
}
scan 'gsap|TweenMax'                 'GSAP'
scan 'ScrollTrigger'                 'GSAP ScrollTrigger'
scan 'SplitText|splitting'           'Split text'
scan 'data-aos|aos\.(js|css)'        'AOS'
scan 'wow\.min|animate\.css|animated' 'animate.css / WOW'
scan 'wpb_animate_when_almost_visible' 'WPBakery css_animation'
scan 'elementor-motion|motion-fx|elementor-invisible' 'Elementor Motion Effects'
scan 'lenis'                         'Lenis smooth scroll'
scan 'locomotive-scroll'             'Locomotive Scroll'
scan 'swiper'                        'Swiper'
scan 'slick|owl-carousel|flickity'   'Slider legacy (slick/owl/flickity)'
scan 'revslider|rs-module|tp-banner' 'Slider Revolution'
scan 'lottie|bodymovin'              'Lottie'
scan 'rive'                          'Rive'
scan 'three\.(min\.)?js|THREE\.'     'three.js / WebGL'
scan 'tsparticles|particles\.js'     'Particles'
scan 'barba'                         'Barba.js page transitions'
scan 'framer-motion|motion/react'    'Framer Motion'
scan 'vanilla-tilt|tilt\.js'         'Tilt 3D'
scan 'scrollreveal'                  'ScrollReveal'
scan 'animation-timeline'            'Scroll-driven animations native'
scan 'view-transition'               'View Transitions API'
scan 'parallax'                      'Parallasse (marker generico)'
scan 'ken-?burns'                    'Ken Burns'

echo "==> Keyframes custom"
grep -rhoE '@keyframes[[:space:]]+[A-Za-z0-9_-]+' "$OUT/assets" 2>/dev/null \
  | sort -u | sed 's/^/  /' | head -40 || true

echo "==> Transizioni piu' usate"
grep -rhoE 'transition[^;{]*;' "$OUT/assets" 2>/dev/null \
  | sed 's/^[[:space:]]*//' | sort | uniq -c | sort -rn | head -12 || true

echo "==> Easing custom"
grep -rhoE 'cubic-bezier\([^)]*\)' "$OUT/assets" 2>/dev/null | sort | uniq -c | sort -rn | head -8 || true

echo
echo "Output in $OUT (page.html, assets/, assets.txt)"
