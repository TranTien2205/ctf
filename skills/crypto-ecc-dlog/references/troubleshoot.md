# Troubleshoot — when the attack doesn't return a key

## `ecdsa-nonce-reuse` returns garbage

- `r` wasn't actually equal → byte-compare the two `r` fields.
- `z` wrong → recompute with FIPS truncation then `mod n` variants.
- `--order` wrong → use published `n` for named curves; verify `n·G = ∞`.

## `hnp-ecdsa` finds no `d`

- **Too few sigs** — `hnp.required_signatures(order_bits, nonce_bits)`;
  gather more from the oracle.
- **`--nonce-bound` too tight** — the real `k` exceeds `B`; widen it.
- **An `r` repeats** — you have a reuse pair; split it out to
  `ecdsa-nonce-reuse`.
- **Nonces weren't biased** — the handout's hint was wrong; verify by
  checking if a recovered `d` (even wrong) is consistent across sigs.

## `pohlig-hellman` stalls

- Largest factor of `ord(g)` too big → not this attack; check for defect
  curves (smart/singular/invalid) or a protocol flaw.
- `ord(g)` wrong → re-derive from `p-1` factorization or the subgroup the
  challenge names.

## `bsgs` finds no match

- `x` outside the supplied bound/order → enlarge or re-check `ord(g)`.
- `h ∉ <g>` → `pow(h, order, p) == 1` check.

## `smart_attack` fails

- `#E ≠ p` → not anomalous; `smoothness --n #E` for PH.
- Points on a different curve → re-check `p, a, b`.

## `singular_ec` fails

- `Δ ≠ 0 mod p` → not singular.
- Node vs cusp confusion → check whether the singular point's tangent is
  defined over `Fp` (split node → multiplicative) or not.

## `crypto_attack.py` errors

- `supply --sigs FILE.json` → the `--sigs` arg is a *file*, not inline JSON.
- `need(data, "order")` → `--order` missing.
- JSON parse errors → `--sigs` wants `[r,s,z]` triples or `{"r","s","z"}`.
