# Lead grammar deep — reading a hint into a signal

## The hint → signal

| The hint | The signal |
|---|---|
| "primes generated sequentially" | `fermat` — `q=next_prime(p)` |
| "shared/semi-primes" | `batch-gcd` |
| "fast decryption" | small `d` → `wiener`/`boneh-durfee` |
| "e=3, broadcast" | `hastad` |
| "partial private key" | `coppersmith`/`crt`/`factor-from-d` |
| "same m, different e" | `common-modulus` |
| "related messages" | `franklin-reiter` |
| "m^n less than n" | `small-e-root`/`nth-root` |
| "weak primes" | `pollard-pm1`/`fermat`/`batch-gcd` |

## The keygen tell → signal

| The tell | The signal |
|---|---|
| `next_prime`,`p+k`,`q=p+2` | `fermat` |
| `random.seed`,`reused p` | `batch-gcd` |
| `getPrime(d)` small | `wiener`/`boneh-durfee` |
| `p-1` smooth | `pollard-pm1` |
| `e=3`,no pad | `small-e`/`hastad` |
| `m2=a·m1+b` | `franklin-reiter` |
| `dp`,`dq`,`qInv` | `crt` |
| `d`/`phi`/`p`,`q` printed | `factor-from-d`/`rsa-decrypt` |
| `redact`/`XXXX` | `coppersmith`/`crt`/`factor-from-d` |
