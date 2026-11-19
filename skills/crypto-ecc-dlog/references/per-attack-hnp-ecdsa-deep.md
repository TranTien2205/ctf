# Per-attack `hnp-ecdsa` deep — the card, expanded

## The trigger

All `r`s distinct AND `k_i` bounded/biased (`k_i < B`), AND enough sigs.

## The command

```bash
python3 tools/crypto_attack.py hnp-ecdsa --sigs sigs.json --order <n> \
  --nonce-bits <bits>          # k_i < 2^bits
# or
python3 tools/crypto_attack.py hnp-ecdsa --sigs sigs.json --order <n> \
  --nonce-bound <B>            # k_i < B
```

## The count heuristic

`required_signatures ≈ 2·order_bits/leaked_bits` —
`order_bits = log2(n)`, `leaked_bits = log2(n/B)`. Below it, the lattice
returns junk; far above it, `lll.py` crawls.

## The lattice

`k_i ≡ t_i·d + u_i (mod n)`, `t_i = s_i⁻¹r_i`, `u_i = -s_i⁻¹z_i`. `d` is
the hidden number; `lll.py` finds the short vector.

## The verification

`d·G == Q`. A plausible `d` that fails is NOT the key — the lattice solved
a different/wrong HNP.

## The falsifiers

- `d·G ≠ Q` at required count → `z`/`order`/`B` wrong or outlier.
- `k` not all `< B` → prune the outlier.

## The boundary

- `B` too tight → misses `k`s; too loose → lattice won't converge.
- pure-python `lll.py` bounds `m` — keep it near `required`.
