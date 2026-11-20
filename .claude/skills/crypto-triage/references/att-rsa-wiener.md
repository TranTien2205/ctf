# RSA small private exponent

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

d < n^(1/4)/3 -> Wiener continued fractions; d a bit
larger -> Boneh-Durfee (ctf-crypto). Falsifier: e near
n means d is large.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
