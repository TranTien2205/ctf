# Crypto (pycryptodome)

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

AES/DES/RSA/ECC operations, number theory helpers -
present; use it rather than reimplementing.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
