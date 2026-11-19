# Detection checklist — the full CORS detection sweep

A step-by-step checklist that takes a target from 'unknown CORS
posture' to a measured verdict.

---

## Phase 1 — the endpoint inventory

```bash
# the API endpoints that carry session data
for ep in /api/me /api/user /api/profile /api/flag /api/token \
          /api/admin /api/account /api/balance /api/config \
          /api/data /api/secret /api/key /api/session /api/info \
          /me /profile /flag /admin /dashboard /api/settings; do
  code=$(curl -s -o /dev/null -w '%{http_code}' -b "$CJ" "$BASE$ep")
  [ "$code" != "404" ] && echo "$ep => $code"
done
```

```bash
# the front-end's own cross-origin calls — the app's API surface
curl -s "$BASE/" | grep -oE '(fetch|axios|XMLHttpRequest)\([^)]*\)|/api/[a-z_/-]+' | sort -u | head -20
```

## Phase 2 — the ACAO measurement per endpoint

```bash
for ep in /api/me /api/flag /api/token; do
  echo "=== $ep ==="
  curl -s -i -b "$CJ" "$BASE$ep" -H 'Origin: https://evil.com' | \
    grep -iE 'access-control-(allow-origin|allow-credentials)|vary'
done
```

## Phase 3 — the check-shape battery

```bash
TD=$(echo "$BASE" | sed -E 's#https?://([^/:]+).*#\1#')
for o in 'https://evil.com' 'null' \
         "https://${TD}.evil.com" "https://evil${TD}" \
         "https://evil-${TD}" "https://sub.${TD}" \
         "https://${TD}@evil.com" "https://evil.com?${TD}" \
         "https://${TD}%2eevil.com" "https://${TD}." \
         "http://${TD}" 'file://' 'data:text/html,'; do
  echo -n "$o => "
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin' || echo 'no ACAO'
done
```

## Phase 4 — the credential gate

```bash
# ACAC — does the response allow credentials
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -i 'access-control-allow-credentials'

# the session cookie's SameSite — does it ride a cross-site fetch
curl -s -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
```

## Phase 5 — the preflight

```bash
# a non-simple request's preflight
curl -i -X OPTIONS "$BASE/api/me" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: X-Token'
# the ACAO/ACAM/ACAH on the preflight
```

## Phase 6 — the cache check

```bash
# the response's cache headers — a per-origin or shared response
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://a.com' | \
  grep -iE 'vary|cache-control|age|cf-|x-cache'
```

## Phase 7 — the alternate-read check

```bash
# a JSONP endpoint — the callback param
curl -s -b "$CJ" "$BASE/api/me?callback=x" | head -1
#   x({...}) → JSONP — a script-tag read

# a ws endpoint
curl -s -i -N -H 'Connection: Upgrade' -H 'Upgrade: websocket' \
  -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: x' \
  -b "$CJ" "$BASE/ws" | head -5
```

## Phase 8 — the verdict synthesis

```text
record the measurement:
- ACAO: <reflected|*|null|fixed|absent>
- ACAC: <true|absent>
- cookie-SameSite: <None|Lax|Strict>
- check-shape: <reflect|null|prefix|suffix|substring|subdomain|strict>
- preflight: <permissive|strict>
- cache: <vary|no-vary>
- alternate-read: <jsonp|ws|none>
→ the verdict: the read's exploitability
```

## The detection-report template

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-detect: /api/<ep> — ACAO=<v> ACAC=<t/f> SameSite=<v> shape=<s>"
```
