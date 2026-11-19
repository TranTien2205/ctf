# boneh-durfee deep — the lattice ceiling for small d

## The precondition

`d` small but beyond Wiener's `n^0.25` — `d` in the `0.25–0.292` window, or the
challenge states `d < n^0.27`. `e` is large (`e≈n`).

## The derivation

`ed ≡ 1 mod φ` ⇒ `ed + k·φ = ed + k·(n - p - q + 1)` for `ed = 1 + kφ`.
Rearrange mod `e`:

```
ed + k·(n+1) - k·(p+q) ≡ 1 + k·n   (mod e)
⇒  k·(A - y) + 1 ≡ 0  (mod e)      where A = n+1, y = p+q
```

The bivariate polynomial `f(x,y) = x·(A - y) + 1` has the small root `(x,y) =
(k, p+q)` mod `e`. `k < d` (small), `y = p+q < 3√n`. Coppersmith's bivariate
method finds the root for `d < n^0.292`.

## The lattice

Build the lattice of `f`-shifts and `e`-multiples; LLL reduces it; the short
vector encodes a bivariate polynomial whose small root is `(k, p+q)`. The `m`
(lattice dimension) and `t` parameters tune the approach toward `n^0.292`.

## The tool

```bash
python3 tools/crypto_attack.py boneh-durfee --n <n> --e <e> --c <c>
python3 tools/crypto_attack.py boneh-durfee-escalate --n <n> --e <e> --c <c>  # auto m
```

`escalate` retries increasing `m` — hands-off but slower.

## The bound / falsifier

`d < n^0.292` is the hard ceiling — exceeding it is the falsifier, and no `m`
parameter recovers. Pure-python LLL is slow — minutes on a large `m`.

## The verify

`pow(c,d,n)` → plaintext; `p*q==n`.

## The traps

- Check `d`'s bound against `wiener` first — `d<n^0.25` is cheaper via CF.
- `fpylll` absent → pure-python LLL — much slower; the `lll_backend` line in
  `list` reports it.
- The applicability line the tool prints is the contract — read it before the
  lattice.
