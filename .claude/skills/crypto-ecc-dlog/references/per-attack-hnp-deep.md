# Per-attack `hnp` deep — the card, expanded

## The trigger

A leak giving `(t_i, u_i)` pairs — MSB/LSB partial nonces, or any
`k_i ≡ t_i·d + u_i (mod n)` shape with `k_i < B`.

## The command

```bash
python3 tools/crypto_attack.py hnp --t t.json --u u.json --modulus <n> --bound <B>
```

`--t`/`--u` take JSON files of ints; `--modulus` is `n`; `--bound` is `B`.

## From sigs to `(t,u)`

```python
t = (pow(s, -1, n) * r) % n
u = (-pow(s, -1, n) * z) % n
```

The transformation is per-signature — a `z` mistake propagates to `u`.

## The lattice

`lll.py` on the `(t,u)` relations — the short vector carries `d`. Same
`required_signatures` heuristic as `hnp-ecdsa`.

## The verification

`d·G == Q`.

## The falsifiers

- `d·G ≠ Q` → `t`/`u`/`B`/`ord` wrong.
- a `k_i ≥ B` in the set → the lattice is poisoned.

## The boundary

- `len(t) == len(u)` — misaligned files parse-fail.
- `B` on the UNKNOWN part — `B` on `k` when the leak is on `k`'s bits.
