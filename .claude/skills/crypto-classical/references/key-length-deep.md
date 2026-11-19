# Key-length deep — the `L` estimation, annotated

## The two estimators

### Kasiski — the gap gcd

A repeated n-gram (≥3 letters) in the `ct` — the same `pt` n-gram encrypted
with the same `k` positions → the gap `g` is a multiple of `L`. GCD the gaps
→ `L`. `THE`/`AND`/`ING` repeat often in English — their `ct` images repeat
at multiples of `L`.

### IC-per-coset — the coincidence

Try `L=1,2,3,...`: split `ct` into `L` cosets `ct[j::L]`, average each coset's
IC. The `L` where the average rises to ~0.066 is the period — each coset is a
Caesar.

## The `L`-mis-estimate

- **`L` a multiple** — `L'=k·L` gives a near-decode with periodic errors —
  try `L/k` — the coset-IC confirms.
- **`L` too small** — cosets overlap → garbage.
- **A short `ct`** — Kasiski fails (no repeats); IC-coset is the estimator.
- **`L=n`** — each letter its own coset → a single-period `σ` — meaningless.

## The `L`-confirm

Split `ct` into `L` cosets; each coset's chi²-min is `k_j`; the `L` Caesars
give the key — `LXFOPVEFRNHR` at `L=5` → `LEMON`.

## The `L=1` boundary

`L=1` → Vigenere = Caesar — `caesar` solves it.

## The `L`-falsifier

No `L` produces language → not Vigenere → `subst`/`π`/other; or a Beaufort/
autokey (different key shape).

## The verify

`key` → `p_i = c_i - k_{i mod L}` → language; re-encrypt reproduces `ct`.
