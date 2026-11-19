# coppersmith deep2 — the lattice small-root, the full treatment

## The mechanism

`f(x) ≡ 0 mod p` (a factor of `n`) or `mod n`, with a *small* root `x0`. LLL
finds a polynomial `g` over the integers with `g(x0)=0` → `x0` → `p` or `m`.
The bound is `|x0| < n^(β²/d)` for `p ≥ n^β`, `f` degree `d` — `β=½`, `d=1` →
`n^0.25`.

## The variants

- **`coppersmith-high-bits`** — `p` = known-high `a` + unknown-low `x`,
  `|x| < n^0.25`. The classic "half the key leaked" — `f(x)=a+x≡0 mod p`.
- **`coppersmith-core`** — a centred guess `a` within `n^0.25` of `p`; or the
  general `f(x)=a+x` small-root over `p`.
- **partial-message** — `f(x) = pad + x ≡ 0 mod n`, `|x| < n^(1/e)` — a known
  prefix/suffix of `m` recovers the rest.

## Detection

- **a redacted/leaked `p`** — high or low bytes present in a partial private key.
- **a centred guess** — `p` known to within `n^0.25`.
- **a pad/prefix** — `m` = `flag{...}` or a known header + unknown tail.

## The bound / falsifier

- factor: the unknown window `< n^0.25` (for `p≥n^0.5`).
- message: the unknown `< n^(1/e)`.
Below the bound → closed. The `m`,`t` lattice params approach the bound.

## The attack

```bash
python3 tools/crypto_attack.py coppersmith-high-bits --n <n> --known <a> --bits <b> [--p-bits <pb>]
python3 tools/crypto_attack.py coppersmith-core --n <n> --a <a> --X <bound>
```

`fpylll` absent → pure-python LLL — slower, same bound.

## The chain

`x` → `p = a+x` → `q=n/p` → `phi` → `d` → `m` → `pow` verify.

## The verify

`p|n`, `p*q==n` for a factor; `pow(m,e,n)==c` for a message.

## Failure modes

- window `< n^0.25` — too small a leak.
- `fpylll` absent → pure-python LLL may be weaker at the bound's edge.
- the `a`/`X` layout wrong → recheck the leak.

## The honest status

Coppersmith 1996 — catalogue.
