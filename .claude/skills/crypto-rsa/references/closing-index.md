# Closing index — crypto-rsa, the final index

## The class

RSA key or plaintext recovery — `n`,`e`,`c` + a leak → `p`,`q`,`d`,`φ`,`m`.
Six violation families: wrap, gap, divisor, exponent, partial, relation/leak.

## The procedure

`crypto_attack.py list` → `parameter-sheet.md` → `attack-table.md` →
`per-bound.md` → `crypto_attack.py <id>` → `verify.md` → `../field-notes.md`.

## The attacks

`fermat` · `wiener`,`boneh-durfee` · `batch-gcd`,`pollard-pm1` ·
`common-modulus` · `small-e-root`,`nth-root`,`hastad` · `coppersmith-*` ·
`franklin-reiter`,`crt` · `factor-from-d`,`rsa-decrypt`,`eth-root`.

## The bounds

`d<n^0.25`/`n^0.292` · window `n^0.25`/`n^(1/e)` · `m^e<n` · `≥e` n's · `gcd=1`
· `|p-q|` small · `B`≥factor · `∏pi>m` · linear · `gcd(e,phi)>1` · held.

## The verify

`pow(m,e,n)==c` / `p*q==n` / `pow(c,d,n)==m` / `1<p<n`,`p|n`.

## The honest status

**Catalogue** — no local solve. `../field-notes.md` (skill root) is where real
solves land.
