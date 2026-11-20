# Common modulus

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Same n, two coprime e's, same m -> Bezout recovers m.
Falsifier: gcd(e1,e2) != 1.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
