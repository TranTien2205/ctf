# Boundary cases — where the attack stops being the attack

## The nonce boundary

- **Same `r`** → `ecdsa-nonce-reuse` (closed form). **Distinct `r`, biased `k`** → `hnp-ecdsa`. **Random `k`** → nothing works on signatures alone.
- One signature is never enough — ECDSA leaks nothing with one sample.
- `--nonce-bits` bound must *cover* the real `k`; one bit short and the lattice misses.

## The order boundary

- `bsgs` ceiling ~2⁴⁴; `pohlig-hellman` bound is the largest *factor* of `ord(g)`, not `ord(g)` itself.
- `p-1 = 2q` (safe prime) → PH useless, BSGS too big → look for a protocol-level flaw instead.

## The curve boundary

- `#E == p` → smart_attack; `#E` prime or near-p → generic-hard.
- `Δ == 0` → singular_ec; near-zero `Δ` is fine, must be *exactly* `0 mod p`.
- Invalid-curve needs a server that skips validation — a pure-math handout
  has no such oracle.

## The `z` boundary

`z` must be the hash as *integer* in the same convention the signer used —
FIPS truncation to `order_bits`, else `mod n`. Wrong `z` → wrong `d` that
fails verify. Try both conventions before declaring the attack dead.

## The group boundary

- `Q = x·G` on curves uses `ec.py` arithmetic; `h = g^x mod p` uses `dlog.py`.
- A `Q` not on the claimed curve → invalid-curve shape or wrong params.

## The verify boundary

`x·G == Q`/`g^x == h` is the only finish line. A scalar that doesn't
reproduce the public key is not the key.
