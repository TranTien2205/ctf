# Detection variant 2 — the reads by artifact shape

## The `sigs.json` shape

- `<2` entries → nonce attacks dead.
- `r` dup → `ecdsa-nonce-reuse`.
- distinct `r` + bounded `k` → `hnp-ecdsa`.
- partial `k` → `hnp`.

## The `params.json` shape

- `p a b` + `Q`/`G` → defect ladder (`Δ` → `#E` → smoothness).
- `p g h` only → field dlog (`smoothness` → PH/BSGS).
- `n`/`ord` absent → count/compute or defect intent.

## The `service` shape

- `sign(m)` — nonce family; probe determinism first.
- `multiply(P)`/`dh(P)` — invalid curve; probe validation first.
- `verify` only — no oracle surface; pure-math shape.

## The `jwt` shape

Two JWS tokens with ES256 — `r||s` in signature part. Same `r` →
`ecdsa-nonce-reuse` → `d` → forge admin → flag.

## The `ct`-only shape

A ciphertext blob with no params → probably not this class — encoding
(`misc-encoding-carrier`) or symmetric (`crypto-symmetric-oracle`).

## The protocol shape

A full protocol description (DH exchange, handshake) → the bug is usually
in the *use* (small `x`, shared `k`, unvalidated point) not the math —
`bsgs`/`pohlig`/`invalid-curve` accordingly.
