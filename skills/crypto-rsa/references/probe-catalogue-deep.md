# Probe catalogue deep — every measurable read, annotated

## Phase 0 — the passive reads (no computation, fill the sheet)

| Probe | The command / read | The signal |
|---|---|---|
| the file types | `ls`/`file`/`xxd` | `.pem`/`der`/`json`/`txt`/`py`/`bin`/`pcap` |
| the key fields | `RSA.importKey` | `n` bits, `e`, `d`/`p`/`q`/`dp`/`dq`/`qInv` |
| a `.der` layout | `openssl asn1parse` | the `SEQUENCE` fields |
| the integers | `re.findall(r'\d{20,}')` | the `n`,`e`,`c` counts |
| the generator | read `keygen.py`/`chal.py` | `next_prime`,`seed`,`getPrime(d)`,`p-1`,`e=3`,no pad,`m2=a·m1+b`,`dp`,`dq`,`qInv`,`redact` |
| the inventory | `crypto_attack.py list` | every id + its bound |

## Phase 1 — the arithmetic reads (cheap, discriminating)

| Probe | The read | The signal |
|---|---|---|
| `n.bit_length()` | `n` size | 512/1024/2048/4096 — context, not a bound |
| `e.bit_length()` vs `n` | `e` size | `e≈n` → small `d` → `wiener`/`boneh-durfee` |
| `e in (3,5,17,257)` | `e` small | `small-e`/`hastad`/`franklin-reiter` |
| `e==65537` | default | the bug is elsewhere |
| `gcd(e,phi)` | `e`,`phi` | `>1` → `eth-root` |
| `isqrt(n)**2==n` | square `n` | `n=p²` → `phi=p(p-1)` |
| `isPrime(n)` | prime `n` | `phi=n-1` |
| `factorint(n)` | smooth `n` | a direct factor |
| `m.bit_length()*e` vs `n` | the wrap | `m^e<n` → `small-e`/`nth-root` |

## Phase 2 — the attack reads (the discriminating probes)

| Probe | The read | Fires → |
|---|---|---|
| `gcd(ni,nj)` pairwise | a shared prime | `batch-gcd` |
| `gcdex(e1,e2)` | Bezout `a,b` | `common-modulus` |
| `a=isqrt(n)+1` loop | `a²-n` square | `fermat` |
| CF convergents `k/d` of `e/n` | `d` | `wiener` |
| `a^{B!} mod n`, `gcd(a-1,n)` | `p` | `pollard-pm1` |
| `crt`/`integer_nthroot` | `m` | `hastad`/`small-e`/`crt` |
| `gcd(s'^e-m,n)` | `q` | `crt` Bellcore (manual) |
| `e·dp-1` loop | `p` | `crt` dp (manual) |
| `f(x)=a+x` LLL small root | `p` | `coppersmith` |
| `f(x,y)=x(A-y)+1` LLL | `d`/`p`,`q` | `boneh-durfee` |
| `gcd(x^e-c1,(ax+b)^e-c2)` | `m` | `franklin-reiter` (manual) |

## Phase 3 — the verify reads (the proof)

| Probe | The read | The gate |
|---|---|---|
| `pow(m,e,n)==c` | `m` | plaintext recovery |
| `p*q==n` | `p`,`q` | factor recovery |
| `pow(c,d,n)==m` | `d` | `d` recovery |
| `1<p<n`, `p|n` | `p` | a real factor |
| `n-phi+1==p+q` | `phi` | the consistency |
| `pow(m_i,e,n)==c` + format | `m_i` | `eth-root` |

## The rule

A probe is a *read* — it produces a measurable signal or a falsifier. The attack
is a probe; the verify is the proof. Run the passive reads first — they fill the
sheet for free.
