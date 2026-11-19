# Boundary cases catalogue — the edge forms, indexed

## `e` boundaries

- `e`=1 → `c=m` · `e`=3/5/17 → `small-e`/`hastad`/`franklin-reiter` ·
  `e`=65537 → default · `e`≈`n` → `wiener`/`boneh-durfee` ·
  `gcd(e,phi)>1` → `eth-root`.

## `n` boundaries

- `n` prime → `phi=n-1` · `n`=p² → `phi=p(p-1)` · `n` smooth → `factorint` ·
  `n` multi → `phi=∏(pi-1)` · `n`≥2 → `batch-gcd`/`hastad` · `n` small → a table.

## `d`/`phi` boundaries

- `d` held → `factor-from-d`/`rsa-decrypt` · `phi` held → `factor-from-d` ·
  `dp`,`dq`,`qInv` → `crt` · `d` small → `wiener`/`boneh-durfee` ·
  `d` multi (λ/φ) → both decrypt.

## `m` boundaries

- `m^e<n` → `small-e` · `m^e≥n` → `hastad`/`coppersmith` · `m2=a·m1+b` →
  `franklin-reiter` · `m` partial → `coppersmith` · `m` padded → strip ·
  `m`=0/1 → trivial.

## `p`,`q` boundaries

- `|p-q|` small → `fermat` · `p` shared → `batch-gcd` · `p-1` smooth →
  `pollard-pm1` · `p` bits → `coppersmith` · `p`,`q` held → `rsa-decrypt`/`eth-root`.

## The verify

`pow(m,e,n)==c` / `p*q==n`.
