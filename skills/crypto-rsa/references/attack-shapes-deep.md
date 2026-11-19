# Attack shapes deep — the challenge-shape vocabulary

## The six families → their shapes

### Wrap — `m^e<n`
- A small `e` (3/5/17), a short `m`, no pad → `small-e-root`/`nth-root`.
- `e` n's, same `m` → `hastad`.

### Gap — `|p-q|` small
- `q=next_prime(p)`/`p+k`/`p+2` → `fermat`.

### Divisor — shared/smooth `p`
- A `.json`/list of `n` → `batch-gcd`.
- `p-1` smooth → `pollard-pm1`.

### Exponent — `ed≡1` leaks `d`
- `e`≈`n` → `wiener`/`boneh-durfee`.
- Two `e` on `n`, `gcd=1` → `common-modulus`.
- `d`/`phi` held → `factor-from-d`/`rsa-decrypt`.

### Partial — bits
- `p` high/low bits → `coppersmith-*`.
- `m` partial → `coppersmith` partial-message.

### Relation/leak — structure
- `m2=a·m1+b` → `franklin-reiter`.
- `sig` fault / `dp`,`dq`,`qInv` / `m mod pi` → `crt`.
- `gcd(e,phi)>1` → `eth-root`.
- `p`,`q` held → `rsa-decrypt`.

## The degenerate shapes

`n=p²` → `phi=p(p-1)` · `n` prime → `phi=n-1` · `n` multi → `phi=∏(pi-1)` ·
`n` smooth → `factorint` · `n` small → a table.

## The verify

`pow(m,e,n)==c` / `p*q==n`.
