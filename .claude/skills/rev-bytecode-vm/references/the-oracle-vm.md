# The VM as an oracle — the byte-by-byte

A fail-fast checker leaks position: run `flag{AAAA...}` — the fail
position tells how many bytes were right. Incrementally fix each
byte.

## The requirement

The VM must fail at the FIRST wrong byte (a linear cmp chain) —
then each position is independently bruteable through the oracle.
