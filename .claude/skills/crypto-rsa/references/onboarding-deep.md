# Onboarding deep — the first-session reads

## The one-liner

`crypto_attack.py list` → `parameter-sheet.md` → `attack-table.md` → the bound
→ `crypto_attack.py <id>` → `verify.md` → `../field-notes.md`.

## The six primitives

Wrap (small `e`,`m^e<n`) → `small-e-root`/`nth-root`/`hastad` · Gap (close
`p,q`) → `fermat` · Divisor (shared/smooth `p`) → `batch-gcd`/`pollard-pm1` ·
Exponent (`ed≡1` leaks `d`) → `wiener`/`boneh-durfee`/`common-modulus`/
`factor-from-d` · Partial (bits) → `coppersmith-*` · Relation/leak
(`a·m1+b`/`sig`/`dp`/`gcd(e,phi)>1`) → `franklin-reiter`/`crt`/`rsa-decrypt`/
`eth-root`.

## The procedure

`list` → extract `n`,`e`,`c`,`counts`,`leak`,`keygen` → the signal → the bound
(falsifier) → `crypto_attack.py <id>` → `pow`/`p*q` verify.

## The honest status

Catalogue — no local solve. `../field-notes.md` grows with real solves.

## The reads, in order

`../SKILL.md` → `attack-table.md` → `per-bound.md` → `workflow.md` → `verify.md`
→ the `per-attack-<id>` for your attack.
