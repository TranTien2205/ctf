# small-e-root / nth-root deep — the no-wrap shortcut

## The precondition

One modulus `n`, small `e` (typically 3), a message `m` short enough that
`m^e < n`. The ciphertext `c` is then `m^e` as a *plain integer* — the modular
reduction never engaged.

## The maths

`c = m^e` exactly → `m = floor(c^(1/e))`. Verify it's an exact root.

```python
from sympy import integer_nthroot
m, exact = integer_nthroot(c, e)
assert exact and pow(m, e) == c        # integer root, no mod n
```

## The tool

```bash
python3 tools/crypto_attack.py small-e-root --n <n> --e <e> --c <c>
python3 tools/crypto_attack.py nth-root --x <x> --n <n>
python3 tools/crypto_attack.py eth-root --c <c> --e <e> --factors "<p>,<q>"
```

`nth-root` is the generic exact root; `eth-root` finds an `e`-th root **mod n**
via the factorisation — for when `gcd(e,φ)>1` or the factors are held.

## The bound / falsifier

`m^e < n` strictly. `m^e ≥ n` → `c` wrapped the modulus → the exact root is not
`m` → route to `hastad` (broadcast) or `coppersmith` (partial `m`).

The check: `m`'s estimated size vs `n`. A 512-bit `n`, `e=3`, ~100-byte flag →
`m³ ~ 2400` bits < `n` ~ 512? No — wait, `m` is 800 bits, `m³` is 2400 bits > `n`
512 — that wraps. The shortcut needs `m` *much* smaller than `n`: `e·log2(m) <
log2(n)`, i.e. `m` under `n^(1/e)`. For `e=3`, `m < n^(1/3)` — a ~170-bit message
under a 512-bit `n`. A real flag usually needs `hastad` or `coppersmith` instead.

## The verify

`pow(m,e)==c` (plain integer), or `pow(m,e,n)==c` if `m` was padded just below
the wrap boundary.

## The traps

- **`e=3` alone ≠ weak.** The wrap check `m^e<n` is the gate — a real-size flag
  under `e=3` usually wraps.
- `m` is *much* smaller than intuition suggests — `n^(1/e)`, not `n`.
- `eth-root` for `gcd(e,φ)>1` gives `gcd` candidate roots — disambiguate by flag
  format.
