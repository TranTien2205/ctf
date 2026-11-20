# ECB oracle

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Byte-at-a-time: control a prefix, watch blocks align.
Falsifier: the ciphertext changes every encryption
of the same plaintext - not ECB.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
