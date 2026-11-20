# CTR/stream nonce reuse

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Same keystream under two ciphertexts -> c1 xor c2
xor known plaintext. Falsifier: fresh nonce per
encryption.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
