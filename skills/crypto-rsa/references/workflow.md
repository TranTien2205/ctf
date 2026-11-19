# Workflow — the phase procedure

## Phase 0 — extract

`parameter-sheet.md` + `detection.md` + `recon-order.md` — `n`,`e`,`c`,counts,
`e_sig`,leak,keygen,degenerate. `crypto_attack.py list` — the inventory +
`lll_backend`. `RSA.importKey` on the keys.

## Phase 1 — discriminate

`attack-table.md` + `decision-table.md` + `detection-matrix.md` — the
first-yes row.

## Phase 2 — bound-check

`per-bound.md` + `lattice-bounds.md` + `falsifiers.md` — the falsifier read.

## Phase 3 — attack

`workflow-playbook*.md` + `payload-*` + `per-attack-*` + `probe-*` — the
`crypto_attack.py <id>` invocation.

## Phase 4 — verify

`verify.md` + `evidence-*` + `checklist*` — `pow(m,e,n)==c`/`p*q==n`.

## Phase 5 — record / escalate

`solved/` + `classify_solve.py --chain <id>` · `knowledge/attempts/` ·
`../field-notes.md` · `tools/decide.py` for the budget/escalation.
