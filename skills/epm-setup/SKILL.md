---
name: "epm-setup"
description: Verifies the Enhanced Party Mode install and, on legacy YAML projects only, consolidates its config. Use when the user requests to 'install epm module', 'configure Enhanced Party Mode', 'setup Enhanced Party Mode', or asks whether the epm install is complete.
---

# Module Setup

## L'installazione basta — e questa skill lo verifica, non lo rifà

Per mesi questo skill è stato **il secondo passo obbligatorio**: l'installer copiava
le skill, e i due file *consolidati* — la config di progetto e il catalogo di
`bmad-help` — li scriveva lui. Era vero quando quei file erano YAML.

**Non lo è più.** Misurato il 2026-07-29 su un'installazione vera
(`bmad-method` 6.10.0, `--modules bmm,epm --custom-source`): l'installer scrive già
`_bmad/config.toml` con **tutti e sette** gli agenti del consiglio
(`module = "epm"`, nome, titolo, icona, descrizione, presi da `assets/module.yaml`)
e `_bmad/_config/bmad-help.csv` con **8 righe su 8** di `assets/module-help.csv`.
`resolve_config.py` — quello che `bmad-help` usa davvero — li risolve tutti e
sette. I file YAML `_bmad/config.yaml` e `_bmad/module-help.csv` non esistono, e
in tutto il progetto installato gli **unici** riferimenti a loro stanno dentro
questo skill.

**Quindi: dopo l'installer non c'è niente da lanciare.** Il primo passo di questa
skill è misurarlo:

```bash
uv run ./scripts/verify-install.py "{project-root}"
```

- **`0`** — l'installazione basta. Dillo e **fermati qui**: non eseguire nessuno
  degli script di merge o di pulizia. Hai finito.
- **`1`** — manca qualcosa, e il referto dice cosa (quale agente, quale voce di
  aiuto). Su un progetto TOML la cura è **reinstallare** elencando `epm` fra i
  moduli, non il merge YAML.
- **`2`** — progetto della **generazione YAML** (c'è `_bmad/config.yaml`, non
  `config.toml`): lì il merge di sotto serve ancora, ed è l'unico caso in cui si
  esegue.

## Il merge di oggi non è inutile: è distruttivo

Non è una preferenza di stile — è misurato, eseguendolo su una copia di
un'installazione vera. La procedura che questo file descriveva:

- `merge-config.py --legacy-dir` e `merge-help-csv.py --legacy-dir` **cancellano**
  `_bmad/epm/config.yaml` e `_bmad/epm/module-help.csv`, che nella generazione
  TOML sono **output dell'installer**, non residui;
- `cleanup-legacy.py --also-remove _config` **cancella `_bmad/_config/`**, cioè
  `bmad-help.csv` — il catalogo consolidato di **tutti** i moduli, non solo di
  epm. Provato: `files_removed_count: 8`, catalogo sparito, `bmm` e `core`
  inclusi. Il suo controllo di sicurezza è passato con `verified_skills: []`:
  aveva verificato zero skill, perché quelle cartelle non ne contengono più.

Per questo l'ordine è: **prima `verify-install.py`, e su `0` si smette**.

---

## Solo su progetti di generazione YAML (`verify-install.py` → `2`)

Quanto segue vale **esclusivamente** lì. Se `_bmad/config.toml` esiste, non
eseguirlo: non serve, e fa i danni descritti sopra.

Module identity (name, code, version) comes from `./assets/module.yaml`. Collects user preferences and writes them to three files:

- **`{project-root}/_bmad/config.yaml`** — shared project config: core settings at root (e.g. `output_folder`, `document_output_language`) plus a section per module with metadata and module-specific values. User-only keys (`user_name`, `communication_language`) are **never** written here.
- **`{project-root}/_bmad/config.user.yaml`** — personal settings intended to be gitignored: `user_name`, `communication_language`, and any module variable marked `user_setting: true` in `./assets/module.yaml`. These values live exclusively here.
- **`{project-root}/_bmad/module-help.csv`** — registers module capabilities for the help system.

Both config scripts use an anti-zombie pattern — existing entries for this module are removed before writing fresh ones, so stale values never persist.

`{project-root}` is a **literal token** in config _values_ (the data written into the files above) — never substitute it there. It signals to the consuming LLM that the value is relative to the project root, not the skill root. **This does not apply to the filesystem path _arguments_ passed to the scripts below** (the `--*-path`, `--*-dir`, and `--target` arguments): those are real paths, so you **must** resolve `{project-root}` to the actual project root before running, or the scripts will write to a literal `{project-root}/` directory under the skill folder. The scripts reject an unresolved token with an error.

### Collect Configuration

If the user provides arguments (e.g. `accept all defaults`, `--headless`, or inline values like `user name is BMad, I speak Swahili`), map any provided values to config keys, use defaults for the rest, and skip interactive prompting. Still display the full confirmation summary at the end.

Ask the user for values. Show defaults in brackets. Present all values together so the user can respond once with only the values they want to change. Never tell the user to "press enter" or "leave blank" — in a chat interface they must type something to respond.

**Default priority** (highest wins): existing new config values > legacy config values > `./assets/module.yaml` defaults. Only keys that match the current schema are carried forward.

**Core config** (only if no core keys exist yet): `user_name` (default: BMad), `communication_language` and `document_output_language` (default: English — ask as a single language question, both keys get the same answer), `output_folder` (default: `{project-root}/_bmad-output`). Of these, `user_name` and `communication_language` are written exclusively to `config.user.yaml`.

**Module config**: `epm` declares **no variables** — there is nothing to ask. Only core config applies.

### Write Files

Write a temp JSON file with the collected answers structured as `{"core": {...}, "module": {...}}` (omit `core` if it already exists). Values inside this JSON keep the literal `{project-root}` token. Replace `{project-root}` in every path argument with the actual project root before running — these are filesystem paths, not config values.

```bash
python3 ./scripts/merge-config.py --config-path "{project-root}/_bmad/config.yaml" --user-config-path "{project-root}/_bmad/config.user.yaml" --module-yaml ./assets/module.yaml --answers {temp-file} --legacy-dir "{project-root}/_bmad"
python3 ./scripts/merge-help-csv.py --target "{project-root}/_bmad/module-help.csv" --source ./assets/module-help.csv --legacy-dir "{project-root}/_bmad" --module-code epm
```

Both scripts output JSON to stdout with results. If either exits non-zero, surface the error and stop. `--legacy-dir` is what **preserves the answers already given** instead of resetting everything to defaults. Run `./scripts/merge-config.py --help` or `./scripts/merge-help-csv.py --help` for full usage.

### Create Output Directories

Resolve the `{project-root}` token to the actual project root and create each path-type value from `config.yaml` that does not yet exist — this includes `output_folder` and any module variable whose value starts with `{project-root}/`. The paths stored in the config files must keep the literal token; only the directories on disk use resolved paths. Use `mkdir -p` or equivalent.

### Cleanup

`cleanup-legacy.py` removes the installer's package directories once their skills are installed at `.claude/skills/`. It verifies that every skill in those directories exists at `.claude/skills/` before removing anything, and missing directories are not errors.

**Never pass `--also-remove _config`**: in any project that has seen a TOML-era installer that directory holds `bmad-help.csv` for every module, and the script's safety check does **not** protect it — it only verifies skills, and `_config/` contains none, so it is removed directly.

```bash
python3 ./scripts/cleanup-legacy.py --bmad-dir "{project-root}/_bmad" --module-code epm --skills-dir "{project-root}/.claude/skills"
```

---

## Confirm

On a TOML project: report the `verify-install.py` result — how many agents are registered, how many help rows are in the consolidated catalog — and say plainly that nothing else was needed. On a YAML project: report what the merge scripts wrote, whether it was a fresh install or an update, and any legacy files migrated. Then display the `module_greeting` from `./assets/module.yaml` to the user.

## Outcome

Once the user's `user_name` and `communication_language` are known (from collected input, arguments, or existing config), use them consistently for the remainder of the session: address the user by their configured name and communicate in their configured `communication_language`.
