# The routing pipeline

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

observable -> named attack -> falsifier -> tool invocation ->
depth file. Every step is cheap; the expensive work lives in
the depth file the router names.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
