# ECC and discrete-log: the given decides the attack

Like RSA, the challenge tells you which break applies — the work is reading
the parameters before reaching for math.

## The parameter questions, in order

1. **Is the curve standard?** `secp256k1`, `P-256`, `Curve25519` — safe
   curves; the bug is elsewhere (nonce, implementation, misuse).
2. **Is the order smooth?** `factor(order)` — if it's all small primes,
   Pohlig-Hellman solves the dlog in minutes (sage `discrete_log`).
3. **Is the embedding degree low?** anomalous/pairing-friendly curves let the
   MOV or FR attack move the dlog to a finite field.
4. **Is the nonce weak?** reused `k` across two signatures gives the private
   key directly — no dlog needed.

## The nonce breaks — most common CTF answer

ECDSA `s = k^{-1}(z + r·d) mod n`. Two signatures with the same `k`
(same `r`):

```python
k  = (z1 - z2) * inverse(s1 - s2, n) % n
d  = (s1*k - z1) * inverse(r, n) % n
```

Partial nonce leakage (MSB/LSB known) → Hidden Number Problem → lattice,
`sage`/`fpylll`.

## The dlog rows

| Given | Attack |
|---|---|
| smooth order | Pohlig-Hellman — `discrete_log` in sage |
| anomalous curve (`#E(Fp) = p`) | Smart's attack — linear time |
| low embedding degree | MOV/FR reduction to finite-field dlog |
| small secret range | baby-step giant-step / Pollard-rho |
| related public keys on a shared curve | invalid-curve attack — points on the wrong curve leak `d mod small_subgroup` |

## Working it

```python
# sage
E = EllipticCurve(GF(p), [a, b])
G, P = E(gx, gy), E(px, py)
n = E.order()
print(factor(n))                 # smooth -> Pohlig-Hellman
d = discrete_log(P, G, ord=n)    # sage handles the small-order case
```

## Falsifier

The curve is standard, order is prime, nonce is fresh per signature and
unleaked, and the implementation is `ecdsa`/libsodium — the ECC itself is
sound; the bug is in the *protocol built on it* (key reuse, missing
validation, bad serialization).

## Traps

- A "custom" curve almost always means a weak one — factor its order first,
  before assuming the hard case.
- Same `r` in two signatures = same `k` = private key recovered in four
  lines; check for it before any lattice work.
- `secp256k1` nonces biased by a bad RNG (PlayStation 3, Android wallet
  incidents) are the classic real-world version of the same bug.
- The public key can be a *point on a different curve* — check `P in E`
  before any math, or the input may already be the attack vector.
