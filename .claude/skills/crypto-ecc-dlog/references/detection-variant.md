# Detection variant — the read by input type

## The `sigs.json` input

The most common input. Parse order:

1. Load JSON, normalize entries to `{"r","s","z"}` ints.
2. Count entries — `<2` → dead on nonce alone.
3. Dedupe `r` → `ecdsa-nonce-reuse` on the pair.
4. All distinct → `hnp-ecdsa` if `k` bounded.
5. Check `z` derivation on one entry (`sha256(msg)` truncated).

## The params input

`{"p","a","b","G_x","G_y","Q_x","Q_y","n"}`:

1. `Δ = -16(4a³+27b²) mod p` → `0` → `singular_ec`.
2. `#E` (given or counted) → `== p` → `smart_attack`.
3. `smoothness --n #E` → `pohlig-hellman`.
4. Else → `bsgs` if `n` small, else defect-of-protocol.

## The service input

`POST /sign {message}`:

1. Same `m` twice → same `(r,s)`? → deterministic `k` (RFC 6979) → reuse
   only possible across different `m`.
2. Different `m` → distinct `r` → `k` random or biased → `hnp-ecdsa` if bounded.
3. Leak: does the response carry `k`, `k&mask`, timestamp? → `hnp`.

## The oracle input

`POST /multiply {x, y}` or DH key agreement:

- Submit a point not on `E` — if accepted → invalid-curve attack.
- If rejected with validation error → the bug isn't here.

## The statement input

`h = g^x mod p`:

- `smoothness --n (p-1)` → `pohlig-hellman`.
- `x` bounded → `bsgs`.
- `p-1 = 2q` → look elsewhere (the intended bug isn't dlog).
