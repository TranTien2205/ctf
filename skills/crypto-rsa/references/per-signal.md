# Per-signal map — the observation → the hypothesis

## The count signals

- `moduli ≥ 2` → `batch-gcd` / `hastad`
- `e` count = 2 on 1 `n` → `common-modulus`
- `c` count ≥ `e` → `hastad`
- `1` `n` → single-modulus

## The exponent signals

- `e`=3/5/17 → `small-e`/`hastad`/`franklin-reiter`
- `e`=65537 → default → look elsewhere
- `e`~`n` → `wiener`/`boneh-durfee`
- `gcd(e,phi)>1` → `eth-root`

## The keygen signals

- `next_prime`/`p+k`/`q=p+2` → `fermat`
- `getPrime(small)` for `d` → `wiener`/`boneh-durfee`
- `random.seed`/`reused p` → `batch-gcd`
- `p-1` smooth → `pollard-pm1`
- `e=3`,no pad → `small-e`/`hastad`
- `m2=a·m1+b` → `franklin-reiter`
- `dp`,`dq`,`qInv` → `crt`
- `d`/`phi` printed → `factor-from-d`
- `redact`/`XXXX` on `p`/`d`/`dp` → `coppersmith`/`crt`/`factor-from-d`

## The file signals

- public `.pem` → `n`,`e` only
- partial private `.pem` → `crt`/`coppersmith`/`factor-from-d`
- `.json` of `n` → `batch-gcd`
- `.txt` of `n`,`e`,`c` → the sheet
- `.py` source → the comment

## The runtime signals

- socket printing `n`,`e`,`c` → transport, the numbers
- socket computing on `m` → `crypto-symmetric-oracle`
- a signing pair → `crt` Bellcore

## The degenerate signals

- `n` square → `phi=p(p-1)`
- `n` prime → `phi=n-1`
- `n` multi-prime → `phi=∏(pi-1)`
- `e`=1/`m`=0,1 → trivial
