# Question: what is already known

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Known plaintext, known IV, known half the key -
the known material converts impossible attacks
into cheap ones.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
