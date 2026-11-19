# subst catalogue — the monoalphabetic substitution, every variant

## The family

`c = σ(p)` — a bijection on 26 letters.

## The variants

- **Simple substitution** — any `σ` — the annealing target.
- **Keyword cipher** — `σ` = `KEYWORD` + the remaining alphabet.
- **Atbash** — `σ` = the reflection.
- **Caesar** — `σ` = a shift — a special `σ`.
- **Affine** — `σ(p) = (a·p+b) mod 26`.
- **Baconian** — a 5-bit substitution, not a letter bijection.
- **Polybius** — a 5×5 grid, pairs → letters.

## The detection

- IC ~0.066 — monoalphabetic.
- Flat chi² — no `k` wins.
- ETAOIN-shaped freq — σ(ETAOIN) are the common `ct` letters.

## The solve

```bash
classical_solve subst --text 'CT'                           # annealing
classical_solve subst --text 'CT' --restarts 8 --iters 4000 # harder
```

```python
# manual — the format positions pin σ
# σ('FLAG{') → the ct letters at those positions
```

## The polish

- Near-English + wrong flag format → a partially-wrong `σ` → swap the entries
  the `flag{`/`CTF{` positions reveal.
- The key word — recoverable from `σ` (the alphabet order).

## The verify

`σ` → `p = σ⁻¹(c)` → language; `σ(p)` reproduces `c`.

## The falsifier

The anneal never reaches language → not a substitution → transposition/other.
