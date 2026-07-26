---
name: awwwards-research
description: Scouting Awwwards + Dribbble + Envato; batch ≥30; mix concetti
code: AW
added: 2026-07-25
type: prompt
---

# Inspiration Research

## Com'è fatto un lavoro riuscito
Set **≥30** (seed data+ora) → **2–5 principi strutturali** (mix, non clone). Inventare URL o clonare un template Envato = fallimento.

| Superficie | Fonti |
|------------|--------|
| marketing / home (no activity) | Awwwards + Dribbble (lenti hero) |
| marketing + `--activity` | **Envato web-templates/{cat}** primario + Awwwards |
| mobile web app | **Envato mobile / mobile-app / PWA** (+ activity cats se tipizzato) |
| dashboard / admin | **Envato admin-templates** primario + Dribbble/Awwwards |

## Le cose che non si indovinano: si applicano
- Load `references/inspire-ops.md` (CLI, URL, ethics). Scorciatoia correzione piccola → no batch.
- Prefer `hero_sample.py --surface marketing|dashboard|mobile [--activity …]`; Envato-only admin via `envato_admin_scout.py --sample 30`.
- Se l’owner dice **mobile** (web app / PWA / task app): `--surface mobile` obbligatorio nel batch — non bastare “landing responsive”.
- Estrai struttura; non hex/asset. Gap → dichiara e prosegui.
- Su 2–4 riferimenti migliori: `awwwards-scout.py --site <slug> --inspect` → **conteggi misurati** sul CSS live. Senza `--inspect` hai solo title+description, cioè zero segnale.
- Annota dai conteggi: **corner language** (`radius_family`), **griglia** (repeat(N) · rail · grid-column espliciti vs span → `grid_system`), **allineamenti** (text-align / justify-self → `alignment_map`), **superfici** (hairline · background-size · radial vs linear · blend → `surface_texture`), **tipografia** (famiglie distinte · tracking a due poli · leading → `type_voices` / `type_scale`).
