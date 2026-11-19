# `hnp` — the raw Hidden Number Problem lattice

## When it applies

The generic form underneath `hnp-ecdsa`: you hold pairs `(t_i, u_i)` where
each `k_i = t_i·d - u_i mod n` is bounded `0 ≤ k_i < B`. Reach for it when
`hnp-ecdsa`'s `(r, s, z)` tuple isn't what you have — e.g. leaked `k` bits
arriving pre-arranged as `(t, u)` pairs.

## The command

```bash
python3 tools/crypto_attack.py hnp --t t.json --u u.json --modulus n --bound B
```

`t.json`, `u.json` — JSON lists of integers (parallel arrays, same length).

In code:

```python
from tools.crypto import hnp
d = hnp.hnp_solve(t_list, u_list, modulus, bound)
n_sigs = hnp.required_signatures(order_bits=256, nonce_bits=8)
```

## The math

Build the `m+1`-dim lattice spanned by rows `(n,0,…,0)`, `(0,n,…,0)`, …,
`(t_1, t_2, …, B/n)`. LLL reduction finds the vector `(k_1,…,k_m,B·d/n)` —
short because every `k_i < B` — reading `d` off the last coordinate.

## The derivation from ECDSA

`s = k⁻¹(z + d·r)` → `k = s⁻¹z + s⁻¹r·d mod n` → `k = t·d - u mod n` with
`t = s⁻¹r`, `u = -s⁻¹z`. `hnp-ecdsa` does this transform for you; use raw
`hnp` when your source already gives `(t, u)` or you transform by hand.

## Preconditions

- At least ~`2·order_bits/log2(n/B)` signatures — `required_signatures`
  computes it exactly.
- `B` covers every `k_i` — one outlier poisons the solve.

## Falsifier

No `d` satisfying `d·G == Q` → too few signatures, wrong `B`, or an
outlier `k` (retry with a pruned set).

## Common mistakes

- Transposing `t`/`u` — `t = s⁻¹r mod n`, `u = -s⁻¹z mod n`.
- `B` as bit-count vs bound — `--bound` is the integer bound `B`, not bits.
- Dedupe first — a repeated `r` is the reuse case, not HNP.
