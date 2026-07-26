---
name: woocommerce
description: Catalogo, checkout, estensioni WooCommerce lean
code: WC
added: 2026-07-25
type: prompt
---

# WooCommerce

## What Success Looks Like
L'owner ha un percorso shop **operativo**: catalogo/checkout/pagamenti/spedizioni con estensioni giustificate, senza pile di "must-have" Woo. Ogni raccomandazione dice perché serve e cosa rompe se la togli. Un carrello lento "risolto" aggiungendo tre plugin di speed è fallimento.

## Non-inferables
- Conferma versione Woo + tema/checkout custom prima di patch profonde.
- Preferisci hook Woo e override template in child theme rispetto a plugin overlay multipli.
- Segnala impatto su performance/cache/sessioni quando tocchi checkout.
- Controlla MEMORY/BOND per shop e gateway già in uso.
