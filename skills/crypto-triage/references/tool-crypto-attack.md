# tools/crypto_attack.py

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

list names implemented attacks; the router emits the
exact invocation per attack. Absent -> the depth
file's stdlib recipe.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
