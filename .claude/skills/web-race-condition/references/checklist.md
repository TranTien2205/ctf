# Checklist — the printable race-condition checklist

The one-page checklist for a race-condition engagement — print it, work it in
order, mark each line.

---

## 0 — Contract

- [ ] reachable target + owned object + fresh one-shot + `--write-ack`
- [ ] `python3 tools/web/race_probe.py --selftest` → PASS

## 1 — Inventory

- [ ] every writable endpoint listed (bundle + source grep)
- [ ] ranked: money → token → account → limit → vote → counter

## 2 — Window

- [ ] read → work → write on the same record identified
- [ ] the check letter named (A uniqueness / B balance / C single-use / D limit /
      F file / G claim / H inventory / L counter / S session / V trusted-view)

## 3 — Defence / falsifier

- [ ] `FOR UPDATE`/`select_for_update`/`PESSIMISTIC` grep → not found
- [ ] `UNIQUE`/`CHECK`/PK on the raced field → not found
- [ ] `SERIALIZABLE` + retry → not found
- [ ] `version` in `WHERE` → not found
- [ ] `findOneAndUpdate`/atomic → not found
- [ ] `pg_advisory`/`GET_LOCK` → not found
- [ ] `SKIP LOCKED`/idempotent → not found
- [ ] single worker + private DB → not the case
- [ ] transaction alone → not a falsifier; proceed

## 4 — Baseline

- [ ] `--baseline-count 5 --count 0 --no-barrier` → the serial set recorded
- [ ] the serial "win" shape noted (if the serial set shows the win — not a race)

## 5 — The raced run

- [ ] `--concurrency N --count N --baseline-count 5 --signature-mode <m> --write-ack`
- [ ] `--url-b` for the two-different-request case
- [ ] the last-byte stall for the narrow-window case

## 6 — Read `max_in_flight`

- [ ] `= 1` → inconclusive — fix delivery, re-roll
- [ ] `≥ 2` → real overlap — the result is meaningful
- [ ] `< requested` → partial — usable if the cross appears

## 7 — The state read

- [ ] the crossed state read from `/api/<state-endpoint>` — not the status
- [ ] the doubled/impossible value recorded (the balance, the count, the two cookies)

## 8 — Attribute the pair

- [ ] the per-slot split names which two requests committed inside the window
- [ ] if you can't name them → lower `--concurrency`, re-roll

## 9 — Verify the effect pays

- [ ] the primitive → the gate → the flag (the buy, the login, the order, the verified)
- [ ] the flag is read from a live response — not the crossed state

## 10 — Record

- [ ] `hooks.py post-probe --verdict confirms --evidence-kind impact`
- [ ] `--evidence` = baseline split + raced split + `max_in_flight` + state read
- [ ] `--response` = the verbatim tool output + the state read

## 11 — Re-roll / abort

- [ ] `--reset-url`/`--reset-body` restores the state between rolls
- [ ] `max_in_flight` can't exceed 1 → the layer can't overlap — race the DB/worker layer
- [ ] 3 clean real-overlap no-cross → falsifier — move endpoint
- [ ] a one-shot target used → stop — unrecoverable
- [ ] budget out → `decide.py` escalate; `--strategy-used` per rung

## 12 — The chain

- [ ] the primitive → the sink class recorded (`web-xss`/`web-ssti`/`web-csrf`/`web-auth-session`/`web-idor`/`web-logic-flaw`)
- [ ] both classes in the solve — the race is the primitive, the sink carries the flag
