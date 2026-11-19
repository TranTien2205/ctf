# Detection deep — every way a CORS misconfig surfaces

The detection surface: the black-box probes, the white-box greps,
and the signals that name the check's shape.

---

## 1. The central measurement — the Origin replay

```bash
# the single most important probe — a foreign Origin, credentialed
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com'
# read the ACAO + ACAC together:
#   ACAO: https://evil.com    → reflected
#   ACAO: *                   → public (never credentialed)
#   ACAO: null                → opaque-allowed
#   ACAO: https://app.t.com   → fixed (your origin excluded)
#   no ACAO                   → not CORS-open
#   ACAC: true                → credentialed read allowed
```

## 2. The baseline-vs-foreign comparison — the differential

```bash
# the same endpoint, no Origin vs foreign Origin
curl -s -i -b "$CJ" "$BASE/api/me" | grep -i 'access-control'
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | grep -i 'access-control'
# a foreign Origin that changes the ACAO → a dynamic check → test its shape
```

## 3. The origin-bypass battery — naming the check's shape

```bash
# a battery of Origin values — each tests a check-shape
declare -A SHAPES=(
  ['reflect']='https://evil.com'
  ['null']='null'
  ['suffix']='https://target.com.evil.com'
  ['prefix']='https://eviltarget.com'
  ['substring']='https://evil-target.com'
  ['subdomain']='https://sub.target.com'
  ['userinfo']='https://target.com@evil.com'
  ['query']='https://evil.com?target.com'
  ['encoded-dot']='https://target.com%2eevil.com'
  ['backtick']='https://target.com%60.evil.com'
  ['underscore']='https://target.com_.evil.com'
  ['port']='https://target.com:443'
  ['trailing-dot']='https://target.com.'
  ['scheme']='http://target.com'
)
for k in "${!SHAPES[@]}"; do
  echo -n "$k (${SHAPES[$k]}) -> "
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: ${SHAPES[$k]}" | \
    grep -i 'access-control-allow-origin' || echo 'no ACAO'
done
```

## 4. The credential-gate measurement — ACAC + SameSite

```bash
# ACAC — does the response allow credentials
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -i 'access-control-allow-credentials'

# the session cookie's SameSite — does it ride a cross-site fetch
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
#   SameSite=None; Secure  → attaches → credentialed read works
#   SameSite=Lax/Strict    → doesn't attach → non-credentialed
#   no SameSite            → Lax-by-default → doesn't attach
```

## 5. The preflight measurement — a non-simple read

```bash
# the preflight — does a custom-header request get permission
curl -i -X OPTIONS "$BASE/api/x" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: X-Token'
# read the preflight's ACAO/ACAM/ACAH/ACAC — the non-simple gate
```

## 6. The Vary/cache measurement — is the response per-origin

```bash
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://a.com' | grep -i 'vary'
#   Vary: Origin → per-origin — each test clean
#   no Vary      → a shared cache may lie
```

## 7. The white-box greps — finding the check's source

```bash
# the CORS middleware/config
grep -rnoiE 'cors\(|CORS\(|CORSMiddleware|flask_cors|rack-cors|django-cors-headers|@CrossOrigin|AddCors|EnableCors' <src> | head -20
# the hand-rolled header set
grep -rnoiE 'Access-Control-Allow-Origin|set_header.*Origin|header.*Allow-Origin|allow_origin' <src> | head -20
# the credential allow
grep -rnoiE 'Access-Control-Allow-Credentials|supports_credentials|allow_credentials|allowCredentials' <src> | head -10
# the origin-check logic — reflect vs allowlist vs regex
grep -rnoiE 'origin.*(in|==|match|test|startswith|endswith|includes|regex|allowed)' <src> | head -20
```

## 8. The check-shape signature table — grep → shape

```text
cors() / CORS(app)                      → a default `*` — public
{origin:true,credentials:true}          → a reflect+creds — THE VULN
Set(Allow-Origin, Request.Origin)       → a literal reflect — THE VULN
origins=['*']                           → a public read
origins=True / AllowAnyOrigin           → a reflect-all
origins=['https://*.t.com']             → a subdomain-trust
allowed_origins_patterns=['.*']         → a regex reflect-all
a startswith/endswith on the origin     → a prefix/suffix bypass
a re.match/re.search                    → a regex bypass
an allowlist (exact-match list)         → a fixed check — closed unless bypassable
```

## 9. The alternate-read signals — the non-CORS channel

```bash
# a JSONP endpoint — a script-tag read
grep -rnoiE 'callback|jsonp|application/javascript' <src>
# a postMessage broadcast
grep -rnoE 'postMessage' <src>
# a ws endpoint
grep -rnoiE 'new WebSocket|ws://|wss://|socket\.io' <src>
```

## 10. The false-positive filter — what isn't the vuln

```text
- a `*` on a sensitive endpoint → public read — NOT the vuln
- an ACAO without ACAC → non-credentialed — limited
- a reflected ACAO with SameSite=Lax cookie → cookie doesn't ride
- an endpoint returning public data → nothing sensitive to read
- 'CORS' in a header name on a WRITE endpoint → CSRF, not CORS
```

## 11. The detection decision-tree

```text
ACAO reflected + ACAC:true + cookie-ride → credentialed read — CONFIRM path
ACAO null + ACAC:true                    → opaque read — a null-shape
ACAO *  (any ACAC)                       → public read — NOT the vuln
ACAO fixed (your origin excluded)        → closed — bypass test or pivot
no ACAO                                  → not CORS — a different class
a JSONP endpoint                         → a script-tag read — alternate channel
a strict allowlist + no bypass           → dead — pivot
```

## 12. The detection ledger — recording the measurement

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-detect: ACAO=<shape>, ACAC=<t/f>, cookie-ride=<y/n> on /api/x"
# the measurement is the hypothesis — the read is the confirm
```
