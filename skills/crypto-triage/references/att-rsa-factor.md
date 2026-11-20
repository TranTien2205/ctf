# RSA factorable n

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

n in factordb, n with small p (Fermat), shared prime
across two n's (gcd). Falsifier: factordb miss and
no shared factor - then Wiener/Boneh-Durfee or give up
the factor route.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
