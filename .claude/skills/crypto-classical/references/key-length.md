# Key-length — the `L` estimation deep

## The two estimators

- **Kasiski** — a repeated n-gram (≥3) at gap `g` → `g` a multiple of `L`.
  `gcd` the gaps → `L`.
- **IC-per-coset** — try `L=1,2,3,...`: split `ct` into `L` cosets, average
  each coset's IC. The `L` where the average rises to ~0.066 is the period.

## The `L`-mis-estimate

- **`L` a multiple** — `L'=k·L` gives a near-decode with periodic errors —
  try `L/k`.
- **`L` too small** — cosets overlap → garbage.
- **A short `ct`** — Kasiski fails (no repeats); IC-coset is the estimator.

## The `L`-confirm

Split `ct` into `L` cosets; each coset's chi²-min is `k_j`; the `L` Caesars
give the key — `LXFOPVEFRNHR` at `L=5` → `LEMON`.

## The `L=1` boundary

`L=1` → Vigenere = Caesar — `caesar` solves it.

## The `L`-falsifier

No `L` produces language → not Vigenere → `subst`/`π`/other.

## The verify

`key` → `p_i = c_i - k_{i mod L}` → language; re-encrypt reproduces `ct`.
