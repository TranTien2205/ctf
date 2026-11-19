# Lattice bounds — the exact ceilings, and what LLL costs

## The two small-d bounds

| Bound | Attack | The polynomial |
|---|---|---|
| `d < n^0.25` | `wiener` | convergent `k/d` of `e/n` — no lattice |
| `d < n^0.292` | `boneh-durfee` | `f(x,y)=x(A-y)+1 mod e`, `A=n+1` — LLL |

Wiener is a theorem (CF convergents). Boneh-Durfee is a lattice bound —
`0.292` is the Coppersmith-derived ceiling; the `m`,`t` parameters approach it.

## The Coppersmith bounds

| The polynomial | The recoverable root |
|---|---|
| `f(x)=a+x ≡ 0 mod p`, `p≥n^0.5` | `|x| < n^0.25` |
| `f(x)=pad+x ≡ 0 mod n`, `e` | `|x| < n^(1/e)` |
| bivariate small-`d` | `d < n^0.292` |

`β=½` for `p≥n^0.5` gives the `n^0.25` bound; `β` smaller (a multiprime `n`,
`p` smaller) gives a lower bound.

## The LLL cost

LLL runs in polynomial time but the lattice dimension `ω` grows with `m`,`t`:
- `wiener` — no lattice, instant.
- `boneh-durfee` `m=4,t=3` — `ω~O(m²)`, seconds on pure-python; `fpylll` absent
  → a pure-python LLL, slower but same bound.
- `coppersmith` — similar; the dimension `m` tunes the bound vs the time.

## The bound as falsifier

A bound is a theorem — `d≥n^0.292` is *unreachable* by Boneh-Durfee, not a
matter of more `m`. A window `< n^0.25` is *unreachable* by Coppersmith-`β=½`.
The bound exceeded → a negative result, the attack closed.

## The fallback when the bound is near

- `d` near `n^0.292` → raise `m`,`t` (approach the bound), accept the time.
- window near `n^0.25` → raise the lattice `m`.
- below the bound → LLL is fast; above → mathematically impossible, record the
  negative.

## The honest status

These are the published bounds — `n^0.25` (Wiener), `n^0.292` (Boneh-Durfee),
`n^0.25` (Coppersmith-`β=½`), `n^(1/e)` (partial-message). The tool reports the
same numbers; `lll_backend` reports whether `fpylll` or pure-python is in use.
