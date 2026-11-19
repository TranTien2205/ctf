# Symmetric-oracle workflow — the ordered path

The class is defined by one question: which oracle do you hold? Everything
else is mechanical once that is named.

## Phase 1 — shape (2-3 requests)

1. Determinism: submit identical input twice. Same output → ECB or fixed-IV.
   Different → per-request nonce/IV.
2. Length: grow input one byte at a time. Block-step growth → block cipher.
   1:1 growth → stream/CTR.
3. Structure: repeated plaintext → repeated blocks = ECB fingerprint.

## Phase 2 — the oracle kind

| Observation | Oracle | Next file |
|---|---|---|
| Identical blocks for identical input | ECB encrypt | `ecb-detection.md` |
| Pad-corrupt vs MAC-corrupt differ | CBC padding oracle | `cbc-padding-oracle.md` |
| Two ciphertexts, same nonce | stream/CTR reuse | `ctr-nonce-reuse.md` |
| `hash(secret||m)` construction | prefix MAC | `length-extension.md` |
| Tag checked before decrypt | authenticated | `authenticated-boundary.md` |

## Phase 3 — the primitive

Run the matched attack. Every loop has three invariants: the distinguisher is
measured first, each byte is confirmed by exact match, and the loop stops at
the measured boundary.

## Phase 4 — evidence

- `post-probe --verdict confirms` on the distinguishing answer (pad vs MAC
  response, ECB block match, tag accept).
- `pre-flag --value` only when the flag bytes are read from a live response.

## Where the loop stops

- Class falsifier fires (authenticated before decrypt) → record the negative,
  hand back to the router.
- Request budget exhausts before the byte loop finishes → escalate to
  `fanout_sweep` or `solver_handoff`, not a sixth variant.
