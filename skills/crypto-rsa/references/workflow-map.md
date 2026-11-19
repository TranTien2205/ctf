# Workflow map — the phase → the file → the command

| Phase | The file | The command |
|---|---|---|
| extract | `parameter-sheet*.md`,`recon-order*.md`,`detection*` | `RSA.importKey`,`re.findall`,`crypto_attack.py list` |
| discriminate | `attack-table*.md`,`decision-*`,`detection-matrix*`,`detection-catalogue*` | the first-yes row |
| bound-check | `per-bound.md`,`lattice-bounds.md`,`falsifiers*`,`boundary-cases*` | the falsifier |
| attack | `workflow*.md`,`payload-*`,`per-attack-*`,`probe-*` | `crypto_attack.py <id>` |
| chain | `multi-step-chains*.md` | `factor-from-d`/`rsa-decrypt`/etc |
| verify | `verify*`,`evidence-*`,`checklist*` | `pow(m,e,n)==c`/`p*q==n` |
| record | `evidence-*`,`solved/` | `post-probe`,`classify_solve.py` |
| escalate | `tools/decide.py` | `chain_match`,`reclassify`,`writeup_search`,`novel_plan`,`fanout_sweep`,`solver_handoff` |

## The indexes

`README*.md`,`index.md`,`map-index.md`,`mechanism-index.md`,`detection-index*`,
`summary-map.md`,`summary-index.md`,`closing-index.md`,`field-notes-deep.md`.
