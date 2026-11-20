# Monoalphabetic substitution

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Frequency-mapped letter swap - chi-squared against
English. Falsifier: letter frequencies stay flat -
polyalphabetic (Vigenere) instead.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
