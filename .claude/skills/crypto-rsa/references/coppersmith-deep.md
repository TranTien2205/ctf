# coppersmith deep — partial knowledge recovers the secret

## The two preconditions

- **high-bits**: the top half of a factor `p` is known (a printed prefix, a
  redacted key).
- **core**: a centred guess `a` of `p` within `|p-a| < n^0.25`-ish.

Both exploit that a *small* unknown part of a factor is a small modular root.

## The maths

`f(x) = a + x ≡ 0 (mod p)`, `x = p - a` the unknown. For `x < X ≈ n^0.25` (the
`β=½` bound), Coppersmith's univariate method finds `x`:

1. Build a lattice of `n`-multiples and `x`-shifted powers `x^j·f(x)^i`.
2. LLL reduces it — a short vector encodes a polynomial `g` with `g(x₀)=0`.
3. `x₀` is the small root → `p = a + x₀`.

For `coppersmith-high-bits`, `a = p_high << shift` — the leaked top bytes placed
in position. For `coppersmith-core`, `a` is the raw centred approximation.

## The message variant

The same method applies to `m`: known flag prefix + small unknown tail →
`f(x) = m_known·2^s + x`, root `x` recovers the tail when the unknown window is
below the `e`-scaled bound. This is the partial-message Coppersmith — for a
*padded* short `m` it is the route when `small-e-root` fails.

## The tool

```bash
python3 tools/crypto_attack.py coppersmith-high-bits --n <n> --known <a> --bits <b> [--p-bits <pb>]
python3 tools/crypto_attack.py coppersmith-core --n <n> --a <a> --X <bound>
```

## The bound / falsifier

The known/approximate window must be ≥ `n^0.25` of the factor. Below it the
lattice fails — the bound is a theorem, not a parameter.

## The verify

`p|n`, `p*q==n`, `rsa-decrypt` → `pow(m,e,n)==c`. For a message: `pow(m,e,n)==c`.

## The traps

- **High vs low bits use different `a`.** `coppersmith-high-bits` wants the top
  bytes shifted; a *low*-bits leak uses `coppersmith-core` with the right `a`.
- A "partially redacted PEM" leaks `p`'s top bytes — reconstruct `a`, not the
  masked literal.
- The `approx` must be *centred* — a raw high-bits value may need adjusting to
  sit within the window.
- Pure-python LLL is slow — the bound matters more than runtime.
