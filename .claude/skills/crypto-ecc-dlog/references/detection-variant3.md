# Detection variant 3 — the reads by what the handout lacks

## Missing `n` (order)

- Named curve → published `n` applies.
- Custom curve → count `#E` (small `p`) or read the intent — defect shapes
  dominate when `n` is withheld.
- `h = g^x` with no `ord` → `ord(g)` = `p-1` for a generator; compute.

## Missing `z`

- Message present → `z = int(H(m))` truncated.
- `z` absent but `r`,`s` given → `z` is the hash — recompute.

## Missing `Q`

- Only `d`/`x` to recover — no `Q` to verify against → the flag is the
  proof instead; `x` decrypts or `d` signs.

## Missing sigs

- Oracle → collect them.
- Params-only → defect/dlog family, not nonce.

## Missing a discriminator

- `r` equal + `k` bounded — prefer `ecdsa-nonce-reuse` (cheaper).
- `ord` smooth + `x` bounded — `pohlig-hellman` usually wins on smooth.

## Missing a fail-safe

- `bsgs` no match → `h ∈ <g>` check before `B` bump.
- `hnp` no `d` → `z` recompute before `B` bump.
- `pohlig` stalls → `smoothness` was skipped or `ord` wrong.
