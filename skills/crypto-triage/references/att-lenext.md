# Length extension

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

hash(secret || msg) + append -> hash(secret || msg
|| pad || append) without the secret. Falsifier:
HMAC or SHA-3 - the construction is immune.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
