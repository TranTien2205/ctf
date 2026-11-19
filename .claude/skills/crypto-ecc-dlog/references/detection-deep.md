# Detection deep — edge signals and the full decision tree

## The signature-count read

| Signatures available | What it enables |
|---|---|
| 1 signature | nothing — single sig leaks nothing about `d` or `k` |
| 2 signatures, same `r` | `ecdsa-nonce-reuse` — closed form |
| 2+ signatures, distinct `r` | `hnp-ecdsa` only if `k` is biased/short/partial |
| many sigs (≈ 2·order_bits/leaked_bits) | `hnp-ecdsa` lattice — the count formula |
| oracle (sign arbitrary messages) | targeted nonce recovery; also re-sign known `z` for verification |

`hnp.required_signatures(order_bits, nonce_bits)` computes the count —
a 256-bit curve with 128-bit nonces needs ~4 signatures; with 8 leaked bits
needs ~64.

## The message-hash read

- `z` is the hash *reduced to an integer* — `int.from_bytes(H(m), 'big')` then
  `mod n` on most curves. Getting `z` wrong (wrong truncation vs mod) makes
  every downstream attack return garbage that fails the `x·G == Q` check.
- ECDSA truncates `H(m)` to `order` bit-length (FIPS 186-4), not `mod n`
  subtraction. Both exist in the wild — try truncation first.

## The curve-shape read

| Handout shape | Attack |
|---|---|
| `p, a, b` given, `#E == p` | `smart_attack.py` — anomalous curve, linear-time solve |
| discriminant `4a³+27b² ≡ 0 mod p` | `singular_ec.py` — maps to additive/multiplicative group |
| `#E` factors into small primes | `pohlig-hellman` on the curve (same math, point arithmetic) |
| `Q` not on the curve | invalid-curve attack — only if the server skips validation |
| two curves with same `b`, different `a` | twist attack — check security of both |

## The oracle-shape read

- **Sign-and-return** — you control `m`, get `(r, s)`. Feed the same `m`
  twice: deterministic `k` (RFC 6979) gives identical `(r, s)`; random `k`
  differs. Identical output + a second message → `ecdsa-nonce-reuse` when `r`
  repeats across *different* messages.
- **Sign-with-timestamp-k** — `k` derived from a timestamp or counter →
  `hnp-ecdsa` with `--nonce-bound` covering the timestamp range.
- **Leaked `k` bits in response** — direct `hnp`.

## The non-cases (route out)

- `RSA` modulus → `crypto-rsa` skill.
- `AES`/`XOR`/stream → `crypto-symmetric-oracle`.
- `mt19937`/`lcg`/`lfsr` → `crypto-prng`.
- base64/hex blob → `misc-encoding-carrier`.

## The verify read

Whatever the route, the answer is a scalar `x`. Verify `x·G == Q` (or
`g^x == h`) before recording — every module ends here.
