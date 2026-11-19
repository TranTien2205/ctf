# Workflow catalogue — the procedures, the commands, the files

## The discriminate procedure

1. `crypto_attack.py list` — ids + `lll_backend`.
2. `parameter-sheet.md` — `n`,`e`,`c`,counts,`e_sig`,leak,keygen,degenerate.
3. `attack-table.md` — the first-yes row.
4. `per-bound.md` — the falsifier.

## The cheap-attack procedure

`fermat --n` → `batch-gcd --moduli` → `small-e-root --n --e --c` →
`common-modulus --n --e1 --c1 --e2 --c2` → `pollard-pm1 --n --b` →
`wiener --n --e` → `crt --residues --moduli` → `hastad --pairs --e` →
`factor-from-d --n --e --d` → `rsa-decrypt --n --e --c --p --q` →
`eth-root --c --e --factors`.

## The lattice procedure

`boneh-durfee --n --e [--delta --m --t]` → `boneh-durfee-escalate --m --t` →
`coppersmith-high-bits --n --known --bits` → `coppersmith-core --n --a --X`.

## The manual procedure

`tools/crypto/franklin_reiter.py` (`franklin-reiter`) · `crt` Bellcore `gcd` ·
`crt` `dp`/`qInv` loop.

## The verify procedure

`pow(m,e,n)==c` / `p*q==n` / `pow(c,d,n)==m` / `1<p<n`&`p|n` /
`n-phi+1==p+q` / `pow(m_i,e,n)==c`+format.

## The record procedure

`post-probe --hypothesis-id --class --verdict --evidence-kind --evidence
--response` · `classify_solve.py --chain <id>` · `knowledge/attempts/` ·
`../field-notes.md`.
