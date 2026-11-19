# Quick reference — the race-condition cheat sheet

The one-page cheat sheet: the class, the contract, the probe, the evidence,
the record. The fastest orientation for a live engagement.

---

## The class

`web-race-condition` — a race condition / TOCTOU: a read-modify-write or
check-then-act whose read and write are separated, and two requests can
overlap inside that window.

**Confusable** — `web-logic-flaw` (the check itself is wrong, no timing needed).

**Verified by** — 2 chain cards: ApexSurvive (token race → XSS → template
overwrite → RCE) and SSOS (registration race → cookie-swap → flag-submit).

**Stuck threshold** — 3. **First probe** — two interleaved requests, not a flood.

## The contract

- A flag counts only from a live response — not a crossed state, not a status.
- A serial baseline **first** — a signature that appears serially is not a race.
- `max_in_flight = 1` → inconclusive — fix delivery, re-roll.
- `max_in_flight ≥ 2` + the crossed state → confirms — attribute, verify, record.
- Race only resources you own — never the shared/demo object.
- A one-shot target already used → stop — unrecoverable.

## The probe

```bash
# baseline first
python3 tools/web/race_probe.py --url "$BASE/api/<ep>" \
  --method POST --body '<b>' -H 'Cookie: <s>' \
  --baseline-count 5 --count 0 --no-barrier --challenge <name>

# then the raced run
python3 tools/web/race_probe.py --url "$BASE/api/<ep>" \
  --method POST --body '<b>' -H 'Cookie: <s>' \
  --concurrency N --count N --baseline-count 5 \
  --signature-mode <m> --write-ack --challenge <name>
```

## The two-request form

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/<ep-a>"  --method POST --body '<b-a>' -H 'Cookie: <s>' \
  --url-b "$BASE/<ep-b>" --method-b POST --body-b '<b-b>' \
  --concurrency 2 --count 10 --baseline-count 4 \
  --signature-mode normalized-body --write-ack --challenge <name>
```

## The evidence

- the **baseline split** (the serial set)
- the **raced split** (the concurrent set)
- **`max_in_flight`** (the real overlap)
- the **state read** (the crossed state — read the state, not the status)
- the **attributed pair** (which two requests committed inside the window)

## The record

```bash
python3 tools/hooks.py post-probe <name> --class web-race-condition \
  --hypothesis-id <h> --verdict confirms --evidence-kind impact \
  --evidence "raced [200×2,409×18] vs baseline [200,409×4], max_in_flight=20; GET /api/account balance=-100" \
  --response "<the tool output + the state read>"
```

## The decision

```text
max_in_flight = 1         → inconclusive — fix delivery, re-roll
real overlap + cross      → confirms — attribute, verify, record
real overlap, all-loser   → falsifier — record, move endpoint
429/403 dominant          → throttled — race the limiter or interleave
timeout on a slot         → unknown — discard, re-roll
IntegrityError on loser   → falsifier — the constraint fired
```

## The references

`README.md` — the index: mechanism, detection, per-check, per-framework,
exploitation, evidence, falsifiers, edge cases, the two verified cards.
