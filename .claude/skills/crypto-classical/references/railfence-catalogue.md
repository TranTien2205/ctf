# railfence catalogue — the transposition family, every variant

## The family

`c = π(p)` — a permutation, the letters preserved.

## The variants

- **Rail-fence** — the zigzag, `r` rails.
- **Columnar** — `w` columns read in key order.
- **Route** — a grid read in a spiral/zigzag/diagonal.
- **Scytale** — a fixed-width wrap.
- **Permutation** — a block permutation with a key.

## The detection

- IC ~0.05-0.066 — language-frequency letters.
- The text *scrambled* — right letters, wrong order.
- Composite length → a grid.

## The solve

```bash
classical_solve railfence --text 'CT'   # the depths ranked
```

```python
# manual — the zigzag
def rail_decode(ct, r):
    pat = [min(i%(2*(r-1)), 2*(r-1)-i%(2*(r-1))) for i in range(len(ct))]
    # slice ct per row, re-read in pattern order
```

## The polish

- A columnar — brute `w`; the key word if named.
- A route — the grid shape; fill row-major, read the route.

## The verify

`r`/`w` → `π⁻¹` → `p` → language; `π(p)` reproduces `c`.

## The falsifier

No depth/width produces language → a different `π` or not a transposition.
