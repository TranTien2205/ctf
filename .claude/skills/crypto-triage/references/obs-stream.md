# Observable: keystream or xor

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

A ciphertext xor'd against a repeating or generated
keystream - xor-analysis.md or stream families. Reused
keystream across two ciphertexts is the cheapest break.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
