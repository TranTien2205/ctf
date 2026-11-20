# Observable: curve parameters

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

p, a, b, G, n or a named curve (secp256k1, P-256) plus
points or signatures - ECC. Nonce reuse in two signatures
is the cheapest first check; ecc-attacks.md owns it.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
