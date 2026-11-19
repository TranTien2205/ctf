# Evasion variant — the disguises restated

## The `r`-in-disguise

- `r` formatted differently per entry (hex vs int, leading zeros) — normalize
  before dedupe; `"0xAB"` and `171` are the same `r`.
- `r` compressed/truncated — the visible `r` may be `r mod q` — compare in
  the same field.

## The bound-in-disguise

- `k` not stated but *observed* — `k_i` from oracle responses reveal `B`.
- `k = f(timestamp)` — `B` is a timestamp range, not a bit count.
- `k` = `PRNG` — the bug is `crypto-prng`, not a nonce bound.

## The order-in-disguise

- `ord(g)` hidden inside `p-1` — `g` in a small subgroup → `ord(g)`, not `p-1`.
- `#E` hidden — count or defect intent.

## The defect-in-disguise

- `b = 0` or `a = 0` curve — still singular-checkable.
- `Q`/`G` compressed — decompress before `Δ`/`#E` checks.
- `E'` disguised as `E` — the fake-curve params differ only in `b`.

## The verify-in-disguise

- `d` verifying on the *wrong* curve — check which `G`/`p`/`a`/`b` the
  supplied `Q` uses.
- `flag{` embedded in the scalar — format it, don't just log the int.
