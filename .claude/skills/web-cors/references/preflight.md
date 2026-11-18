# Preflight — the OPTIONS negotiation and its bypasses

A non-simple CORS request triggers a preflight `OPTIONS` first. The
preflight's own response decides whether the real request fires —
and it's a separate surface from the actual response.

---

## 1. When a preflight fires

```text
a request needs a preflight when it's NOT 'simple':
- a method other than GET/HEAD/POST
- a custom header (X-CSRF-Token, Authorization, X-Custom)
- a Content-Type other than urlencoded/text-plain/multipart
- an upload listener, a ReadableStream body, etc.
a simple request (a form POST, a basic GET fetch) skips the preflight.
```

## 2. The preflight's own headers — the answer that matters

```bash
curl -i -X OPTIONS "$BASE/api/x" \
  -H 'Origin: https://evil.com' \
  -H 'Access-Control-Request-Method: PUT' \
  -H 'Access-Control-Request-Headers: X-Custom-Auth'
```

Read the preflight response's:
| Header | Meaning |
|---|---|
| `Access-Control-Allow-Origin` | which origin may proceed |
| `Access-Control-Allow-Methods` | which methods |
| `Access-Control-Allow-Headers` | which custom headers |
| `Access-Control-Allow-Credentials` | whether credentials ride |
| `Access-Control-Max-Age` | how long the browser caches it |

## 3. The preflight-vs-actual divergence — a common hole

```text
the preflight can answer DIFFERENTLY than the actual request:
- a preflight that returns ACAO:* but the actual returns reflected —
  or vice versa
- a preflight that allows PUT but the actual endpoint doesn't
- a preflight that's permissive while the actual is strict (or the
  reverse)
read BOTH — a strict preflight blocks the request entirely; a lax
preflight lets it fire even if the actual is strict.
```

## 4. The "the actual request never fires" — a strict preflight

```text
a preflight that doesn't reflect the Origin or doesn't allow the
method → the browser never sends the real request → the endpoint
is unreachable via that shape. the bypass: a SIMPLE request that
needs no preflight.
```

## 5. The simple-request bypass — avoiding the preflight

```js
// a simple request — no preflight
fetch('https://t/api/x',{credentials:'include'})   // GET — simple
// a 'custom' header needs a preflight — avoid it:
//   use a body-field instead of a header for the credential
//   use Content-Type: text/plain instead of application/json
```

A CORS exploit that needs no custom headers or methods skips the
preflight entirely — the simplest read.

## 6. The Max-Age cache — a measurement trap

```text
Access-Control-Max-Age: 86400 → the browser caches the preflight
for a day. a test that 'fixed' the CORS may still use a cached
permissive preflight. test in a fresh context/incognito for a real
measurement.
```

## 7. The preflight's Origin-reflection — its own check

```text
the preflight's ACAO is the gate that decides if the real request
fires — the same reflection/allowlist/null checks apply to the
preflight's ACAO as to the actual response's. test the preflight's
ACAO separately from the actual's.
```

## 8. The Allow-Headers surface — which custom headers pass

```text
Access-Control-Allow-Headers: *           → any header — open
Access-Control-Allow-Headers: Authorization, X-Custom → a list
Access-Control-Allow-Headers: <reflected> → reflects the request —
                                            the same bypass surface
```

A reflected Allow-Headers lets you send any custom header — a
Bearer-token credential, a custom CSRF token.

## 9. The preflight→bypass table

| Preflight shape | The move |
|---|---|
| strict ACAO on preflight | a simple request (no preflight needed) |
| reflected ACAO on preflight | the real request fires — the read is open |
| Allow-Headers: * or reflected | send any custom header |
| Max-Age long | fresh-context test |
| strict method-list | a GET/simple request for the read |

## 10. The falsifier

```text
a strict preflight (no Origin reflection, a fixed method/header
list) AND the only useful request needs a custom header/method that
the preflight blocks AND no simple-request read exists — the read
is closed via preflight.
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "preflight: <preflight-shape> -> <the bypass or block>"
```
