# Workflow index — the phase → the file

| Phase | The file |
|---|---|
| extract | `parameter-sheet*`,`detection*`,`recon-order*`,`probe-*` |
| discriminate | `attack-table*`,`decision-*`,`detection-matrix*`,`detection-catalogue*` |
| bound-check | `per-bound.md`,`lattice-bounds.md`,`falsifiers*`,`boundary-cases*` |
| attack | `workflow*`,`payload-*`,`per-attack-*`,`probe-*` |
| chain | `multi-step-chains*` |
| verify | `verify*`,`evidence-*`,`checklist*` |
| record | `evidence-*`,`solved/`,`field-notes*` |
| escalate | `tools/decide.py` — the 6 rungs |

## The indexes

`README*.md`,`index.md`,`map-index.md`,`mechanism-index.md`,`detection-index*`,
`summary-*`,`closing-index.md`,`field-notes-deep.md`,`workflow-index.md`,
`workflow-map.md`,`workflow-catalogue.md`,`workflow-playbook*`.

## The order

`crypto_attack.py list` → `parameter-sheet` → `attack-table` → `per-bound` →
`crypto_attack.py <id>` → `verify` → `field-notes`.
