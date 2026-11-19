# Boundary cases variant — the limits, restated

## The lattice bound

`required_signatures ≈ 2·order_bits/leaked_bits` — `m` below it and `lll.py`
returns junk. `m` far above it and the pure-python LLL crawls.

## The dlog bound

`bsgs`/`PH` both die when the *effective* order is too big:
- `bsgs` — `ord`/`B` > 2⁴⁴.
- `pohlig-hellman` — largest factor > 2⁴⁰.
- safe-prime `ord = 2q` → neither works.

## The defect bound

- `#E == p` must be exact — `#E ≈ p` is not anomalous.
- `Δ == 0` exact — near-zero is a normal curve.
- invalid curve needs *no* validation — a single `y² ≡ x³+ax+b` check kills it.

## The reuse bound

- `r` must match exactly — close is a different `k`.
- RFC 6979 deterministic `k` — same `m` always same `r`; different `m` never
  collides.

## The `--order` bound

`n`, not `p`. `n | #E`, `n` is `ord(G)`. Passing `p` where `n` is wanted
breaks every nonce/lattice attack.
