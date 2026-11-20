# Trap: assuming RSA

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Any n/e/c-looking triple is not automatically RSA -
check for curve params, a script doing custom ops,
or a non-RSA structure.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
