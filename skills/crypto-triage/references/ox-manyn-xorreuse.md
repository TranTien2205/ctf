# Observable cell: many-n / xor-reuse

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

Whether the `many-n` observable names the `xor-reuse` attack.

## Read

Primary-signal, secondary, or ruled-out for this pairing -
the observable's shape against the attack's precondition.
The falsifier is stated for every non-ruled-out cell.

## Next

Primary-signal -> run the falsifier, then the tool
invocation; ruled-out -> the cell says why so it is
never revisited.
