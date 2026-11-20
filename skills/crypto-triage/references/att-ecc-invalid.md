# Invalid curve attack

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

A server doing scalar multiplication on a supplied
point - submit low-order points on curves with smooth
order. Falsifier: the server validates on-curve.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
