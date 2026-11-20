# Vigenere

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Repeating key - Kasiski or index of coincidence gives
key length, then per-column Caesar. Falsifier: IC
matches random text - not periodic.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
