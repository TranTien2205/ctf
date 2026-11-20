# Format: hex blob

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Raw hex ciphertext - byte length names block vs
stream; 16-byte multiples suggest a block cipher.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
