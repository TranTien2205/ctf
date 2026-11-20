# LCG recovery

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

s1=a*s0+c mod m - three outputs solve a,c (known m),
or ~six recover m too. Falsifier: outputs are
truncated - the truncated-LCG variant applies.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
