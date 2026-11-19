# wiener deep — the small-d continued-fraction attack, the full treatment

## The mechanism

`ed ≡ 1 mod φ` → `ed - k·φ = 1` for some `k < d`. Dividing by `d·n` and using
`φ ≈ n`:

```
|e/n - k/d| < 1/(3d²)   when  d < (1/3)·n^0.25
```

`k/d` is then a convergent of the continued-fraction expansion of `e/n`. The CF
enumerates `k_i/d_i`; each candidate `d_i` gives `φ' = (e·d_i - 1)/k_i`, and
`p`,`q` are the roots of `x² - (n - φ' + 1)x + n = 0` — integer roots confirm.

## Detection

- **`e` ≈ `n` in bit-length** — `e = inverse(d, φ)` for small `d` ≈ `n`.
- **keygen**: `d = getPrime(64)`/`getPrime(128)`/`d small`/`d = <small>`.
- **the tell**: a "fast decryption" note → a deliberately small `d`.

## The bound / falsifier

`d < n^0.25` (the safe form is `d < (1/3)·n^0.25`). `d ≥ n^0.25` → `wiener`
returns nothing → escalate to `boneh-durfee` (`n^0.292`). `d ≥ n^0.292` →
small-d closed — a negative.

## The attack

```python
from Crypto.PublicKey import RSA
def wiener(e, n):
    # CF convergents k/d of e/n
    cf = CF(e, n)                      # the continued fraction
    for (k, d) in cf.convergents():
        if k == 0: continue
        if (e*d - 1) % k: continue
        phi = (e*d - 1) // k
        s = n - phi + 1                # p+q
        disc = s*s - 4*n
        if disc >= 0:
            t = isqrt(disc)
            if t*t == disc:
                return d, (s+t)//2, (s-t)//2   # d, p, q
```

Or: `python3 tools/crypto_attack.py wiener --n <n> --e <e>`.

## The chain

`d` → `m = pow(c,d,n)` → `pow(m,e,n)==c` → the flag.

## The verify

`pow(c,d,n)==m` recovers the plaintext; `pow(m,e,n)==c` proves it. The
`p*q==n` check on the quadratic roots confirms the convergent.

## Variants

- **`d` just over `n^0.25`** → `boneh-durfee` (`n^0.292`).
- **the CF misses** → `boneh-durfee-escalate` (`m`,`t` up).

## Failure modes

- `d ≥ n^0.25` — Wiener's bound; `boneh-durfee` is the wider reach.
- `e` not large — if `e`≈65537, `d` is ~`n`, not small.

## The honest status

Wiener 1990 — catalogue.
