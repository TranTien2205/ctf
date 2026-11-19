# Workflow deep — the RSA solve, end to end

## Phase 0 — extract

```python
# parse every n,e,c; the bit-lengths; count them
from Crypto.PublicKey import RSA
import re, glob
for f in glob.glob('*'):
    if f.endswith(('.pem','.der','.key','.crt')):
        k=RSA.importKey(open(f,'rb').read()); print(f,k.n.bit_length(),k.e,k.has_private())
```

Fill `parameter-sheet.md`: `n`,`e`,`c` counts, the leak, the keygen.

## Phase 1 — discriminate

`attack-table.md` — first yes picks the id:
- ≥2 moduli → `batch-gcd`/`hastad`
- 2 `e` on 1 `n` → `common-modulus`
- `e`≈`n` → `wiener`→`boneh-durfee`
- `e`=3,`m` short → `small-e-root`
- `p`,`q` close → `fermat`
- `p-1` smooth → `pollard-pm1`
- leak → `factor-from-d`/`crt`/`coppersmith`
- `m2=a·m1+b` → `franklin-reiter`
- residues/fault → `crt`

## Phase 2 — bound-check

Read `per-bound.md`/`lattice-bounds.md` — the bound is the falsifier. A bound
exceeded is a negative result, not a tuning problem.

## Phase 3 — attack

`python3 tools/crypto_attack.py <id> <flags>` — `<id> --help` for the args.
Cheap first: fermat, batch-gcd, small-e, common-modulus, pollard, wiener. The
lattice last: boneh-durfee, coppersmith.

## Phase 4 — verify

`pow(m,e,n)==c` for `m`; `p*q==n` for `p`,`q`; `pow(c,d,n)==m` then
`pow(m,e,n)==c` for `d`. The only proof. Strip a PKCS pad if `m` is a padded
block. For `eth-root` try each `gcd` candidate.

## Phase 5 — record / escalate

`solved/<name>/` + `classify_solve.py` + the evidence tuple
`{sheet,attack,bound,recovered,pow}`. A dead end → `knowledge/attempts/` with
each bound. A spent budget → `tools/decide.py` names the next rung.

## The loop discipline

Five probes in one attack family with no new signal → change the discriminator
row, not the payload variant. A bound exceeded → record, escalate the family.
Every bound on the sheet met → `class-boundary` — the bug isn't in the RSA.
