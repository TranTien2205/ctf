# Shape cell: single-cipher / classical

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Whether the `single-cipher` ciphertext shape points at the
`classical` family.

## Read

Primary, possible, or ruled-out - the byte-shape against the
family's output grammar. The family's cheapest observable
confirms a `possible` before the router commits.
