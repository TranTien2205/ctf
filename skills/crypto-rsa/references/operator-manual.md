# Operator manual — the complete field reference

## The one-liner

`crypto_attack.py list` → `parameter-sheet.md` → `attack-table.md` →
`per-bound.md` → `crypto_attack.py <id>` → `verify.md` → `../field-notes.md`.

## The six primitives

Wrap (small `e`,`m^e<n`) → `small-e-root`/`nth-root`/`hastad` · Gap (close
`p,q`) → `fermat` · Divisor (shared/smooth `p`) → `batch-gcd`/`pollard-pm1` ·
Exponent (`ed≡1` leaks `d`) → `wiener`/`boneh-durfee`/`common-modulus`/
`factor-from-d` · Partial (bits) → `coppersmith-*` · Relation/leak
(`a·m1+b`/`sig`/`dp`/`gcd(e,phi)>1`) → `franklin-reiter`/`crt`/`rsa-decrypt`/
`eth-root`.

## The bounds

`d<n^0.25` wiener · `d<n^0.292` boneh-durfee · window `n^0.25`/`n^(1/e)`
coppersmith · `m^e<n` small-e/nth-root · `≥e` n's hastad · `gcd=1`
common-modulus · `|p-q|` fermat · `B`≥factor pollard-pm1 · `∏pi>m` crt ·
linear franklin-reiter · `gcd(e,phi)>1` eth-root · held factor-from-d/rsa-decrypt.

## The verify

`pow(m,e,n)==c` / `p*q==n` / `pow(c,d,n)==m` / `1<p<n`,`p|n` /
`n-phi+1==p+q` / `pow(m_i,e,n)==c`+format.

## The record

`post-probe --hypothesis-id --class --verdict --evidence-kind --evidence
--response` · `classify_solve.py --chain <id>` · `knowledge/attempts/` ·
`../field-notes.md` · `decide.py` for the budget/escalation.

## The honest status

Catalogue — no local solve. `../field-notes.md` grows with real solves.
