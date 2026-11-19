# Case studies — the challenge shapes seen in the wild

## Shape 1 — "the reused key"

Two JWTs or two raw signatures, same `r`. `ecdsa-nonce-reuse` → `d` → sign
an admin token / decrypt. The cheapest CTF shape.

## Shape 2 — "the weak RNG"

A signing service whose `k` is `time(NULL)` or a counter — `hnp-ecdsa`
with `--nonce-bound` covering the timestamp range. The `required_signatures`
count tells you how many oracle calls.

## Shape 3 — "the DIY curve"

Custom `p, a, b`. The gates in order: `#E == p`? → smart. `Δ == 0`? →
singular. `#E` smooth? → PH. Else → look at the *protocol* (the math is
hard; the bug is in the use).

## Shape 4 — "the point oracle"

Server multiplies your point by `d` without validation → invalid-curve.
Craft `P'` on a smooth-order fake curve via `ec.py`, recover `d mod m_i`
per submission, CRT.

## Shape 5 — "the biased LSB/MSB"

Service returns `k` masked — e.g. `k & ((1<<64)-1)` leaked, or `k` shares
the top bits. Transform into `(t, u)` pairs → `hnp`/`hnp-ecdsa` with the
correct `--nonce-bound`.

## Shape 6 — "the tiny subgroup"

`g` generates a small subgroup of `Fp*` (e.g. order 100 inside `p` huge).
`bsgs`/`pohlig-hellman` on `ord(g)` — trivial.

## Shape 7 — "the pairing curve"

`#E` has a small embedding degree — MOV/Frey-Rück transfers the ECDLP to
`F_{p^k}` where `pohlig-hellman`/`index-calculus` applies. No pairing tool
here — flag it as an intended path, note in field-notes.

## What every shape shares

The verify `x·G == Q`/`g^x == h` — none of these attacks are real until
the scalar reproduces the public key.
