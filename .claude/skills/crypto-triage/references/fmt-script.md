# Format: the generator script

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

A handout .py doing the crypto - read it for the
operations order; the vulnerability is a coding flaw,
not the primitive.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
