# coppersmith — the small-root lattice attacks, complete

## What it is

LLL-based small-root finding for `f(x) ≡ 0 mod p` (a factor of `n`) or `mod n`.
Recovers `p` when a contiguous window of `p`'s bits leaks, or a partially-known
`m`.

## The mechanism

`f(x) = a + x ≡ 0 mod p`, `p ≥ n^β`. For `β=½`, roots `|x| < n^(β²/d) = n^0.25`
are recoverable — LLL finds a polynomial with `x0` as a small integer root.

## The variants

- **`coppersmith-high-bits`** — `p` = known-high `a` + unknown-low `x`,
  `|x| < n^0.25`. The classic "half the key leaked".
- **`coppersmith-core`** — a centred guess `a` within `n^0.25` of `p`; or the
  general `f(x)` small-root.
- **partial-message** — `f(x) = pad + x ≡ 0 mod n`, `|x| < n^(1/e)` — a known
  prefix/suffix of `m`.

## Detection

- **a redacted/leaked `p`** — high or low bytes present in a partial private key.
- **a centred guess** — `p` known to within `n^0.25`.
- **a pad/prefix** — `m` = `flag{...}` or a known header + unknown tail.

## The bound / falsifier

- factor: the unknown window `< n^0.25` (for `p≥n^0.5`).
- message: the unknown `< n^(1/e)`.
Below the bound → closed.

## The attack

```bash
python3 tools/crypto_attack.py coppersmith-high-bits --n <n> --known <a> --bits <b>
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
- the `a`/`f` layout wrong → recheck the leak.

## The honest status

Standard published attack (Coppersmith 1996) — catalogue.
