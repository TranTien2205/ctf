# ECDSA nonce reuse

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Two signatures (r,s1),(r,s2) sharing r -> k from
(s1-s2), then d. Falsifier: different r values -
no reuse; check weak RNG or invalid-curve instead.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
