# Workflow — the RSA solve

`parameter-sheet.md` → `attack-table.md` discriminator → `per-bound.md`
bound-check → `crypto_attack.py <id>` → `verify.md` → record.

1. **extract** — parse `n`,`e`,`c`,the leak,the keygen → the sheet.
2. **discriminate** — `attack-table.md` first yes picks the id.
3. **bound-check** — `per-bound.md`/`lattice-bounds.md` — the falsifier.
4. **attack** — `crypto_attack.py <id> <flags>` — cheap first, lattice last.
5. **verify** — `pow(m,e,n)==c` / `p*q==n`.
6. **record** — `solved/` + `classify_solve.py` or `knowledge/attempts/`.

The loop: 5 probes / 15 min per family → change the row; a bound exceeded →
record, escalate; every bound met → `class-boundary.md`. See `workflow-deep.md`,
`workflow-map.md`, `workflow-index.md`, `workflow-playbook.md`.
