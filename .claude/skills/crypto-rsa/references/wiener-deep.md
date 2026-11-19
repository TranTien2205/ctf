# wiener deep — continued fractions recover a small d

## The precondition

`d` small — `d = getPrime(128)` or similar in the keygen — making
`e = inverse(d, φ)` a value the size of `n`.

## The derivation

`ed ≡ 1 mod φ` ⇒ `ed - kφ = 1` for some `k`. Divide by `d·φ`:

```
e/φ  -  k/d  =  1/(d·φ)
```

`φ ≈ n`, so `e/n ≈ k/d`. The error `|e/n - k/d|` is small when `d` is small;
Legendre's theorem says `k/d` is then a convergent of `e/n`'s continued-fraction
expansion.

## The procedure

1. Expand `e/n` as a CF: `e/n = [a0; a1, a2, …]`.
2. For each convergent `ki/di`, compute candidate `φ' = (e·di - 1)/ki`.
3. If `φ'` is an integer, `p+q = n - φ' + 1`; solve `x²-(p+q)x+n=0`.
4. Integer `p`,`q` → `d=di` is the private exponent.

```python
from Crypto.Util.number import inverse
def cf_convergents(num, den):
    while den:
        a = num//den
        yield a; num,den = den, num-a*den
# convergents ki/di → check each φ'
```

## The tool

```bash
python3 tools/crypto_attack.py wiener --n <n> --e <e> --c <c>
```

## The bound / falsifier

`d < n^0.25` (the classic `⅓·n^0.25`). `d` in `0.25–0.292` → `boneh-durfee`.
`d ≥ n^0.292` → dead.

## The verify

`pow(c,d,n)` yields plaintext; `p*q==n` is the hard check.

## The traps

- **You cannot see `d`** — the signal is a *large `e`*. `e=65537` → `d` random
  → Wiener is a negative.
- Verify each convergent by reconstructing `p`,`q` — a plausible `d` that fails
  `pow` is wrong.
- If Wiener fails but `e` is still large, escalate to `boneh-durfee` before
  abandoning small-`d`.
