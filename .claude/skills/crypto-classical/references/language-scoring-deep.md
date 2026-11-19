# Language scoring deep — the `subst` objective, annotated

## The n-gram model

`score(σ) = Σ_i log p_4(pt[i:i+4])` — the sum of log-probabilities of the
4-grams under a precomputed English tetragram table. A real `pt` scores high;
a wrong `σ` scores low.

## The anneal — hill-climb the `σ`

1. **Init** — `σ` by frequency: `σ(ct_top)=E`, `σ(ct_2nd)=T`, ...
2. **Score** — the current `σ`-decode's tetragram sum.
3. **Swap** — two `σ` entries; re-score.
4. **Keep** — the improvement; occasional random restart.
5. **`--restarts N` / `--iters N`** — more restarts/iterations for a harder
   `σ` or a short `ct`.

## The near-decode — `gLAG{...}`

A partially-right `σ`. The `flag{`/`CTF{` positions reveal the wrong `σ`
entries — `σ⁻¹(g)` should be `f`. Swap `σ(g)↔σ(f)` and re-score — the anneal
often finishes it.

## The short-ct problem

Under ~100 chars the tetragram model is weak — the `flag{`/`CTF{` positions
carry the solve, or a crib — `known-plaintext.md`.

## The keyed-alphabet read

A `σ` recovered reads `σ = KEYWORDABCDEFGHIJLMNPQRSTUVWXYZ` — the keyword is
`σ` restricted to the alphabet's start.

## The falsifier

The anneal's score plateaus below language — not a `σ` → `π`/other.
