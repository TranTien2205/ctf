# Operator summary — the one-paragraph reference

RSA: `n`,`e`,`c` + a leak → `p`,`q`,`d`,`φ`,`m`. `crypto_attack.py list` → the
signal (`e` small/`e`≈`n`/`gcd`/shared `p`/`p-1` smooth/bits/`a·m1+b`/`sig`/
`dp`/`d`/`phi`/`p`,`q`/`|p-q|`/degenerate) → `per-bound.md` →
`crypto_attack.py <id>` → `pow(m,e,n)==c`/`p*q==n`. Catalogue — `../field-notes.md`
for real solves.

## The bounds

`d<n^0.25` wiener · `d<n^0.292` boneh-durfee · window `n^0.25`/`n^(1/e)`
coppersmith · `m^e<n` small-e/nth-root · `≥e` n's hastad · `gcd=1`
common-modulus · `|p-q|` fermat · `B`≥factor pollard-pm1 · `∏pi>m` crt ·
linear franklin-reiter · `gcd(e,phi)>1` eth-root · held factor-from-d/rsa-decrypt.

## The verify

`pow(m,e,n)==c` / `p*q==n` / `pow(c,d,n)==m` / `1<p<n`,`p|n`.

## The record

`post-probe` on every confirm/falsify · `classify_solve.py --chain <id>` after
a solve · `knowledge/attempts/` for a dead end · `../field-notes.md` (skill root).
