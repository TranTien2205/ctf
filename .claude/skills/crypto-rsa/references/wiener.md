# wiener — the small-d continued-fraction attack

`d < n^0.25` → `k/d` a convergent of `e/n` → `d`. Detection: `e`≈`n` (`e=
inverse(d,phi)` for small `d`). Bound: `d<n^0.25` — escalate to `boneh-durfee`
at `n^0.292`. Chain: `d`→`m=c^d`→`pow(m,e,n)==c`. Command: `crypto_attack.py
wiener --n <n> --e <e>`. See `per-attack-wiener.md` for the full module.
