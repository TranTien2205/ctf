# per-attack boneh-durfee deep — the small-d lattice, the full treatment

## The mechanism

`ed ≡ 1 mod φ` → `e·d + k·s ≡ 1 + k(n+1) mod e`, `s=p+q`. `f(x,y)=x(A-y)+1≡0
mod e`, `A=n+1`, has root `(k,s)`, `k≈d<n^0.292`, `s<n^0.5`. Coppersmith's
bivariate small-root LLL → `(k,s)` → `d`,`p`,`q`.

## Detection

- `e`≈`n` — small `d`.
- `d` in `n^0.25..n^0.292` — beyond Wiener.
- `d` explicitly small but larger than `n^0.25`.

## The bound / falsifier

`d < n^0.292`. `d ≥ n^0.292` → closed. `m`,`t` approach the bound.

## The attack

```bash
crypto_attack.py boneh-durfee --n <n> --e <e> [--delta --m --t]
crypto_attack.py boneh-durfee-escalate --n <n> --e <e> --m <m> --t <t>
```

`fpylll` absent → pure-python LLL — `ω~O(m²)` dimension.

## The chain

`(k,s)` → `s=p+q` → `p`,`q` from `x²-sx+n=0` → `phi` → `d` → `m` → `pow`.

## The verify

`pow(c,d,n)==m` → `pow(m,e,n)==c`; `p*q==n`.

## Failure modes

- `d ≥ n^0.292` — unreachable.
- LLL slow — `ω~O(m²)`; budget not retry.
- `fpylll` absent → weaker at the edge.

## The honest status

Boneh-Durfee 1999 — catalogue.
