# Nonce family — everything that leaks `k`

## The three nonce attacks

| Shape | Attack | Command |
|---|---|---|
| `r` repeated | `ecdsa-nonce-reuse` | `--sigs sigs.json --order n` |
| `k < B` bounded | `hnp-ecdsa` | `--sigs … --nonce-bits B` |
| `(t,u)` pairs leaked | `hnp` | `--t t.json --u u.json --modulus n --bound B` |

## The shared math

`s = k⁻¹(z + d·r)` — every attack recovers `d` by first recovering `k` or
directly from the `k_i = t_i·d - u_i mod n` system.

## The sigs file

`--sigs` is a **file**, not inline JSON:

```json
[{"r": 1, "s": 2, "z": 3}, {"r": 1, "s": 4, "z": 5}]
```

`[r,s,z]` triples or `{"r","s","z"}` objects; hex or int.

## The signature count

`hnp.required_signatures(order_bits, nonce_bits)`:

| leak | sigs needed |
|---|---|
| `k` fully known | 1 (direct) |
| `k` 128-bit on 256-bit curve | ~4 |
| `k` 8-bit leak | ~64 |

## The boundary

One signature, no bound → nothing to do. `r` equal → reuse, not lattice.
