# Per-attack `bsgs` deep — the card, expanded

## The trigger

`h = g^x mod p` with `x < B` bounded, OR `ord(g)` ≤ ~2⁴⁴.

## The command

```bash
python3 tools/crypto_attack.py bsgs --g <g> --h <h> --p <p> --order <B-or-ord>
```

`--order` is the bound on `x` — when `x < B`, pass `B`; when `x < ord`,
pass `ord(g)`.

## The mechanism

`x = i·m + j`, `m = ⌈√N⌉` for `N` the bound/order; baby steps `g^j` vs
giant steps `h·g^(-i·m)` collide at `x`.

## The verification

`pow(g, x, p) == h`.

## The falsifiers

- No collision → `h ∉ <g>` or `x` beyond the bound.
- `N` > 2⁴⁴ → out of reach.

## The boundary

- `√(2⁴⁴) ≈ 2²²` baby steps — the practical RAM/time wall.
- `h ∉ <g>` → solve for `x` in the right subgroup or the statement is
  malformed.
- `x` exactly at the bound edge → off-by-one; bump `N` by 1.

## The curve variant

`x < B` on `E` → same collision with `E.mul` instead of `pow`.
