# Subst variants — the `σ` family, annotated

## The family

`c = σ(p)` — a bijection on {A..Z}. The multiset structure is preserved —
`σ(E)` is the top `ct` letter — so IC ~0.066 and the freq *shape* is ETAOIN.
The chi² is flat — no `k` fits a non-rotation.

## The variants

### Simple substitution — any `σ`

`classical_solve subst --text` — the tetragram anneal.

### Keyword cipher — `σ = KEYWORD + rest`

`σ = KEYWORDABCDEFGHIJLMNPQRSTUVWXYZ` — the `σ` order reveals the keyword.

### Caesar — `σ` a cyclic shift

`σ(i) = (i+k) mod 26` — a special `σ`; `caesar` (25 `k`) beats the anneal.

### Atbash — `σ` the reflection

`σ(i) = 25-i` — `atbash --text`; the reversed ETAOIN.

### Affine — `σ(p) = (a·p+b) mod 26`

`gcd(a,26)=1` — 12·26=312 keys — brute-forceable; a linear `σ`.

### Baconian — the A/B code

5-bit A/B groups — an *encoding*, not a `σ` — `enc_detect` may catch it.

### Polybius — a 5×5 grid

(row,col) pairs → letters — a fractionation cipher — pairs not letters.

## The detection — the chi² flat + ETAOIN shape

`cipher_id` — IC~0.066, chi² flat, the `ct` frequency ranked ETAOIN-shaped —
`σ(E)` top, `σ(T)` next.

## The solve — the anneal

`subst --text [--restarts --iters]` — tetragram `Σ log p(quad)` hill-climb.

## The polish — the `flag{` anchor

`gLAG{...}` — the `flag{` positions reveal wrong `σ` entries — `σ⁻¹(g)=f` —
swap.

## The verify

`σ⁻¹(c)=p` language; `σ(p)=c`.

## The falsifier

The anneal never reaches language → `π` (transposition) or non-substitution.
