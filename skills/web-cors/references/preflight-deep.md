# Preflight deep — the OPTIONS gate for non-simple reads

A non-simple request — a custom header, a non-simple method, a
non-safelisted content-type — needs a preflight. Its own CORS
headers decide whether the real request fires.

---

## 1. When a preflight happens

```text
a request is NON-simple when it has:
- a method other than GET/HEAD/POST
- a content-type other than urlencoded/multipart/text-plain
- ANY custom header (Authorization, X-Token, Content-Type json)
- a ReadableStream body
a non-simple request → the browser fires an OPTIONS preflight first.
```

## 2. The preflight request — what the browser sends

```http
OPTIONS /api/x HTTP/1.1
Origin: https://evil.com
Access-Control-Request-Method: GET
Access-Control-Request-Headers: X-Token
```

## 3. The preflight response headers — the permission

```text
Access-Control-Allow-Origin   — which origin may proceed
Access-Control-Allow-Methods  — which methods are allowed
Access-Control-Allow-Headers  — which headers are allowed
Access-Control-Allow-Credentials — may credentials ride
Access-Control-Max-Age        — how long the browser caches it
```

## 4. The preflight test — per method

```bash
# does the preflight allow the request?
curl -i -X OPTIONS "$BASE/api/x" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: X-Token'
#   ACAO/ACAM/ACAH on the response — allowed or not
```

## 5. The preflight-vs-actual split — two different checks

```text
the preflight's ACAO and the actual response's ACAO are SEPARATE —
a permissive preflight (reflects the Origin) + a strict actual (a
fixed allowlist) means the request fires but the read fails. a
strict preflight blocks the request before the actual is reached.
```

## 6. The Max-Age cache — a preflight that persists

```text
a Max-Age caches the preflight — a 'fixed' CORS still uses the
cached permissive answer. a test in the same browser session sees
the stale cache. test in a fresh context.
```

## 7. The simple-request bypass — avoiding the preflight

```js
// a GET — simple, no preflight
fetch('https://t/api/x',{credentials:'include'})
// a urlencoded POST — simple
fetch('https://t/api/x',{method:'POST',credentials:'include',
  headers:{'Content-Type':'application/x-www-form-urlencoded'},
  body:'q=x'})
```

A simple request skips the preflight — only the actual ACAO is
checked. when the preflight is strict, use a simple request.

## 8. The ACAH gate — which headers are allowed

```bash
# a custom header needs the preflight's ACAH to name it
curl -i -X OPTIONS "$BASE/api/x" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: Authorization'
#   ACAH: authorization → allowed; else the header can't be sent
```

## 9. The ACAM gate — which methods are allowed

```bash
# a PUT needs ACAM to allow it
curl -i -X OPTIONS "$BASE/api/x" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: PUT'
#   ACAM: GET,PUT → PUT allowed
```

## 10. The preflight-credential rule

```text
the preflight NEVER carries credentials — it's a permission check.
the credential question is decided on the ACTUAL request's
credentials:'include' + the actual's ACAO+ACAC.
```

## 11. The preflight-failure modes

```text
- the preflight's ACAO doesn't allow your origin → the request
  never fires — a `cors error` in the console.
- the ACAM doesn't list your method → the request never fires.
- the ACAH doesn't list your header → the request never fires.
- the endpoint doesn't handle OPTIONS → a 405/no-CORS → blocked.
```

## 12. The white-box preflight read

```bash
# the OPTIONS handler — the preflight logic
grep -rnoE 'OPTIONS|preflight|options\(|app\.options|Access-Control-Allow' <src> | head -20
```

## 13. The preflight decision table

```text
a permissive preflight + a permissive actual → non-simple read works
a permissive preflight + a strict actual     → request fires, read fails
a strict preflight                           → request never fires
a simple request                             → no preflight — actual decides
```
