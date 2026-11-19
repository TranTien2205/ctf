# factor-from-d deep — recovering (p,q) from a leaked private value

## The preconditions

- `d` leaked — `ed - 1` is a multiple of `φ`.
- `φ` leaked — `p+q = n - φ + 1` directly.
- `dp`,`dq`,`qInv` leaked — CRT reconstruction.
- the factors `p`,`q` themselves.

## The maths

### From `φ`

`φ = n - p - q + 1` ⇒ `p + q = n - φ + 1`. Solve `x² - (p+q)x + n = 0`:
`p,q = ((p+q) ± √((p+q)² - 4n))/2`.

### From `d` (the randomized split)

`ed - 1 = k·φ` for unknown `k`. Write `ed-1 = 2^t·r` with `r` odd. Pick a random
`g`; compute `x = g^r mod n`, then square: `x, x², x⁴, …`. For a `g` that is a
non-square mod `n`, some `x` satisfies `x² ≡ 1 mod p` but `≢ 1 mod q` →
`gcd(x-1, n) = p`. Repeat for a few `g` — the standard Miller-Rabin-flavoured
factor-from-`d`.

```python
import random
from math import gcd
k = e*d - 1
t, r = 0, k
while r % 2 == 0: t += 1; r //= 2
for _ in range(100):
    g = random.randrange(2, n)
    x = pow(g, r, n)
    if x in (1, n-1): continue
    for _ in range(t):
        y = pow(x, 2, n)
        if y == n-1: break
        if y == 1:
            p = gcd(x-1, n)
            if 1 < p < n: return p, n//p
        x = y
```

### From `dp`

`e·dp - 1` is a multiple of `p-1` → `gcd(a^(e·dp-1)-1, n) = p`.

## The tool

```bash
python3 tools/crypto_attack.py factor-from-d --n <n> --e <e> --d <d>
python3 tools/crypto_attack.py rsa-decrypt --n <n> --e <e> --c <c> --p <p> --q <q>
```

`rsa-decrypt` handles `gcd(e,φ)>1` — no inverse → `eth-root` among `gcd` roots.

## The bound / falsifier

None — direct arithmetic. Failure means the `d`/`φ` doesn't match `(e,n)`.

## The verify

`p*q==n`, `pow(m,e,n)==c`. The whole proof standard.

## The traps

- `gcd(e,φ)>1` → no inverse; `eth-root` not `inverse(e,φ)`.
- A "leaked `d`" failing `pow(c,d,n)==m` is a decoy — verify the pairing.
- `p`,`q` may come back either order — both valid.
- `phi = ed-1` alone is *not* `φ` — it's `k·φ`; the split recovers the factor.
