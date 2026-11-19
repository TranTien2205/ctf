# Mechanism deep — the six primitives, the full treatment

## Primitive 1 — the wrap

`c = m^e` with `m^e < n`: the modulo never engaged. `c` is an exact integer
power. `small-e-root`/`nth-root` take the `e`th root; `hastad` CRTs `e` coprime
moduli first. **Falsifier**: `m^e ≥ n`.

## Primitive 2 — the gap

`p`,`q` close: `n = a²-b²`, `a=(p+q)/2` near `√n`. `fermat` walks `a` until
`a²-n` is `b²`. **Falsifier**: `|p-q|` too large (`a` past budget).

## Primitive 3 — the divisor

A shared prime (`gcd(ni,nj)=p`) or a smooth `p-1` (`a^{B!}≡1 mod p`) → `gcd`
leaks a factor. `batch-gcd`, `pollard-pm1`. **Falsifier**: all `gcd=1` /
`p-1` not `B`-smooth.

## Primitive 4 — the exponent

`ed≡1 mod φ` leaks `d`: `d<n^0.25` (Wiener CF), `d<n^0.292` (Boneh-Durfee
lattice), `gcd(e1,e2)=1` (Bezout), `d`/`phi`/`dp` held (arithmetic).
**Falsifier**: `d≥n^0.292` / `gcd>1` / `d` fails `pow`.

## Primitive 5 — the partial

A contiguous window of `p` (`≥n^0.25` unknown) or `m` (`≥n^(1/e)` unknown) →
Coppersmith small-root. `coppersmith-high-bits`, `coppersmith-core`.
**Falsifier**: window below the bound.

## Primitive 6 — the relation/leak

`m2=a·m1+b` (Franklin-Reiter), residues/fault/`dp` (crt), `d`/`phi`/`p`,`q`
(factor-from-d/rsa-decrypt/eth-root). **Falsifier**: not linear / `∏pi≤m` / no
fault / wrong input.

## The falsifier table

| Primitive | The falsifier |
|---|---|
| wrap | `m^e≥n` / `<e` n's / pad |
| gap | `|p-q|` large |
| divisor | `gcd=1` / `p-1` not smooth |
| exponent | `d≥n^0.292` / `gcd>1` / `d` fails |
| partial | window `<n^0.25` / `<n^(1/e)` |
| relation | not linear / `∏pi≤m` / no fault |
| leak | `pow`/`gcd` fails |
