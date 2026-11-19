# Field notes index — the record components → the files

## The record components

| Component | The files |
|---|---|
| `hypothesis-id` | `field-notes-catalogue.md` |
| `class`/`impact` | `evidence*.md` |
| the `ct`+`cipher_id` tuple | `evidence*.md`,`detection*.md` |
| the `pt`+`key`/`k`/`σ`/`π` | `payload-dictionary*.md`,`field-notes-catalogue.md` |
| `enc(pt)=ct` | `verify*.md` |
| the `flag` | `evidence*.md` |
| the fail-record | `negative-*.md`,`field-notes-catalogue.md` |
| the chain card | `LEARNING_LOOP`,`classify_solve.py` |

## The record files

`../field-notes.md` (skill root), `field-notes-catalogue.md`, `verify*.md`,
`evidence*.md`, `negative-*.md`, `checklist*.md`.

## The record commands

`post-probe` (the ledger) · `classify_solve.py` (the chain card) ·
`decide.py` (the next).

## The record checklist — `field-notes-catalogue.md`

- [ ] the `ct` bytes recorded.
- [ ] `cipher_id --text` run; the tuple recorded.
- [ ] `classical_solve` run; the `pt` + parameter recorded.
- [ ] `enc(pt)=ct` verified.
- [ ] `flag{`/`CTF{` present.
- [ ] `post-probe` run (the ledger).
- [ ] a fail → `knowledge/attempts/` falsifier.
- [ ] a solve → `classify_solve.py`.
