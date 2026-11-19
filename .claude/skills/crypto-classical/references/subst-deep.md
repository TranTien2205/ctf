# subst deep — the monoalphabetic substitution, annotated

## The transform

`c_i = σ(p_i)` — a bijection `σ` on the 26 letters. Every `E` in `pt` lands on
`σ(E)` — so the *frequency shape* is preserved, just renamed.

## The variants

- **Simple substitution** — any `σ` — the annealing target.
- **Keyword cipher** — `σ` = `KEYWORD + remaining-alphabet-in-order` —
  e.g. `KEYWORD...` then `A,B,C,...` minus the keyword letters.
- **Caesar** — `σ` a cyclic shift — `classical_solve caesar` is faster.
- **Atbash** — `σ` the reflection `25-i`.
- **Affine** — `σ(p) = (a·p+b) mod 26`, `gcd(a,26)=1` — 12·26 = 312 keys,
  brute-forceable.
- **Baconian** — a 5-bit A/B *encoding*, not a substitution.
- **Polybius** — a 5×5 grid, pairs→letters — a *fractionation* cipher.

## The detection — the signal

`cipher_id` on a subst `ct`:
- **IC ~0.066** — a bijection preserves the multiset structure.
- **chi² flat** — no single `k` wins (the mapping isn't a rotation).
- **ETAOIN-shaped freq** — the common `ct` letters are `σ(E),σ(T),σ(A),...`
  in English order. `Z,Q,X` are `σ` of the rares.

## The solve — the annealing

```bash
python3 tools/classical_solve.py subst --text 'CT'                            # the anneal
python3 tools/classical_solve.py subst --text 'CT' --restarts 8 --iters 4000  # harder
```

The anneal: start from a frequency-ordered `σ`, score by tetragram `log p`,
swap two `σ` entries, keep the improvement, restart on a plateau. More
`--restarts`/`--iters` for a harder `ct`.

```python
# manual — anchor σ from the format positions
# if flag{ is at positions 0-4, σ⁻¹(ct[0])='f', σ⁻¹(ct[1])='l', ...
```

## The polish

- **Near-English + wrong flag format** — a partially-right `σ`. The `flag{`
  positions reveal which `σ` entries are wrong — swap them: `gLAG{` → `σ⁻¹(g)` should be `f` not `g`.
- **The keyword** — recoverable from `σ`: read the sorted `σ` order — the
  keyword is `σ` restricted to the alphabet's start.
- **No spaces** — the anneal handles it; word boundary errors are polish.

## The verify

`σ` → `p = σ⁻¹(c)` → language; `σ(p)` reproduces `c`.

## The falsifier

The anneal never reaches language → not a `σ` → transposition (`π`) or a
non-substitution.

## The trap

`σ` applied to a keyed *alphabet* — `KEYWORDABCDEFG...` — reads `σ` directly;
the keyword shows in the recovered `σ` order.
