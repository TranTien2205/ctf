# Workflow map — the phase → the file → the command

| Phase | The file | The command |
|---|---|---|
| read | `detection*.md`,`cipher-identification.md` | `cipher_id --text` |
| discriminate | `cipher-identification.md`,`detection-matrix.md` | the IC/chi²/Kasiski |
| solve | `payload-dictionary.md` | `classical_solve <family> --text` |
| verify | `evidence.md` | `enc(pt)==ct` |
| record | `../field-notes.md` | `post-probe`,`classify_solve.py` |
| escalate | `tools/decide.py` | the 6 rungs |

## The indexes

`README.md`,`detection-index*.md`,`workflow-index*.md`,`summary*.md`,
`map-index.md`,`closing-index.md`.
