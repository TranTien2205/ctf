# Observable: (n, e, c) tuple

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

A PEM key or an n/e/c triple in the handout - RSA. The
first questions: e small? n factorable? c a textbook
encryption? rsa-attacks.md owns the depth.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
