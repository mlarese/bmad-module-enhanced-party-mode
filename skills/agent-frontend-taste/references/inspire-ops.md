# Inspiration Ops

How to scout Awwwards, Dribbble, and Envato Elements reliably. Load from AW (one hop). Not a capability.

## Batch entry (prefer this)

```bash
uv run scripts/hero_sample.py --surface marketing
uv run scripts/hero_sample.py --activity ristorante --count 40   # Envato vertical (~100 pool)
uv run scripts/hero_sample.py --surface mobile --activity hotel # web app mobile + vertical
uv run scripts/hero_sample.py --surface dashboard --count 30
uv run scripts/hero_sample.py --list-activities
```

| Flag | Effect |
|------|--------|
| `--surface marketing` | Landing; senza activity → Awwwards/Dribbble (come prima) |
| `--activity <tipo>` | Envato `/web-templates/{categoria}` (2+ cat ≈ pool ~100). **Valuta 30–50**, non 100 in chat |
| `--surface mobile` | Envato `mobile` · `mobile-app` · `pwa` · `progressive-web-app` |
| `--surface mobile --activity …` | Vertical + mobile catalogs insieme |
| `--surface dashboard` | Envato admin (invariato) |

**Misurato 2026-07-26:** Dribbble `?q=` ignora il termine (stesso set). Non usare DRB search per l’attività. Envato category paths sì.

Seed `YYYYMMDDHH` → a different set each hour. Scorciatoia correzione piccola → no batch.

Extract **structure** only — never hex/assets. Invented URLs or cloning one Envato template = failure.

**DESIGN.md modelli:** `references/design-md-landing.md` · `design-md-dashboard.md` · `design-md-saas.md` · `design-md-mobile-web-app.md`.

Dopo il batch ≥30 annota anche la **chrome geometry** (angoli): conta sharp / soft / rounded / pill sui migliori 8–12 e dichiara `radius_family` coerente col mix **e** con activity (vedi `craft-rules.md` → Chrome geometry). Non defaultare a box quadrati.

**Misura, non impressioni.** Su 2–4 riferimenti migliori esegui `awwwards-scout.py --site <slug> --inspect` (o `--live <url>`): segue il sito premiato e conta sul CSS reale famiglie/tracking/leading, `repeat(N)` e `grid-column` espliciti vs `span`, `text-align` / `justify-self`, hairline solid vs dashed, `background-size`, radial vs linear, blend, blur, `data-theme`. Da quei conteggi ricavi `grid_system`, `alignment_map`, `bleed_rhythm`, `surface_texture`, `type_voices`, `type_scale`. Costo: ~5 request per sito (`--css-limit` per alzare/abbassare).

---

## Envato Elements (dashboard primary)

Canonical (no ad tracking):  
https://elements.envato.com/web-templates/admin-templates

| Path | Role |
|------|------|
| `/web-templates/admin-templates` | **Primary** admin HTML / dashboard kits |
| `/web-templates/dashboard` | Sister catalog (rotate groups) |
| `/web-templates/admin-dashboards` | Sister catalog |

`?page=` does not change SSR item set — rotate catalogs + hourly seed instead.

```bash
uv run scripts/envato_admin_scout.py --sample 30
uv run scripts/envato_admin_scout.py --list --limit 40
```

**Ampiezza vera (centinaia, non 30):** i tag path `/web-templates/admin-templates/{tag}` rendono 48 item ciascuno e sono largamente disgiunti — 22 tag = 560 unici, e il tag è anche un tratto. `dashboard_corpus.py` li raccoglie insieme alla GitHub search API e salva `assets/dashboard-corpus.json`; `dashboard_recipe.py` ci pesa sopra le decisioni. Dettagli e leve morte (`all-items?terms=` ignora il termine, ThemeForest 403): `references/dashboard-rules.md`.

---

## Envato Elements (mobile / PWA)

**Le leve non sono le stesse degli admin.** Misurato 2026-07-26:

| Superficie | Resa | Nota |
|------|------|------|
| `/web-templates/{mobile, mobile-app, pwa, progressive-web-app, mobile-website}` | 48 item ciascuno, overlap 3–27% | cataloghi core |
| `+ {ui-kits, app-landing-page, ionic, flutter, food-delivery, fitness, banking, travel, onboarding, splash-screen, gradient}` | 48 ciascuno, overlap **0–8%** | **la leva di ampiezza**: 16 cataloghi ≈ 610 unici |
| `/web-templates/mobile/{tag}` | **stessi 48 del catalogo base** | **leva morta**: il tag è ignorato server-side — l'opposto degli admin |

**Il nome del catalogo non è automaticamente un tratto.** Fedeltà misurata (quanti item confermano il tema del catalogo): `food-delivery` 100% · `fitness` 93% · `mobile` 90% · `pwa` 68% · `ui-kits` 62% — ma `flutter` 10% · `splash-screen` 6% · `onboarding` 5% · `gradient` 0% · `ionic` 0%. I secondi sono etichette di vetrina: allargano il corpus, non timbrano un tratto.

```bash
uv run scripts/mobile_corpus.py --build     # ~22 request → assets/mobile-corpus.json
uv run scripts/mobile_corpus.py --stats
```

**Per il craft grafico (splash, fondo di marca, onboarding) il corpus non serve:** zero tratti onesti su 866 item. Si guarda **a mano** — vedi Figma Community sotto. Regole: `references/mobile-rules.md`.

---

## Figma Community — solo a mano

`figma.com/community/mobile-apps?resource_type=files` è la fonte giusta per splash e fondi veri, ed è **la sola che non si automatizza**: il `robots.txt` di Figma dichiara `User-Agent: anthropic-ai → Disallow: /`, più `Disallow: /api/*` e `/community/search?*`.

Nessuno scout, nessun corpus, nessuna fetch di raccolta. L'owner apre la pagina nel browser e i reperti entrano nel craft a voce. Un umano che sfoglia non è un crawler; un agente che raccoglie sì.

After ≥30: write **mix notes** (nav / tables / KPI / theme chrome / **corner language: sharp·soft·pill**) — blend best concepts, do not clone one item. Do not scrape Envato `/api/*`.

---

## Awwwards (marketing / live sites)

| Path | Status | Note |
|------|--------|------|
| `/` | 200 | Home, SOTD |
| `/websites/` | 200 | Site list → `/sites/{slug}` |
| `/websites/sites_of_the_day/` | 200 | ~30 unique site links |
| `/websites/sites_of_the_month/` | 200 | idem |
| `/websites/nominees/` | 200 | idem |
| `/websites/best-of/` | 200 | idem |
| `/collections/` | 200 | collections |
| `/sites/{slug}/` | 200 (occasional 502) | retry once |

Weak/intermittent: `/inspiration/...`, `/blog/`. WebFetch MCP: Varnish 302 — **unreliable**.

Robots: `Disallow: /websites/?` — no query-string lists. Avoid `/search-websites`, `/vote/`, `/preview/`.

```bash
uv run scripts/awwwards-scout.py --list sotd --limit 12
uv run scripts/awwwards-scout.py --site spotify-wrapped-party            # title + og:desc + URL live
uv run scripts/awwwards-scout.py --site terminal-industries --inspect    # + conteggi su CSS live
uv run scripts/awwwards-scout.py --live https://siena.film               # salta Awwwards
```

La detail page Awwwards porta **solo** `<title>` + `og:description`: senza `--inspect` non hai segnale strutturale. L’URL live si legge dal link `nofollow` della pagina; se manca, il tool lo dichiara.

---

## Dribbble (UI / templates)

| Path | Status | Note |
|------|--------|------|
| `/tags/website-template` | empty | robots `/*/tags/*` — **do not use** |
| `/search/*` | blocked | robots Disallow |
| `/shots?q=website+template` | 200 | operational equivalent of website-template |
| `/shots` | 200 | recent feed |
| `/` | 200 | home cards |

Detail pages can be bot-gated — list titles + URLs are enough for craft.

```bash
uv run scripts/dribbble-scout.py --list website-template --limit 12
uv run scripts/dribbble-scout.py --list shots --limit 12
```

Filter logo-only shots in the prompt. Prefer admin/saas/crm queries when surface is dashboard.

---

## Source balance

| Job | Primary | Secondary |
|-----|---------|-----------|
| Landing generica (no activity) | Awwwards + Dribbble | — |
| Landing tipizzata (`--activity`) | **Envato web-templates/{cat}** | Awwwards |
| Web app mobile (`--surface mobile`) | **Envato mobile / PWA** (16 cataloghi) | Awwwards; + vertical se `--activity` |
| Mobile — **craft grafico** (splash, fondo, icona) | **Figma Community, a mano** | Dribbble — il corpus non copre |
| Dashboard / admin | **Envato admin-templates** | Dribbble, Awwwards |
| Cinematic full-page | Awwwards | Dribbble |

If one source fails: declare the gap; proceed with the other or stated structural principles.

## Ethics

Few requests, honest User-Agent, no vote/like/follow/download automation. Internal craft references only — not mirrors of awarded sites or Envato assets.
