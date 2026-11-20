# RSA small-e broadcast

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Same message under e different n's -> Hastad broadcast.
Falsifier: the messages differ or count < e. e=3 with
unpadded c is the related single-key case: c^(1/3).

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
