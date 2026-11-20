# Observable: block ciphertext + oracle

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Fixed-size ciphertext blocks with an encrypt/decrypt/
padding interface - block-cipher.md. ECB vs CBC is the
first discrimination: equal plaintext blocks -> equal
cipher blocks means ECB.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
