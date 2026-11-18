# Credentials interplay — cookies, auth headers, and the fetch modes

What actually attaches to a CORS read — and the fetch credentials
mode that decides it.

---

## 1. The fetch credentials modes

```js
fetch(url)                            // default 'same-origin' — no cross creds
fetch(url,{credentials:'same-origin'})// same-origin only
fetch(url,{credentials:'omit'})       // never send credentials
fetch(url,{credentials:'include'})    // send cookies + auth — needs ACAC:true
```

`credentials:'include'` is the CSRF/CORS mode — it sends the session
cookie on the cross-origin request AND (for `cors` mode) lets you
read the response when ACAC:true.

## 2. The mode split — cors vs no-cors

```js
fetch(url,{mode:'cors',credentials:'include'})
// a CORS-mode fetch: the response is READABLE if ACAO+ACAC allow —
// this is the CORS-read class

fetch(url,{mode:'no-cors',credentials:'include'})
// a no-cors fetch: sends cookies but response is OPAQUE — the CSRF
// shape, not a read
```

The `mode` decides read-vs-write: `cors` reads (needs CORS-open),
`no-cors` writes (opaque). A CORS exploit uses `cors` + `include`.

## 3. The credential types that ride

```text
- cookies → per SameSite + the cookie's attributes
- HTTP Basic/Digest auth → the browser's stored auth
- client TLS certs → mutual-TLS contexts
- the Authorization header → only if the app echoes it AND
  Access-Control-Allow-Headers lists it AND ACAC allows
```

## 4. The SameSite question on a CORS read

```text
the cookie still needs SameSite to attach:
- SameSite=None+Secure → attaches cross-site → the read carries it
- SameSite=Lax → does NOT attach on a fetch (not a top-nav) → the
  read carries no cookie → a non-credentialed read
- SameSite=Strict → never attaches
```

A CORS-read needs BOTH the ACAO/ACAC allow AND the SameSite cookie
to actually carry the credential. A `SameSite=Lax` session cookie
never rides a fetch — the "CORS vuln" reads nothing private.

## 5. The Authorization-header read — the non-cookie credential

```text
an API that takes Authorization: Bearer <token> — the token isn't a
cookie:
- the token must be KNOWN (a leaked/hardcoded/public token) — a
  cross-origin page can't read a cookie-token
- BUT the token needs Access-Control-Allow-Headers: Authorization
  on the preflight + ACAO for the read
```

A Bearer-token API is CORS-exploitable only if the attacker knows a
token — a different credential model than the ambient cookie.

## 6. The preflight on a credentialed non-simple request

```text
a fetch with credentials + a non-simple method/header → a preflight
OPTIONS first. the preflight must ALSO return ACAO+ACAC for the
real request to fire.
- a preflight that returns ACAO:* → the real credentialed request
  can't use it (*+credentials invalid)
- a preflight that reflects the Origin + ACAC → the real request fires
```

## 7. The cookie that CAN'T be set — third-party blocking

```text
a cross-origin read's response Set-Cookie — the browser may block
it under third-party-cookie rules or Partitioned. the READ works;
the WRITE of a new cookie may not.
```

## 8. The full credential→read matrix

| Credential | Attaches on a cross-origin fetch? | Readable? |
|---|---|---|
| SameSite=None+Secure cookie | yes (ACAC:true) | yes (ACAO allows) |
| SameSite=Lax cookie | no | — |
| SameSite=Strict cookie | no | — |
| Authorization: Bearer | if you know the token + ACAH allows | yes |
| Basic auth | the browser's stored auth — if prompted | yes |
| a custom header credential | if ACAH allows + you know it | yes |

## 9. The "a * can't carry credentials" trap — restated

```text
ACAO:* + ACAC:true → the browser REJECTS — no credentialed read via
*. a sensitive endpoint returning * is NOT exploitable — record it
as not-exploitable, a common false-positive.
```

## 10. The falsifier

```text
ACAO reflected/fixed-open but the session cookie is SameSite=Lax/
Strict AND no non-cookie credential exists — the read carries no
credential → a public-data read only. not the vuln.
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-creds: ACAO reflected + ACAC:true + SameSite=None -> credentialed read"
```
