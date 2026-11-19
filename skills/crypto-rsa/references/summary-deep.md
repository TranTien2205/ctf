# Summary deep — the class, the procedure, the honest status

## The class

RSA key or plaintext recovery. `n`,`e`,`c` + a leak → `p`,`q`,`d`,`φ`,`m`. The
violation is in one of six places — wrap, gap, divisor, exponent, partial,
relation/leak.

## The procedure

`crypto_attack.py list` → extract `n`,`e`,`c` + the counts + the leak + the
keygen → the signal → the bound (falsifier) → `crypto_attack.py <id>` →
`pow(m,e,n)==c`/`p*q==n`.

## The attacks

`fermat` (gap) · `wiener`,`boneh-durfee` (small `d`) · `batch-gcd`,
`pollard-pm1` (divisor) · `common-modulus` (Bezout) · `small-e-root`,
`nth-root`,`hastad` (wrap) · `coppersmith-*` (partial) · `franklin-reiter`,
`crt` (relation) · `factor-from-d`,`rsa-decrypt`,`eth-root` (leak).

## The bounds

`d<n^0.25`/`n^0.292` · window `n^0.25`/`n^(1/e)` · `m^e<n` · `≥e` n's · `gcd=1` ·
`|p-q|` small · `B`≥factor · `∏pi>m` · linear · `gcd(e,phi)>1` · the value held.

## The verify

`pow(m,e,n)==c` / `p*q==n` / `pow(c,d,n)==m` / `1<p<n`,`p|n`.

## The honest status

**Catalogue** — no local solve. `../field-notes.md` (skill root) is where real
solves land.
