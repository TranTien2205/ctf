# Observable: many small equations

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Approximate linear relations, hidden number, small
private key with hints - lattice families. ctf-crypto
owns LLL; the router names it when the observable is
an approximate-equation bundle.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
