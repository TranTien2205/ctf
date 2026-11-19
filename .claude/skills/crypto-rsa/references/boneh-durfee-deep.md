# boneh-durfee deep — the small-d lattice attack, the full treatment

## The mechanism

`ed ≡ 1 mod φ` → `ed + k(n+1-p-q) = 1 + kn` → `e·d + k·s ≡ 1 + k(n+1) mod e`
with `s = p+q`. Rearranged: `f(x,y) = x(A-y) + 1 ≡ 0 mod e`, `A = n+1`, has the
root `(k, s)` where `k ≈ d < n^0.292` and `s < n^0.5`. Coppersmith's bivariate
small-root LLL recovers `(k,s)` → `d` and `p`,`q`.

## Detection

- **`e`≈`n`** — small `d` (same tell as wiener).
- **`d` in `n^0.25..n^0.292`** — beyond Wiener, within the lattice bound.
- **keygen**: `d` explicitly small but larger than `n^0.25`.

## The bound / falsifier

`d < n^0.292`. `d ≥ n^0.292` → small-d closed — the bound is a theorem. The
`m`,`t` lattice parameters *approach* the bound; they cannot exceed it.

## The attack

```bash
python3 tools/crypto_attack.py boneh-durfee --n <n> --e <e>
python3 tools/crypto_attack.py boneh-durfee-escalate --n <n> --e <e> --m 4 --t 3
```

`fpylll` is absent → `tools/crypto/` runs a pure-python LLL — slower, same
bound. `crypto_attack.py list` reports `lll_backend`. The lattice dimension is
`ω ~ O(m²)` — raise `m`,`t` to approach `n^0.292`.

## The chain

`(k,s)` → `s = p+q` → `p`,`q` from `x² - sx + n = 0` → `phi` → `d` → `m` →
`pow` verify.

## The verify

`pow(c,d,n)==m` → `pow(m,e,n)==c`; or `p*q==n` on the quadratic roots.

## Worked shape

```
f(x,y) = x(A-y) + 1  mod e, A = n+1
x = k  (k ≈ d),  y = s (s = p+q)
LLL → the small roots (k, s)
→ d = k,  p,q = (s ± sqrt(s²-4n))/2
```

## Variants

- **`boneh-durfee-escalate`** — raise `m`,`t` to approach `n^0.292`.
- **a partial `d`** — combine with `coppersmith` if `d`'s bits leak.

## Failure modes

- `d ≥ n^0.292` — unreachable.
- LLL too slow — the dimension `ω~O(m²)`; give it the budget, not a retry.
- `fpylll` absent → pure-python LLL may be weaker at the bound's edge.

## The honest status

Boneh-Durfee 1999 — catalogue.
