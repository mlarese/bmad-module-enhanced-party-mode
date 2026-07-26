# Enhanced Party Mode (`epm`)

Modulo BMad: consiglio di esperti per party mode e cantiere — craft FE, motion, GDPR, tech/AI law, infra, WordPress, fiscale.

| | |
|---|---|
| **Code** | `epm` |
| **Setup skill** | `epm-setup` |
| **Requires** | [BMad Method](https://github.com/bmad-code-org/bmad-method) v6+ (`npx bmad-method`) |

## Agenti

| Skill | Persona | Ruolo |
|---|---|---|
| `agent-frontend-taste` | Vesper | Craft frontend |
| `agent-web-animations` | Vera Motion | Motion web |
| `agent-gdpr-counsel` | Jane Privacy | GDPR / privacy IT-UE |
| `agent-tech-law-counsel` | Elena Giuridis | Tech / AI law |
| `agent-it-infra-expert` | Rex Wire | Sysadmin / SRE |
| `agent-wordpress-expert` | Niki Press | WordPress craft |
| `agent-world-cpa` | Commercialista Mondiale | Fiscale / contabile |

## Installazione

### Interattivo

```bash
npx bmad-method install
```

Dopo i moduli ufficiali, rispondi sì a *custom source* e incolla:

```text
https://github.com/mlarese/bmad-module-enhanced-party-mode
```

### Non-interattivo

```bash
npx bmad-method install \
  --directory . \
  --modules bmm \
  --custom-source https://github.com/mlarese/bmad-module-enhanced-party-mode \
  --tools cursor \
  --yes
```

Locale (sviluppo):

```bash
npx bmad-method install \
  --directory ~/mio-progetto \
  --custom-source /path/to/bmad-module-enhanced-party-mode \
  --tools cursor \
  --yes
```

Poi in IDE: attiva **`epm-setup`** (o “setup Enhanced Party Mode” / “install epm module”) per registrare config + `bmad-help`.

## Help codes

| Code | Capability |
|---|---|
| `SU` | Setup / configure modulo |
| `VX` | Vesper |
| `VR` | Vera Motion |
| `JP` | Jane Privacy |
| `EG` | Elena Giuridis |
| `RW` | Rex Wire |
| `NP` | Niki Press |
| `CP` | Commercialista Mondiale |

## Struttura

```text
.
├── .claude-plugin/marketplace.json
├── skills/
│   ├── epm-setup/
│   ├── agent-frontend-taste/
│   ├── agent-web-animations/
│   ├── agent-gdpr-counsel/
│   ├── agent-tech-law-counsel/
│   ├── agent-it-infra-expert/
│   ├── agent-wordpress-expert/
│   └── agent-world-cpa/
├── LICENSE
└── README.md
```

## Aggiornamento

```bash
npx bmad-method install --action quick-update
```

Oppure riesegui `epm-setup`.

## Licenza

MIT — vedi [LICENSE](./LICENSE).
