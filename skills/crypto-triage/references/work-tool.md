# The tool invocation

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

tools/crypto_attack.py list names the implemented attacks;
the router hands the one-line invocation. An attack not in
the tool gets a stdlib recipe in its depth file.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
