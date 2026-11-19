# Probe catalogue — every measurable read, in order

## Phase 0 — the passive reads (no computation)

| Probe | Reads | The signal |
|---|---|---|
| `ls`/`file`/`xxd` | the file types | `.pem`/`der`/`json`/`txt`/`py` |
| `RSA.importKey` | `n`,`e`,private fields | `n` bits, `e`, `d`/`p`/`q`/`dp`/`dq`/`qInv` present |
| `openssl asn1parse` | a `.der`/`crt` | the field layout |
| `re.findall(r'\d{20,}')` | the integers | the `n`,`e`,`c` counts |
| read `keygen.py`/`chal.py` | the generator | `next_prime`,`seed`,`getPrime(d)`,`p-1`,`e=3`,no pad |
| `crypto_attack.py list` | the inventory | every id + its bound |

## Phase 1 — the arithmetic reads (cheap)

| Probe | Reads | The signal |
|---|---|---|
| `n.bit_length()` | `n` size | 512/1024/2048/4096 |
| `e.bit_length()` vs `n` | `e` size | `e≈n` → small `d` |
| `e in (3,5,17,257)` | `e` small | wrap/broadcast/relation |
| `e==65537` | default | bug elsewhere |
| `gcd(e,phi)` if `phi`/`p`,`q` known | `e,phi` | `>1` → `eth-root` |
| `isqrt(n)**2==n` | square `n` | `n=p²` |
| `isPrime(n)` | prime `n` | `phi=n-1` |
| `factorint(n)` | smooth `n` | trivial factor |
| `m.bit_length()*e` vs `n` | the wrap | `m^e<n` → root |

## Phase 2 — the attack reads (the discriminating probes)

| Probe | Reads | Fires when |
|---|---|---|
| `gcd(ni,nj)` pairwise | a shared prime | `>1` → `batch-gcd` |
| `ext_gcd(e1,e2)` | Bezout `a,b` | `gcd=1` → `common-modulus` |
| `a=isqrt(n)+1` loop | `a²-n` square | `fermat` converges |
| CF convergents of `e/n` | `k/d` | `wiener` |
| `a^{B!} mod n`, `gcd(a-1,n)` | `p` | `pollard-pm1` |
| `crt`/`integer_nthroot` | `m` | `hastad`/`small-e`/`crt` |
| `pow(a,e*dp-1,n)-1` gcd | `p` | `crt` dp leak |
| `gcd(s'^e-m,n)` | `q` | `crt` Bellcore |

## Phase 3 — the verify reads (the proof)

| Probe | Reads | The gate |
|---|---|---|
| `pow(m,e,n)==c` | `m` | plaintext recovery |
| `p*q==n` | `p`,`q` | factor recovery |
| `pow(c,d,n)==m` | `d` | `d` recovery |
| `1<p<n` and `p|n` | `p` | a real factor |
| `p*q==n` + `phi` | `phi` | the consistency |

## The rule

A probe is a *read* — it produces a measurable signal or a falsifier. The attack
is a probe; the verify is the proof. Run the passive reads first — they fill
the sheet for free.
