# Falsifier: not RSA

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

No n/e/c, no key material - a ciphertext alone is not
an RSA observable. Reclassify.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
