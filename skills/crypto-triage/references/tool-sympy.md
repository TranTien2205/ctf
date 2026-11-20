# sympy

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

factorint, discrete_log, gcd, mod_inverse, continued
fractions - the stdlib-plus workhorse behind most
router-named attacks.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
