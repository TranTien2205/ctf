# LFSR recovery

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

A bit generator with linear structure - Berlekamp-
Massey recovers taps from ~2L bits. Falsifier: the
output is not linear (nonlinear combiner).

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
