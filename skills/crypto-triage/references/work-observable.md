# Reading the observable

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

The handout's actual bytes: key size, exponent, ciphertext
shape, script operations, oracle interface. The observable
names the attack before any math.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
