# Checklist index — the run-lists → the files

## The run-lists

| List | The files |
|---|---|
| the detection run | `detection-checklist*.md` |
| the per-family solve | `checklist*.md`,`per-family-*.md` |
| the record | `field-notes-catalogue.md`,`negative-*.md` |
| the verify | `verify*.md`,`evidence*.md` |
| the falsifier | `falsifiers*.md`,`per-falsifier*.md` |

## The detection checklist — `detection-checklist*.md`

- [ ] `enc_detect` first — `+/=`/hex/`01`/`.-` → encoding.
- [ ] `cipher_id --text` — the tuple.
- [ ] `ADFGVX`/`AB`×5/`n=r·c`/name → `other-ciphers`/grid/route.
- [ ] the IC split → mono/poly/`π`.
- [ ] the chi² split → `caesar`/`subst`/`atbash`.
- [ ] the family → `classical_solve`.
- [ ] `pt` language + `enc(pt)=ct` + `flag{` present.
- [ ] record / falsify / escalate.

## The solve checklist — `checklist*.md`

- [ ] the right `classical_solve` family.
- [ ] `--keylen`/`--restarts` tuned.
- [ ] `pt` language (a score is not).
- [ ] `enc(pt)=ct`.
- [ ] `flag{`/`CTF{` present.
- [ ] a fail → the falsifier recorded.

## The record checklist — `field-notes-catalogue.md`

- [ ] the `ct` bytes + the `cipher_id` tuple.
- [ ] the `classical_solve` + `pt` + parameter.
- [ ] `post-probe` (the ledger) · `classify_solve.py` (the card).
- [ ] a fail → `knowledge/attempts/`.
