# Edge cases deep — the boundary shapes in full

## The `s` / `n-s` duality

ECDSA accepts `s` and `n-s` — both verify. If the handout gives the "other"
`s`, the attack still works; the recovered `d` is the same. Verify catches
a genuine mismatch.

## The compressed-key boundary

`Q` may arrive as `02||x` or `03||x` (compressed) — decompress via
`ec.py`/`y² = x³+ax+b mod p` square root before using `x·G == Q` verify.

## The deterministic-k oracle

`sign(m)` twice on the same `m`: identical `(r,s)` → RFC 6979 deterministic
`k` → reuse impossible on same `m`; you'd need `r` to repeat across
*different* `m` (still possible if `k` derives only from `d`).

## The partial-`k` shapes

- **MSB known** — `k = known_high·2^L + k_low`, `k_low < 2^L` → `hnp` with
  `B = 2^L`.
- **LSB known** — `k = k_high·2^L + known_low` → same `B` on `k_high`.
- **`k` = timestamp** — `B` = timestamp range (e.g. 2³² seconds).

## The subgroup boundary

`h` may not be in `<g>` — `pow(h, ord(g), p) == 1` checks it. If not, find
`ord(h)` and solve in `<h>`'s subgroup — a wrong coset representative is
the classic PH trap the tool already guards.

## The multi-curve boundary

Two curves in one handout (`E` and a twist `E'`) — solve on the weaker,
transfer `d` if the protocol reuses it. Check `ord` on both.
