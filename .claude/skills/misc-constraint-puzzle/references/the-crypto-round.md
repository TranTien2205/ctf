# Small crypto rounds — nonce/hash

`find x s.t. sha256(x+salt) starts 000` — brute-force loop in the
solver; the deadline makes the language choice matter but the loop
is still just a loop.

## The loop

Bounded brute-force; the deadline bounds N.
## The bound

Deadline bounds the search space.
