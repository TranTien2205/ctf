# Trap: brute-forcing a key

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

A 128-bit key is never brute-forced; if brute force
looks necessary, the attack classification is wrong.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
