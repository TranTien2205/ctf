# Theory deep 2 — the working facts, expanded

## The families, restated

1. **Shift** — `c=p+k` — IC~0.066, one chi² min. Caesar/ROT/Atbash.
2. **Substitution** — `c=σ(p)` — IC~0.066, flat chi², ETAOIN-shaped freq.
3. **Polyalphabetic** — `c_i=p_i+k_{i mod L}` — IC~0.038, Kasiski `L`.
4. **Transposition** — `c=π(p)` — letters preserved, order scrambled.
5. **Encoding** — a structured alphabet, no key — `enc_detect`.

## The statistics — the math

### IC — the collision probability

`IC = Σ_i n_i(n_i-1) / N(N-1)` — the probability two random letters match.

- **English** ≈ 0.066 — the `E`,`T`,`A` spikes raise it.
- **Uniform** ≈ 0.038 — all letters equal.
- **A `σ`** preserves it — the multiset is renamed, not changed.
- **A `π`** preserves it — the multiset is *identical*.
- **A `L`-alphabet mix** drops it toward 0.038 — each position a `L`-mix.

### chi² — the shift fit

`chi²(k) = Σ_i (o_i - e_{i+k})² / e_{i+k}` over the 26 letters — the `ct`
shifted by `k` fit against English `e`. A Caesar's `ct` has **one deep
minimum** at `k` — the un-rotation. A `subst`'s is flat — no `k` fits a
non-rotation.

### Kasiski — the period

A repeated n-gram at gap `g` → `g` a multiple of `L`. `gcd` the gaps → `L`.
The coset-IC complements it — the `L` that makes each coset's IC ~0.066.

### Tetragram — the `σ` objective

`score(σ) = Σ log p_4(quad)` — the anneal swaps `σ` entries, keeps the
improvement, restarts on a plateau.

## The facts — the lemmas

- **Caesar ⊂ substitution** — a shift is a `σ`.
- **`L` is the key *length*** — Kasiski/IC estimate it; `L` Caesars find it.
- **`flag{`/`CTF{` leaks the transform** — the format pins `σ`/`k`/`key`.
- **A near-decode is a candidate** — `gLAG{` — polish the wrong `σ` entries.
- **A layered cipher** — `cipher_id` on each output; the layers independent.
- **The charset is the first discriminator** — `+/=`/hex/`01` → encoding.
- **`π(σ(p))` order matters** — `π` first (position-only), then `σ`.

## The verify

`pt` language + `enc(pt)=ct`.
