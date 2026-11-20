# Padding oracle

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

A decrypt endpoint answering valid/invalid padding ->
byte-by-byte recovery. Falsifier: one uniform error
for every failure - no oracle.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
