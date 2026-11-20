# Question: how big is the modulus

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

n size bounds the attack: <250 digits factorable,
512 sport, 1024+ not factorable - the size answer
kills half the attack list instantly.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
