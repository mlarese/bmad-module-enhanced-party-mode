---
name: migrate
description: Migrazioni/upgrade WP con rollback
code: MG
added: 2026-07-25
type: prompt
---

# Migrate

## What Success Looks Like
L'owner ha un piano di migrazione/upgrade **con rollback** che include, obbligatoriamente e in chiaro: (1) backup pre-cutover, (2) **WP-CLI `search-replace`** (o equivalente serializzato-safe) per URL/path — mai sed/regex ciechi sul dump come percorso raccomandato, (3) cutover DNS/host, (4) smoke test post-go-live, (5) failback esplicito. "Copia i file via FTP e spera" è fallimento. Un piano lungo senza `search-replace` (o equivalente safe) è fallimento.

## Non-inferables
- Conferma da→a (host, domain, PHP/WP version) prima della sequenza.
- Nel piano scritto deve comparire il comando o l'equivalente: `wp search-replace 'old' 'new' --all-tables` (o tool serializzato-safe documentato). Mai raccomandare sed/find-replace grezzi sul SQL.
- Ordine tipico: backup → staging prove (incluso search-replace dry-run se possibile) → cutover → smoke test (login, permalink, form, checkout se Woo) → rollback pronto.
- Controlla MEMORY/BOND per ambienti e siti già migrati.
