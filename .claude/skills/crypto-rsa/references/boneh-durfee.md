# boneh-durfee — the small-d lattice attack

`d < n^0.292` → bivariate Coppersmith lattice `f(x,y)=x(A-y)+1 mod e` → `d`.
Detection: `e`≈`n`, `d` in `n^0.25..n^0.292`. Bound: `d<n^0.292` — the LLL
ceiling. `fpylll` absent → pure-python LLL, slower. Commands:
`crypto_attack.py boneh-durfee --n --e`, `boneh-durfee-escalate --n --e --m --t`.
See `per-attack-boneh-durfee.md` for the full module.
