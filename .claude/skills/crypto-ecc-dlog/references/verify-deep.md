# Verify deep — the check per attack, with the exact code

## `ecdsa-nonce-reuse` / `hnp-ecdsa` / `hnp` — `d·G == Q`

```python
from tools.crypto import ec
E = ec.curve("secp256k1")   # or {"p":..,"a":..,"b":..}
G = E.point(gx, gy)
Q = E.point(qx, qy)
assert E.mul(G, d) == Q
```

`--curve`/`--pubkey` on `hnp-ecdsa` runs this inside the tool.

## `pohlig-hellman` / `bsgs` — `g^x == h`

```python
assert pow(g, x, p) == h
```

`pow` is enough — no curve ops needed for field dlog.

## `smart_attack` / `singular_ec` — `x·P == Q`

```python
assert E.mul(P, x) == Q
```

Same point-mul verify, on the supplied `(P, Q, p, a, b)`.

## Invalid curve — `d·G == Q`

```python
assert E.mul(G, d) == Q
```

On the *real* curve — a `d` verifying on `E'` was derived on `E'`.

## The flag check

```python
re.search(rb'flag\{[^}]*\}|CTF\{[^}]*\}', decrypted)
```

## The `h ∈ <g>` precheck

```python
pow(h, ord(g), p) == 1
```

Confirms `h` is reachable before solving.
