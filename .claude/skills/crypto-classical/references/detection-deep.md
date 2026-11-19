# Detection deep — the statistics, annotated

## The IC — Index of Coincidence

`IC = Σ n_i(n_i-1) / N(N-1)` over the 26 letters — the probability two random
letters from the `ct` are equal.

- **English plaintext**: ~0.066 — the `E`,`T`,`A` spikes raise it.
- **Random/uniform**: ~0.038 — all letters equal.
- **A monoalphabetic** `σ(p)`: the IC is preserved — `σ` only renames the
  letters, the *multiset* is unchanged. → **IC ~0.066 → monoalpha**.
- **A polyalphabetic** `c_i = p_i + k_{i mod L}`: each position's distribution
  is a mix of `L` shifts → the IC flattens toward 0.038. → **IC ~0.038 →
  polyalpha**.
- **A transposition** `π(p)`: the multiset is *exactly* preserved → IC ~0.066
  but the order is scrambled. The frequency *shape* is English.

## The chi² — the Caesar discriminator

`chi²(k) = Σ_i (o_i - e_{(i+k) mod 26})² / e_{(i+k) mod 26}` — fit the `ct`
shifted by `k` against the English frequencies `e`.

- A Caesar `ct` has **one deep minimum** at the true `k` — the shift that puts
  `E`'s image back on `E`.
- A `subst` `ct` has **no deep minimum** — the `σ` isn't a rotation, so no `k`
  fits.

## Kasiski — the period estimator

A repeated n-gram (≥3 letters) in the `ct` — the same `pt` n-gram encrypted
with the same `k` positions → the gap `g` is a multiple of `L`. GCD the gaps
→ `L`. Complement with **IC-per-coset**: the `L` that makes each coset's IC
rise to ~0.066.

## The frequency — the shape

- **ETAOIN-shaped** (the `ct` letters ranked like English) → a `σ` — `σ(E)` is
  the top `ct` letter.
- **Reversed-ETAOIN** (`Z`,`V`,`G` top) → `atbash`.
- **Flat** → polyalphabetic or random.
- **English counts, scrambled order** → transposition.

## The short-ct rule

Under ~30 chars the IC/chi²/Kasiski are unreliable — a 15-char `ct` can read
0.05 by chance. The `flag{`/`CTF{` positions and common letters carry the
solve.
