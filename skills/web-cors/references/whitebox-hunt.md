# Whitebox hunt — finding the CORS surface in source

The grep-driven pass over the handout: where the CORS config lives,
where the sensitive endpoints are, and where the read target sits.

---

## 1. The config greps — the CORS posture

```bash
# the middleware/config — every framework's CORS call
grep -rnoiE 'cors\(|CORS\(|CORSMiddleware|flask_cors|rack-cors|django-cors-headers|@CrossOrigin|AddCors|EnableCors|fruitcake|cors\.New|cors\.AllowAll' <src> | head -30

# the hand-rolled header set — no middleware
grep -rnoiE 'Access-Control-Allow-Origin|set_header.*Origin|header.*Allow-Origin|allow_origin|res\.setHeader.*Origin|Header.*Origin' <src> | head -30
```

## 2. The origin-check greps — reflect vs allowlist vs regex

```bash
# the reflect — the request's Origin echoed
grep -rnoiE 'origin.*(request|req|self\.request|ctx).*origin|headers.*Origin|Request\.Origin|Request\.Headers.*Origin|HTTP_ORIGIN' <src> | head -20

# the allowlist — a fixed set
grep -rnoiE 'allowed_origins|allow_origins|origins.*=|whitelist.*origin|allowedOrigins|origins.*\[|origins.*\(' <src> | head -20

# the check logic — in/==/startswith/endswith/regex
grep -rnoiE 'origin.*(in|==|===|match|test|startswith|endswith|includes|indexOf|regex|pattern|re\.|fullmatch)' <src> | head -20
```

## 3. The credential greps — ACAC + the cookie

```bash
# the credential allow
grep -rnoiE 'Access-Control-Allow-Credentials|supports_credentials|allow_credentials|allowCredentials|credentials.*true' <src> | head -20

# the session cookie's SameSite — does it ride
grep -rnoiE 'SameSite|same_site|sameSite|cookie.*Secure|secure.*cookie|set_cookie|setCookie' <src> | head -20
```

## 4. The endpoint greps — the sensitive read targets

```bash
# the API endpoints returning session data
grep -rnoE '(api|me|user|profile|flag|secret|data|private|admin|account|balance|token|config|session|info|dashboard)' <src> | \
  grep -iE 'route|@|app\.|def |get|json|res\.|return|response|http' | head -40

# the flag specifically
grep -rnoiE 'flag|FLAG\{|secret|key|token' <src> | grep -v 'test\|spec\|# ' | head -20
```

## 5. The preflight greps — the OPTIONS handler

```bash
# the OPTIONS/preflight logic
grep -rnoiE 'OPTIONS|preflight|app\.options|@app\.route.*OPTIONS|method.*OPTIONS|Access-Control-Allow' <src> | head -20
```

## 6. The alternate-read greps — JSONP/ws/postMessage

```bash
# JSONP — a callback param
grep -rnoiE 'callback|jsonp|application/javascript|text/javascript|res\.send.*\(' <src> | head -20
# postMessage
grep -rnoE 'postMessage\(' <src> | head -10
# websocket
grep -rnoiE 'new WebSocket|ws://|wss://|socket\.io|websocket|onmessage' <src> | head -10
```

## 7. The bot greps — the victim-viewer

```bash
# the bot — a puppeteer/playwright/admin context
grep -rnoiE 'bot|admin|visit|report|puppeteer|playwright|chromium|selenium|JSDOM|headless' <src> | head -20
# the flag-cookie — whose session rides
grep -rnoiE 'flag.*cookie|cookie.*flag|setCookie.*flag|flag.*admin|admin.*flag' <src> | head -10
```

## 8. The per-file read — the CORS code in context

```bash
# read the file around the CORS call — the check's shape
grep -rln 'cors\|Access-Control\|origin' <src> | head -10 | while read f; do
  echo "=== $f ==="; grep -n -A3 -B3 'cors\|Access-Control\|origin' "$f" | head -40; done
```

## 9. The check-shape signature — grep → what it means

```text
cors() / CORS(app)                       → default `*` — public
{origin:true,credentials:true}           → reflect+creds — VULN
Set(A-C-A-Origin, Request.Origin)        → literal reflect — VULN
origins=['*']                            → public read
origins=True / AllowAnyOrigin            → reflect-all
origins=['https://*.t.com']              → subdomain-trust
allowed_origins_patterns=['.*']          → regex reflect-all
a startswith/endswith on origin          → a bypassable check
an exact-match allowlist                 → a closed check
'supports_credentials' / ACAC            → the credentialed read intended
```

## 10. The hunt ledger — the source findings recorded

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-whitebox: <file:line> — <check-shape> + <sensitive-endpoint>"
```
