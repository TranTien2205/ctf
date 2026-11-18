# Evidence rules — the CSRF proof standard

CSRF is a DELIVERY primitive — the proof is the state change, not
the request reaching the server. The repository's rules apply with
delivery-specific teeth.

---

## 1. The confirms bar

```text
a `confirms` verdict on web-csrf needs the ATTRIBUTABLE state change
read from a live response — not:
- "the request returned 200" (delivery ≠ write)
- "the bot visited my page" (load ≠ write)
- "the endpoint exists" (reachability ≠ effect)
- a flag-shaped string guessed from source (static ≠ live)
```

The evidence is the before/after delta on the object the write
touched — read by a separate request you control.

## 2. The response-substring rule

```bash
python3 tools/hooks.py post-probe <c> --verdict confirms \
  --hypothesis-id <H> --class web-csrf --evidence-kind impact \
  --evidence 'bio field now contains csrf-marker-7f3a' \
  --response 'the response body the marker was read from'
```

`--evidence` must be a substring of `--response` — the gate checks
the quote is IN the response, not retyped. `tools/web/http_probe.py`
holds request and response together and emits the whole command.

## 3. The candidate-vs-confirm split

```text
candidate  — a token-strip replay ACCEPTED, a foreign-Origin replay
             accepted, a SameSite=missing cookie — these SIGNAL a
             delivery may work. they're candidates, not confirms.
confirms   — the actual write landed and you read the state change.
```

A token-strip that returns 200 is a CANDIDATE — it proves the token
isn't enforced, not that a browser delivery fires. The browser
delivery + state readback is the confirm.

## 4. The attribution requirement

```text
on a shared instance another team's CSRF might change the state.
the unique marker is the attribution:
- a nonce only your payload produces: 'csrf-9f2ab1-mine'
- not 'admin'/'1'/'test' that anyone writes
- the marker's value ties the state change to YOUR delivery
```

## 5. The refutes bar — a gate that held

```text
a `refutes` verdict names the gate that closed:
- 'token required and session-bound — replay failed'
- 'SameSite=Strict on the only credential — no cross-site attach'
- 'content-type whitelisted to application/json — text/plain 415'
each refutes needs the response showing the gate's answer.
```

```bash
python3 tools/hooks.py post-probe <c> --verdict refutes \
  --hypothesis-id <H> --class web-csrf --evidence-kind class \
  --evidence 'CSRF token mismatch — 403' \
  --response 'the 403 body'
```

## 6. The inconclusive bar — couldn't decide

```text
- the bot visited but no state change AND no clear gate refusal —
  inconclusive (could be a slow oracle, a partial write, a missed
  field)
- the delivery fired but the oracle read is ambiguous — inconclusive
a timeout on the readback is NEVER a confirm.
```

## 7. The flag rule

```text
a flag counts only when read from a live response or supplied
artifact AND passed through hooks.py pre-flag:
python3 tools/hooks.py pre-flag --value 'HTB{...}' \
  --source 'GET /api/me' --evidence '<the response>'
a flag-shaped string in source, a guess, or a 'the write probably
worked' is NOT a flag — it's a candidate.
```

## 8. The delivery ≠ write rule

```text
the most common false-confirm: 'the form submitted' is delivery.
the write is the STATE CHANGE on the target. prove the state:
- read the object after — the marker present
- read a list/stats — the record present
- read a balance/count — the delta
- read the flag in its new home — the extraction
```

## 9. The negative-result recording

```text
every gate that held, every failed delivery, every inert write —
record it:
python3 tools/state.py <c> --hypothesis "refutes: token-bound"
the kill-map of what's closed is as valuable as the open path —
it prevents re-walking the same dead gates.
```

## 10. The falsifier statement

```text
the class falsifier, explicitly: 'the endpoint requires a token the
attacker page cannot read, or a content type a cross-origin form
cannot produce — and no stored-content or sibling-route vector
exists'. when that's measured true, record refutes and stop; the
class is done for this endpoint.
```

## 11. The provenance note

```text
when a chain card or a writeup supplied the shape — record the
source: 'the text/plain JSON shape from htb-tornadoservice card'
or 'the SSO cookie-swap from htb-ssos card'. provenance matters —
a verified chain's mechanism transfers; an unverified guess doesn't.
```

## 12. The ledger template

```bash
# candidate
python3 tools/state.py <c> --hypothesis \
  "candidate: token-strip accepted on POST /x"

# confirms
python3 tools/hooks.py post-probe <c> --verdict confirms \
  --hypothesis-id <H> --class web-csrf --evidence-kind impact \
  --evidence 'marker present' --response '<body>'

# refutes
python3 tools/hooks.py post-probe <c> --verdict refutes \
  --hypothesis-id <H> --class web-csrf --evidence-kind class \
  --evidence 'token session-bound' --response '<403 body>'

# flag
python3 tools/hooks.py pre-flag --value 'FLAG{...}' \
  --source 'GET /api/me' --evidence '<body>'
```
