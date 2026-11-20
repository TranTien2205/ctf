# Corpus index

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

references/: work-*/obs-*/att-*/fal-*/fmt-*/tool-*/
q-*/trap-*/neg-*/ox-*/ax-*/sx-* plus the seven base
files and -route companions.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
