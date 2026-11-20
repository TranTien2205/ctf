# Question: what does the interface answer

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

encrypt, decrypt, padding-valid, sign, verify -
each response type opens a different attack list.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
