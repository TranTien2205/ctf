# Falsifier: no oracle

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

The interface encrypts but never decrypts, leaks no
valid/invalid signal - padding-oracle and ECB-byte-
at-a-time both die.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
