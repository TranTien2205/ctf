# Observable: sequential outputs

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

A generator emitting outputs - MT19937 needs 624
consecutive 32-bit outputs to clone; an LCG needs ~3.
Count the outputs before naming the attack.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
