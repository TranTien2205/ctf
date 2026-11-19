# Workflow checklist — the printable business-logic engagement

One page. Tick each row; every row either produces verbatim evidence or
a recorded negative/falsifier.

## Setup

- [ ] `python3 selfcheck.py` — green before anything
- [ ] `python3 tools/state.py <name> --category web --target <url>
      --challenge-name "<real>" --event "<event>"`
- [ ] `python3 tools/classify.py "<obs>"` — class named
- [ ] `python3 tools/chain_match.py --record <name>` (source) or on
      signals — candidates read, not trusted

## Recon

- [ ] `bundle_miner` on the JS → `endpoints.txt`, `secrets.txt`
- [ ] happy-path baseline saved: register → cart → checkout → order
- [ ] `GET` on the primary object → field map written down

## Mechanism sweep (one probe each, falsifier attached)

- [ ] mass assignment: `register`/`update` + `role=admin`
      → falsifier: `role: user` on read-back
- [ ] workflow skip: `/confirm` (or terminal) without earlier steps
      → falsifier: `302/400` to required step
- [ ] state replay: redeem/claim twice serially
      → falsifier: `409` second time
- [ ] numeric boundary: `-1`, `0`, `NaN`, `1e309`, `0x10` per numeric field
      → falsifier: `400`/clamp per row
- [ ] scaling-after-check: `id` at limit, limit+1, word wraps
      → falsifier: identical rejection to malformed id
- [ ] unit confusion: value in the "other" unit
      → falsifier: canonical normalization
- [ ] idempotency: exact replay with same key/body
      → falsifier: `409`
- [ ] time assumption: past expiry / future notBefore
      → falsifier: `400` on invalid
- [ ] sequence: stale ID replay
      → falsifier: `409`
- [ ] ownership: foreign `objectId` in operation
      → falsifier: `403` (route to IDOR)
- [ ] singleton: second privileged object
      → falsifier: `409`
- [ ] trust-in-earlier-step: mutated upstream value downstream
      → falsifier: server recomputes / `400 mismatch`

## Evidence

- [ ] every probe has a baseline pair
- [ ] every verdict went through `post-probe` with `--response` attached
- [ ] falsifiers recorded as `falsified`, not silently skipped
- [ ] negatives recorded with the variable that changed

## Closure

- [ ] flag through `pre-flag` against a live response
- [ ] `classify_solve.py --chain <id>` files the solve
- [ ] ../field-notes.md appended (proposed entries)
- [ ] or: budget spent → `decide.py` → escalation rung, not a sixth
      spelling variant
