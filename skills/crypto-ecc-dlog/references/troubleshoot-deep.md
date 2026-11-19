# Troubleshoot deep — the second-order failures

## The `z`-convention loop

`d` recovers but verify fails → wrong `z`. The two conventions:

```python
z = int.from_bytes(hashlib.sha256(msg).digest(), 'big')          # FIPS: truncate to order_bits
z = int(hashlib.sha256(msg).hexdigest(), 16) % n                  # mod n
```

Try the other. A third exists — raw message int — rarely.

## The lattice-empty problem

`hnp-ecdsa` returns nothing / wrong `d`:

1. Re-count: `hnp.required_signatures(order_bits, nonce_bits)` — do you have
   enough? The estimate is optimistic; add ~2 more.
2. Re-bound: is `B` covering every `k`? One outlier kills the solve — prune
   sigs where `k` might exceed `B`.
3. Re-check `z` — one bad `z` entry poisons the whole lattice.
4. Try `--nonce-bound` (integer `B`) vs `--nonce-bits` — same thing but
   easier to get right.

## The `order` problem

- `--order` = `n` always. A `p`-sized `n` breaks every attack silently.
- On a custom curve without a given `n`: count `#E` (small `p`) or assume
  the challenge intends defect-curve, not generic dlog.

## The `--sigs` format problem

- `supply --sigs FILE.json` — the arg is a *file path*, not inline JSON.
- Entries must be `[r,s,z]` triples or `{"r","s","z"}` — a `{"r","s","h"}`
  or missing `z` fails with a parse error.
- Hex strings `"0x..."` and ints both work — mixing is fine.

## The "no attack fits" problem

Re-read the handout for: the protocol-level bug (not crypto), the encoding
misread (`misc-encoding-carrier`), or a different crypto class (RSA/PRNG/
symmetric). `crypto-triage` re-routes.
