# Observable: hash + length

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

A MAC of secret||message or a collision task -
hash-attacks.md. Length-extension needs an MD5/SHA1/
SHA256 MAC shape; the falsifier is the hash's structure.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
