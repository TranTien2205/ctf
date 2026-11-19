# First hour — the RSA solve, the plan

- **0–10**: `crypto_attack.py list`; parse `n`,`e`,`c`; read `keygen.py`; the sheet.
- **10–20**: the discriminator — `attack-table.md` first yes → the id.
- **20–35**: the cheap probes — `fermat`, `batch-gcd`, `small-e`, `common-modulus`,
  `pollard`, `wiener`. A hit → `rsa-decrypt` → `pow` → done.
- **35–55**: the lattice — `boneh-durfee`/`coppersmith`. The bound is the
  falsifier; pure-python LLL is slow — budget, not retry.
- **55–60**: verify + record — `pow`/`p*q`; `solved/` or `knowledge/attempts/`.

Stop rule: 5 probes in one family with no new signal → change the row. See
`first-hour-deep.md`.
