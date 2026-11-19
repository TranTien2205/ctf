# Invalid-curve attack — server skips point validation

## When it applies

A service computes `d·P` for a caller-supplied point `P` on a named curve
but does **not** check that `P` lies on the curve. The submitted point lives
on a *different* curve `E'` (same `a` or `b` tweaked), where `ord(P)` is
small or smooth — you solve a small dlog to get `d mod ord(P)`, then CRT
across several fake curves.

## Detection

1. A service/endpoint accepts a point `(x, y)` or a public key to multiply.
2. The server never validates `y² == x³ + ax + b mod p` — the bug the whole
   attack needs. If it validates → dead end, this route is closed.

## The procedure

1. Pick a fake curve `E'` sharing the `b` (or `a`) coefficient — the server
   computes `d·P'` thinking it's on `E` but `P' ∈ E'`.
2. Choose `P'` with small order `m` (factor `#E'` first with `smoothness`).
3. Submit `P'`; the response reveals `d·P'`, giving `d mod m` via a tiny
   `bsgs`/`pohlig-hellman`.
4. Repeat with several `E'_i` covering `Π m_i ≥ n` → CRT recovers `d`.

## Tools

`tools/crypto/ec.py` does point arithmetic on custom `(p, a, b)` —
use it to compute fake-curve orders and test your `P'` before sending.
`crypto_attack.py bsgs --g --h --p --order` covers the small dlog on the
*multiplicative* model — for curve subgroups use `dlog.bsgs` logic with
`ec.py` point ops.

## Falsifier

- Server rejects the point with a validation error → attack impossible.
- `d` recovered via CRT doesn't satisfy `d·G == Q` → wrong curve arithmetic
  or an `ord(P)` miscount.

## Common mistakes

- Submitting the singular point — it has no defined group order.
- Choosing `E'` with smooth *but tiny* order — gives few CRT bits; need
  enough `m_i` to cover `n`.
- Assuming this works on `secp256k1` signing APIs — signatures don't take
  attacker points; this is for DH/key-agreement oracles.
