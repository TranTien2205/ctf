# Falsifier first

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Every named attack carries a falsifier that rules it out in
seconds: e too big, n not factorable, no padding oracle.
Run the falsifier before the attack.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
