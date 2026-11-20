# ecdsa library

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Present - curve arithmetic and key handling for the
ECC attacks.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
