# railfence deep — the transposition family, annotated

## The transform

`c = π(p)` — a *permutation* of positions, not of letters. The letter multiset
is exactly preserved; only the order is scrambled.

## The variants

- **Rail-fence** — write the `pt` in a zigzag over `r` rails, read the rows.
- **Columnar** — write in `w` columns, read the columns in key order.
- **Route** — a grid read in a spiral / zigzag / diagonal / boustrophedon.
- **Scytale** — a fixed-width wrap (a `w`-column route with row read).
- **Block permutation** — `pt` in blocks of `b`, each block permuted by `π`.
- **Permutation cipher** — a keyed `π` on positions.

## The detection — the signal

`cipher_id` on a transposition `ct`:
- **IC ~0.05-0.066** — the *letter counts* are unchanged, so the collision
  probability stays English.
- **The freq is exactly English** — the `ct` has English letter counts (E
  common) but the *order* is scrambled — the text reads as random jumbled
  English letters.
- **Composite length** — `n` composite → a grid of `n = r·c` cells.

## The solve

```bash
python3 tools/classical_solve.py railfence --text 'CT'   # the depths ranked
```

```python
# manual — the zigzag decode for depth r
def rail_decode(ct, r):
    pat = [min(i % (2*(r-1)), 2*(r-1) - i % (2*(r-1))) for i in range(len(ct))]
    # count each row, slice ct into row buffers, re-read in pattern order
```

## The polish

- **A columnar** — brute the width `w`; fill row-major, read columns in key
  order. A key word names the column order.
- **A route** — the grid shape `n = r·c`; fill row-major, read the route
  (spiral/zigzag/diagonal).
- **A scytale** — the `w`-width wrap; try `w` from 2.

## The verify

`r`/`w`/`π` → `π⁻¹` → `p` → language; `π(p)` reproduces `c`.

## The falsifier

No depth/width produces language → a different `π` or not a transposition
→ `subst` (a letter-`σ`) or other.

## The trap

- A transposition over a *substituted* text — `π(σ(p))` — the IC is ~0.066
  but the letters aren't English-ordered. Un-scramble first (the `π` is
  position-only), then `subst` the un-scrambled `ct`.
- `L` factors — `n = r·c` — try the divisors as `w`.
