# First hour deep — the RSA solve, minute by minute

## 0–10 min — extract

- `python3 tools/crypto_attack.py list` — the inventory + bounds.
- Parse every `n`,`e`,`c`; the bit-lengths; count them.
- Read `keygen.py`/`chal.py` — the comment names the misuse.
- A PEM/DER → `n`,`e` only.
- Fill the `parameter-sheet`.

## 10–20 min — discriminate

- `moduli ≥ 2` → `batch-gcd` / `hastad`.
- `2 e` on `1 n` → `common-modulus`.
- `e≈n` → `wiener`→`boneh-durfee`.
- `e=3`,`m` short → `small-e-root`.
- `p,q` close → `fermat`.
- `p-1` smooth → `pollard-pm1`.
- leak → `factor-from-d`/`crt`/`coppersmith`.
- `m2=a·m1+b` → `franklin-reiter`.
- residues/fault → `crt`.

## 20–35 min — the cheap probes

Run in cost order, fastest first:
- `fermat` — `a=isqrt(n)+1` converges if gap small.
- `batch-gcd` — pairwise `gcd`, instant.
- `small-e-root`/`nth-root` — one `pow`.
- `common-modulus` — one Bezout.
- `pollard-pm1` — bounded `gcd` loop.
- `wiener` — CF convergents, fast.

A hit ends it → `rsa-decrypt` → `pow` verify → done.

## 35–55 min — the lattice

- `boneh-durfee-escalate` for `d` in `0.25–0.292`.
- `coppersmith-high-bits`/`-core` for partial `p`.
- Read the applicability bound — it is the falsifier.
- Pure-python LLL is slow; give it the budget, not a retry.

## 55–60 min — verify + record

- `pow(m,e,n)==c` or `p*q==n` — the gate.
- `solved/<name>/` + `classify_solve.py` + the evidence tuple.
- Dead end → `knowledge/attempts/` with each bound.

## The stop rule

Five probes in one family with no new signal → change the discriminator row.
A bound exceeded → record, don't retry.
