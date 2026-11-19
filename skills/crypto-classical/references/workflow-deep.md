# Workflow deep — the procedures, annotated

## Phase 0 — the reads

`cipher_id.py --text 'CT'` — IC/chi²/Kasiski/frequency/verdict. The charset —
cipher vs encoding. A name in the text. `flag{`/`CTF{` positions. The length —
a grid/route shape.

## Phase 1 — the discriminate

`cipher-identification.md` — the IC × chi² × Kasiski table → the family.

## Phase 2 — the solve

`classical_solve <family> --text [--keylen|--key|--restarts]` — the mechanical
half. For a named cipher not in the tool — a script/dcode.fr.

## Phase 3 — the verify

`pt` language → `enc(pt)==ct` → `flag{`/`CTF{` → the flag.

## Phase 4 — the record / escalate

`post-probe` · `classify_solve.py` · `../field-notes.md` · `decide.py` for the
budget — `chain_match`, `reclassify`, `writeup_search`, `novel_plan`,
`fanout_sweep`, `solver_handoff`.

## The falsifier-first rule

The bound *before* the solve — no `k`/`L`/language → the family closes; don't
re-run.
