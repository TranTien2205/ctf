# per-attack coppersmith deep — the lattice small-root, the full treatment

## The mechanism

`f(x)≡0 mod p` (a factor of `n`) or `mod n`, a *small* root `x0`. LLL finds
`g` over Z with `g(x0)=0` → `x0` → `p` or `m`. Bound `|x0|<n^(β²/d)`.

## The variants

- **`coppersmith-high-bits`** — `p=a+x`, `|x|<n^0.25` — half the key leaked.
- **`coppersmith-core`** — a centred guess `a` within `n^0.25` of `p`.
- **partial-message** — `f(x)=pad+x≡0 mod n`, `|x|<n^(1/e)`.

## Detection

- a redacted/leaked `p` — `XXXX`/masked.
- a centred guess — `p` within `n^0.25`.
- a pad/prefix — `m`=known+unknown.

## The bound / falsifier

window `n^0.25` (factor) / `n^(1/e)` (message). Below → closed.

## The attack

```bash
crypto_attack.py coppersmith-high-bits --n <n> --known <a> --bits <b> [--p-bits]
crypto_attack.py coppersmith-core --n <n> --a <a> --X <bound>
```

`fpylll` absent → pure-python LLL — slower, same bound.

## The verify

`p|n`, `p*q==n` / `pow(m,e,n)==c`.

## Failure modes

- window `< n^0.25` — too small a leak.
- `fpylll` absent → weaker at the edge.
- the `a`/`X` layout wrong → recheck the leak.

## The honest status

Coppersmith 1996 — catalogue.
