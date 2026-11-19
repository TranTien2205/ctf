# Detection deep — fingerprinting the RSA weakness, fully

## The four reads

1. **The source** — `keygen.py`/`chal.py`: the generator's misuse line.
2. **The counts** — `len(set(n))`, `len(set(e))`, `len(c)`: the family.
3. **The exponent** — `e` value/size: the cheapest discriminator.
4. **The leak** — `d`,`phi`,`dp`,`p`-bits,`m`-partial,`p`,`q`: the terminal.

## The fingerprint table

| Fingerprint | The attack |
|---|---|
| `e`≈`n` | `wiener`/`boneh-durfee` |
| `e`=3/5/17 | `small-e`/`hastad`/`franklin-reiter` |
| `e`=65537 | default — look elsewhere |
| `gcd(e,phi)>1` | `eth-root` |
| `n` count ≥2 | `batch-gcd`/`hastad` |
| `e` count 2, 1 `n` | `common-modulus` |
| `next_prime`/`p+k` | `fermat` |
| `random.seed` | `batch-gcd` |
| `p-1` smooth | `pollard-pm1` |
| `getPrime(d)` small | `wiener`/`boneh-durfee` |
| `dp`,`dq`,`qInv` | `crt` |
| `d`/`phi` | `factor-from-d` |
| `p` partial | `coppersmith-*` |
| `m2=a·m1+b` | `franklin-reiter` |
| residues/fault | `crt` |
| `n` square/prime | degenerate `phi` |

## The reads in order

`recon-order.md` — source → count → exponent → leak → relation → degenerate.
First yes → `attack-table.md` row → the attack.

## The verify

`pow(m,e,n)==c` or `p*q==n` — the gate.
