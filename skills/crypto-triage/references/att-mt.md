# MT19937 cloning

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

624 consecutive outputs -> clone the state, predict
all future outputs. Falsifier: fewer outputs or
tempered output - partial-recovery territory.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
