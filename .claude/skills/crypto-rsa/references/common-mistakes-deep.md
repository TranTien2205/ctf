# Common mistakes deep — the traps, annotated

## Attacking the wrong parameter

`e` small + `m` short → `small-e`; `e` small + broadcast → `hastad`; `e`≈`n` →
small `d`; `d`/`phi` held → `factor-from-d`. The *tells* route — the parameter
matters, not the attack's name.

## Confusing the bounds

- `d<n^0.25` (Wiener) ≠ `d<n^0.292` (Boneh-Durfee) — the wider reach is slower.
- The Coppersmith window `n^0.25` (factor) ≠ `n^(1/e)` (message) — the degree
  `d` differs.
- `m^e<n` (exact root) ≠ `m^e≥n` (wrapped — `hastad`/`coppersmith`).

## `n=p²` → `phi=(p-1)²`

`n=p²` → `phi=p(p-1)` — Euler for a prime power, not `(p-1)²`. A wrong `phi` →
a wrong `d` → `pow` fails.

## `pow(m,e,n)==c` skipped

`m` is a candidate until `pow`. A `m` that decrypts but isn't re-encryptable is
wrong; a `p*q==n` that doesn't decrypt `c` is incomplete.

## Reading `d` as a plaintext leak

`d` held → `factor-from-d`/`rsa-decrypt` — `d` is the *exponent*, not `m`.
`phi`/`dp`/`qInv` similarly.

## A flag-shaped `m` that isn't

`m` may be a padded block — strip `\x00\x02<pad>\x00`/OAEP. A flag-shaped `m`
that fails `pow` is a decoy.

## The relation misread

`m2=a·m1+b` is `franklin-reiter`; `m_i=a_i·m+b_i` broadcast is `hastad`/pad;
a random pad is dead — read the keygen.
