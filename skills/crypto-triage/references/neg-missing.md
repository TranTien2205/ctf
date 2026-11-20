# Negative: missing material

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

The attack needs two signatures and one exists -
the falsifier fires; escalate to writeup search
rather than inventing the missing half.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
