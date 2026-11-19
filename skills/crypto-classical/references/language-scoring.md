# Language scoring — the `subst` objective deep

## The n-gram model

`score(σ) = Σ_i log p_4(pt[i:i+4])` — the sum of log-probabilities of the
4-grams. A real `pt` scores high; a wrong `σ` scores low.

## The anneal

1. `σ` initialized by frequency (`σ(ct_top)=E`, `σ(ct_2nd)=T`, ...).
2. Score the current `σ`-decode.
3. Swap two `σ` entries; re-score.
4. Keep the improvement (hill-climb); occasional random restart.
5. `--restarts N` / `--iters N` — more restarts/iterations for a harder `σ`.

## The near-decode

`gLAG{...}` — a partially-right `σ`. The `flag{` positions reveal the wrong
entries — `σ⁻¹(g)` should be `f`. Swap and re-score.

## The short-ct problem

Under ~100 chars the tetragram model is weak — the `flag{`/`CTF{` positions
carry the solve, or a crib.

## The keyed-alphabet read

A `σ` recovered reads `σ = KEYWORDABCDEFG...` — the keyword in the `σ` order.

## The falsifier

The anneal's score plateaus below language — not a `σ` → `π`/other.
