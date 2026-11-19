# Summary index — crypto-rsa at a glance

## The class

RSA key or plaintext recovery — `n`,`e`,`c` + a leak → `p`,`q`,`d`,`φ`,`m`.
Six violation families: wrap, gap, divisor, exponent, partial, relation/leak.

## The procedure

`parameter-sheet.md` → `attack-table.md` → `per-bound.md` → `crypto_attack.py <id>` → `verify.md` → `../field-notes.md`.

## The attacks, one line each

- `batch-gcd` — `gcd(ni,nj)` for a shared `p`.
- `common-modulus` — `m=c1^a·c2^b`, `gcd(e1,e2)=1`.
- `fermat` — `n=a²-b²` for close `p,q`.
- `wiener` — `d<n^0.25` → CF convergent.
- `boneh-durfee` — `d<n^0.292` → LLL.
- `coppersmith-*` — `p`/`m` bits → small-root.
- `small-e-root`/`nth-root` — `m=c^{1/e}`, `m^e<n`.
- `hastad` — CRT + root over `e` n's.
- `pollard-pm1` — `gcd(a^{B!}-1,n)`.
- `franklin-reiter` — `gcd` of related polys (manual/`franklin_reiter.py`).
- `crt` — residues / Bellcore / dp.
- `factor-from-d`/`rsa-decrypt`/`eth-root` — the leaks.

## The verify

`pow(m,e,n)==c` / `p*q==n`.

## The honest status

**Catalogue** — no local solve. `../field-notes.md` (skill root) grows with real
solves.
