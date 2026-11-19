# Key-length catalogue — the `L` estimation, indexed

## The two estimators

| Estimator | The method | The files |
|---|---|---|
| Kasiski | repeated-n-gram gaps `gcd` → `L` | `key-length*.md`,`detection-deep.md`,`vigenere-*.md` |
| IC-per-coset | the `L` that makes coset-IC ~0.066 | `key-length*.md`,`detection-deep.md` |

## The `L`-mis-estimate

| Case | The fix | The files |
|---|---|---|
| `L'` a multiple `k·L` | try `L`/`L/2`/`2L` | `key-length*.md`,`vigenere-*.md` |
| `L` too small | cosets overlap — re-estimate | `key-length*.md` |
| a short `ct` | Kasiski fails; the coset-IC | `key-length*.md` |
| `L=n` | a single-period `σ` — meaningless | `key-length*.md` |

## The `L`-confirm

Split `ct` into `L` cosets → each coset's chi²-min is `k_j` → the `L` Caesars
give the key — `key-length*.md`,`vigenere-*.md`.

## The `L`-falsifier

No `L` produces language → `subst`/`π`/other; a Beaufort/autokey if the key
shape differs — `per-falsifier*.md`,`beaufort-autokey*.md`.

## The verify

`key` → `p_i = c_i - k_{i mod L}` → language — `verify*.md`.
