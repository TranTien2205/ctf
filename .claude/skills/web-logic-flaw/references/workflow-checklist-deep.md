# Workflow checklist deep — the engagement checklist with response-reading per row

`workflow-checklist.md` is printable. This module is the same rows with
the response-reading rules — what each checkbox's result means.

## Setup rows

- `selfcheck.py` green → any FAIL is a broken gate — fix before
  evidence can be recorded at all.
- `state.py` init → the ledger exists or `post-probe` refuses writes.
- `classify.py` → the candidate class; a different class winning means
  this skill may not be the route — re-read the signals.
- `chain_match.py` → a literal-signal match runs the card's probe
  verbatim; a `family_leads` hit is READ-ONLY context.

## Recon rows

- `bundle_miner` → `endpoints.txt` is the edge list. Missing the
  bundle? The endpoint list comes from the crawl + devtools XHR log.
- baseline saved → every response file `b_*.txt` — the diffs need them.
- field map → the GET response's keys ARE the mass-assignment target
  list — any key not on the form is a probe.

## The 60-second rows — response reading

- `GET /flag` bare: `200`+flag = zero-step skip CONFIRM. `403`/`302` =
  it checks something — find what.
- `GET /admin` bare: `200` = either no gate or a default-privileged
  session — check `role` on the current object.
- `POST /register role=admin`: read-back decides — echo is not store.
- Terminal step bare: `200`+forbidden pair = CONFIRM; `302` = enforced;
  `200`+unchanged = soft no-op.

## The sweep rows — per-mechanism reading

- mass assignment nested/array/content-type rows: each is a different
  code path — one falsifier doesn't kill the siblings.
- boundary rows: `400` per row = validator; `200`+forbidden = CONFIRM;
  clamped = note the layer.
- replay rows: serial ×2 only — a `409` ends this class's question on
  that endpoint (parallel → race).
- transform rows: the contrast pair (limit+1 vs malformed) — identical
  = falsifier; different = CONFIRM.
- trust rows: minted-vs-accepted pair — `charged:1` vs minted `50` is
  the evidence.

## Evidence rows

- baseline pairs: no verdict without the diff — a lone `balance:200`
  row is unattributable.
- `post-probe` per verdict: `confirms` needs `--evidence` substring-of-
  `--response`; `falsified`/`negative` still want `--response` attached.
- falsifier rows recorded: a falsified shape in the ledger is what
  stops the NEXT session from re-walking it.

## Closure rows

- `pre-flag` against the live response — the flag string must be a
  substring of the response it was read from.
- `classify_solve.py --chain <id>` → the solve lands in the right class
  skill and the card gets its ancestry.
- `decide.py` on a spent alphabet → the escalation rung — `chain_match`
  → `reclassify` → `writeup_search` → `novel_plan` → `fanout_sweep` →
  `solver_handoff` — never a sixth spelling.
- kill map → `knowledge/attempts/<name>.json` — every dead layer with
  its measurement and the precondition that would reopen it.
