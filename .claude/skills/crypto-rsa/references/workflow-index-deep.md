# Workflow index deep — the phase → the files → the command

## Phase 0 — extract

`parameter-sheet.md`, `detection.md`, `detection-deep.md`,
`detection-checklist*.md`, `recon-order.md`, `probe-catalogue.md`, `probe-map.md`.
`crypto_attack.py list` — the inventory + bounds. `RSA.importKey` on the keys.

## Phase 1 — discriminate

`attack-table.md`, `attack-table-deep.md`, `decision-table.md`,
`decision-catalogue.md`, `detection-matrix.md`, `detection-catalogue.md`,
`per-signal.md`, `per-condition.md`, `per-check.md`, `per-parameter.md`,
`per-attack.md`, `per-mechanism.md`, `per-class.md`, `per-target.md`,
`per-form.md`, `per-channel.md`, `per-endpoint.md`, `per-vector.md`.

## Phase 2 — bound-check

`per-bound.md`, `lattice-bounds.md`, `boundary-cases*.md`, `falsifiers.md`,
`falsifier-map.md`, `per-falsifier.md`, `per-boundary.md`, `negative-results.md`,
`negative-map.md`.

## Phase 3 — attack

`workflow*.md`, `first-hour*.md`, `field-manual*.md`, `operator-notes.md`,
`exploitation*.md`, `multi-step-chains.md`, `payload-*.md`, `probe-*.md`,
`per-attack-*.md` + `-deep` + stub.

`crypto_attack.py <id> <flags>` — `<id> --help` for the args.

## Phase 4 — verify

`verify.md`, `verification-protocol.md`, `evidence-*.md`, `checklist*.md`.
`pow(m,e,n)==c` / `p*q==n` / `pow(c,d,n)==m`.

## Phase 5 — record / escalate

`solved/` + `classify_solve.py --chain <id>` · `knowledge/attempts/` for a dead
end · `../field-notes.md` · `hooks.py post-probe --hypothesis-id --class --verdict
--evidence-kind --evidence --response`.

`tools/decide.py` owns the budget — `escalate` → `chain_match`, `reclassify`,
`writeup_search`, `novel_plan`, `fanout_sweep`, `solver_handoff`.

## The indexes

`README.md`, `README-deep.md`, `index.md`, `map-index.md`, `mechanism-index.md`,
`detection-index.md`, `detection-index-deep.md`, `summary-map.md`,
`summary-index.md`, `closing-index.md`, `field-notes-deep.md`.
