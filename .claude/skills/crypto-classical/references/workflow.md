# Workflow — the procedures, ordered

## Phase 0 — the reads

```bash
python3 tools/cipher_id.py --text 'CT'
```

- the charset — letters-only vs `+/=`/hex/`01`/`.-` (`enc_detect`)
- the IC / chi² / Kasiski / frequency
- a cipher name in the challenge text
- `flag{`/`CTF{`/`SNT{` positions — the format leak
- the length — a grid/route shape (`n = r·c`)

## Phase 1 — the discriminate

`cipher-identification.md` — the (IC × chi² × Kasiski × charset) tuple → the
family.

## Phase 2 — the solve

```bash
python3 tools/classical_solve.py <family> --text 'CT' [--keylen|--key|--restarts|--iters]
```

`payload-dictionary.md` for the flag set. For a named cipher not in the tool —
a script / dcode.fr.

## Phase 3 — the verify

`pt` language → `enc(pt)==ct` → `flag{`/`CTF{` present → the flag.

## Phase 4 — the record / escalate

- `post-probe --hypothesis-id --class --verdict --evidence-kind --evidence --response`
- `classify_solve.py --chain <id>` — the solve into the class
- `../field-notes.md` — the skill's own notes
- `decide.py` — the budget; the 6-rung escalate — `chain_match`, `reclassify`,
  `writeup_search`, `novel_plan`, `fanout_sweep`, `solver_handoff`

## The falsifier-first rule

The bound *before* the solve — no `k`/`L`/language → the family closes; don't
re-run. The charset first — `enc_detect` before the cipher statistics.
