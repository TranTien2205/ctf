# The ACAO/ACAC matrix — what each header pair allows

The two headers that decide the whole class: `Access-Control-Allow-
Origin` (who may read) and `Access-Control-Allow-Credentials`
(whether cookies ride). Every combination and its exploitability.

---

## 1. The pair, in one table

| ACAO | ACAC | The read |
|---|---|---|
| `*` | absent/false | any origin reads, NO credentials — public data only |
| `*` | `true` | INVALID — the browser rejects `*`+credentials; the request fails |
| `<reflected-origin>` | `true` | that origin reads WITH credentials — the vuln |
| `<fixed-allowlist>` | `true` | only listed origins read with credentials |
| `null` | `true` | `null` origin reads with credentials — opaque-origin pages |
| absent | — | not CORS-open — no cross-origin read |

## 2. The `*`+credentials rule — the browser's hard reject

```text
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
→ the browser REFUSES this combination — a wildcard origin can't
  carry credentials. the fetch fails with a CORS error. a `*` is
  only useful for unauthenticated/public data.
```

The common mistake: `*` looks open but never carries credentials —
a `*` on a session endpoint is not exploitable for the session data.

## 3. The reflected-origin — the vulnerable shape

```text
Access-Control-Allow-Origin: <whatever-you-sent>
Access-Control-Allow-Credentials: true
→ the server echoes ANY origin → your evil page reads the response
  WITH the victim's cookies → full read primitive.
```

```js
fetch('https://t/api/me',{credentials:'include'})
  .then(r=>r.json()).then(d=>/* d is the session data */)
// the victim's browser sends cookies; the reflected ACAO lets you read
```

## 4. The fixed-allowlist — and its bypasses

```text
Access-Control-Allow-Origin: https://app.target.com
→ only that origin — unless the check is bypassable:
- a substring match: 'target.com' matches 'target.com.evil.com'
- a prefix match: 'https://target.com' matches 'https://target.com.evil.com'
- a suffix match: '.target.com' matches 'eviltarget.com'? no — needs
  the dot; 'sub.target.com' matches — a subdomain you control
- a null check: 'null' matches a data:/sandboxed origin
- a regex bug: 'target.com*' matches 'target.com.evil.com'
```

## 5. The `null` origin — the opaque-origin carrier

```text
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true
→ a page with an opaque origin reads with credentials. opaque origins:
- a sandboxed iframe (sandbox attr without allow-same-origin)
- a data: URL
- a file: page
- a redirect through an opaque context
```

```html
<!-- a sandboxed iframe sends Origin: null -->
<iframe sandbox="allow-scripts" src="data:text/html,
<script>fetch('https://t/api/me',{credentials:'include'})
.then(r=>r.text()).then(d=>parent.postMessage(d,'*'))</script>">
</iframe>
```

The `null`-allowed endpoint + a sandboxed/data: page = a credentialed
read.

## 6. The ACAC — the credentials question

```text
Access-Control-Allow-Credentials: true
→ the browser lets a fetch(..., credentials:'include') send cookies
  AND lets the JS read the response. without it, the fetch sends
  cookies but the response is unreadable (or the browser blocks).
- ACAC: true is REQUIRED for a credentialed read
- a missing ACAC → a non-credentialed read (public data)
```

## 7. The preflight pair — Allow-Methods + Allow-Headers

```text
a non-simple request (custom header, PUT/DELETE, application/json)
triggers a preflight OPTIONS. the response decides:
Access-Control-Allow-Methods: GET, POST, PUT
Access-Control-Allow-Headers: X-Custom, Content-Type
→ which methods/headers the real request may use.
```

```bash
# the preflight read
curl -i -X OPTIONS "$BASE/api/x" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: PUT' \
  -H 'Access-Control-Request-Headers: X-Custom'
# read ACAO, ACAM, ACAH on the preflight response
```

## 8. The Expose-Headers — what response headers are readable

```text
Access-Control-Expose-Headers: X-Token, Authorization
→ the JS reads these response headers — a token in a header is
  readable if Expose-Headers lists it. a Set-Cookie is NEVER
  readable cross-origin.
```

## 9. The Max-Age — preflight caching

```text
Access-Control-Max-Age: 86400
→ the browser caches the preflight for N seconds — a measurement
  that changes may need a fresh context to re-test.
```

## 10. The decision matrix — what's exploitable

| Shape | Verdict |
|---|---|
| reflected ACAO + ACAC | full credentialed read — the vuln |
| reflected ACAO, no ACAC | read without credentials — limited |
| `*` + no ACAC | public read — not the vuln |
| `*` + ACAC | invalid combo — request fails |
| `null` + ACAC | credentialed read via opaque origin — the vuln |
| fixed-allowlist + ACAC | closed unless the check bypasses |
| no ACAO | not CORS-open |

## 11. The falsifier

```text
a fixed allowlist the check enforces exactly (no substring/prefix/
null/subdomain bypass) AND ACAC absent — the read is closed. a `*`
on a sensitive endpoint is NOT a vuln (no credentials) — record it
as not-exploitable.
```
