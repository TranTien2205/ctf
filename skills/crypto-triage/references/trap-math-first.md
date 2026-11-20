# Trap: deriving before classifying

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Writing the math before the observable names the
attack - the router exists so the classification
comes first.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
