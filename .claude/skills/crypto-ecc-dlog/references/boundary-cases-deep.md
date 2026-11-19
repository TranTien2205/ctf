# Boundary cases deep — the numeric edges in full

## The signature-count edge

`hnp-ecdsa`/`hnp` at exactly `required_signatures` is the information-theoretic
minimum — add 1–2 extra; below it the lattice is underdetermined.

## The order edge

- `ord(g) = 2q` with `q` large prime — the worst case for both PH and BSGS:
  `q` is the factor PH can't break and `√q` is too big for BSGS. The intended
  bug isn't dlog — look at the protocol.
- `ord(g)` a prime-power `q^e` — PH handles it (e BSGS steps of size `q`).

## The bound edge

`--nonce-bound` exactly at `B = max k_i` works; `B` smaller misses one sig,
`B` larger wastes lattice dimension. `--nonce-bits` rounds to powers of two —
`--nonce-bound` gives the exact `B` when known.

## The `bsgs` memory edge

`max_table = 1 << 22` default — ~4M entries. `bsgs` on `ord > 2^44` exceeds
it; raise `max_table` in code (`dlog.bsgs(g,h,p,order,max_table=1<<24)`) or
accept the ceiling.

## The field-vs-curve edge

`dlog.*` tools are for `Fp*`; `Q = x·P` needs `ec.py` point arithmetic with
the same order logic. A `bsgs` call on a curve shape fails — the tool is
multiplicative-group only.

## The `Δ` near-miss

`Δ ≈ 0` isn't singular — it must be `≡ 0 mod p` exactly. `Δ mod p` non-zero
but small means a valid curve; move on.

## The verify edge

`x·G == Q` on the *supplied* `G`, `Q`, `p`, `a`, `b` — a `d` verifying on a
different curve means you derived on the wrong one.
