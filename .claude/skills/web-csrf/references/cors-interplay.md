# CORS interplay — when the CSRF meets the CORS gate

CORS and CSRF are siblings that answer different questions. CSRF is
about SENDING a request; CORS is about READING the response. The
places they interact — and where one class becomes the other.

---

## 1. The split in one table

| | CSRF | CORS-read |
|---|---|---|
| the goal | fire a request with credentials | read a cross-origin response |
| the gate | SameSite/token/Origin on the request | ACAO/ACAC on the response |
| the request | `no-cors`, forms — no CORS needed | `cors` mode — needs CORS-open |
| reads response | never | yes — the whole point |

## 2. The no-cors carriers — CSRF doesn't need CORS

```js
fetch(url,{mode:'no-cors',credentials:'include'})   // sends, response opaque
navigator.sendBeacon(url,body)                       // sends, no response
<form> submits                                        // sends, nav response
XMLHttpRequest + withCredentials                      // sends, response opaque
```

`no-cors` mode sends the request WITHOUT a CORS check — the response
is opaque (unreadable) but the write lands. CORS governs READING,
not SENDING. This is why CSRF works without CORS-open.

## 3. The CORS-open read — when it becomes the better class

```text
if the endpoint returns the flag/secret AND is CORS-open
(Access-Control-Allow-Origin: * or a reflected origin +
Access-Control-Allow-Credentials: true) → a fetch in cors mode
reads the response cross-origin → that's a READ, the web-cors class.
```

```js
fetch('https://t/api/me',{credentials:'include'})   // cors mode
  .then(r=>r.text()).then(d=>/* the flag in d */)
// works ONLY if the response carries ACAO:* or ACAO:<your-origin>
// AND ACAC:true
```

## 4. The preflight question — when a preflight is needed

```text
a 'simple' request (GET/POST/HEAD + safelisted headers) doesn't
preflight — a no-cors CSRF uses these.
a 'non-simple' request (PUT/DELETE, a custom header, application/json
content-type) triggers a preflight OPTIONS — the server must answer
the preflight for the real request to fire.
```

A CSRF that needs `application/json` can't ship it in no-cors (it's
not safelisted) — and a preflight would fail without CORS-open.
That's WHY the JSON write must go through text/plain.

## 5. The CORS-misconfig that helps CSRF

```text
a CORS-open endpoint lets the CSRF page READ the token:
- /api/csrf-token returns the token AND is ACAO:* → the page fetches
  it cross-origin → embeds it in the CSRF form → the token gate opens
```

The interplay: a CORS-read of the CSRF token breaks the token
defense. Check for a readable token endpoint.

## 6. The readback-via-CORS — when the CSRF needs the response

```text
a CSRF write whose RESULT is in the response (the flag, a new id,
a token) — you can't read it in no-cors. options:
- if CORS-open → fetch in cors mode reads it
- if not → the write must store the result somewhere you read
  separately (a field, a list, your account)
```

## 7. The "the request is simple but the response needs CORS" trap

```text
a form POST is a simple request — it fires without a preflight. but
the RESPONSE goes to the navigation — unreadable. a CSRF never
needs the response readable; if you need the response, you need
CORS-open and it's a different class.
```

## 8. The credential mode matrix

```text
fetch(url)                              // same-origin default — no credentials
fetch(url,{credentials:'same-origin'})  // same-origin only
fetch(url,{credentials:'include'})      // attach cookies — but in no-cors
                                        // the response is opaque; in cors
                                        // it needs ACAC:true on the response
fetch(url,{mode:'no-cors',credentials:'include'})  // attach + opaque — the CSRF
fetch(url,{mode:'cors',credentials:'include'})     // attach + readable — needs
                                                   // CORS-open — the READ class
```

## 9. The SameSite+CORS interaction

```text
SameSite gates whether the cookie ATTACHES; CORS gates whether the
RESPONSE is readable. a SameSite=None cookie attaches to a fetch;
whether the response is readable depends on CORS. a SameSite=Lax
cookie doesn't attach to a fetch regardless of CORS.
```

## 10. The decision — CSRF or CORS class

```text
do you need to READ a cross-origin response?     → web-cors (needs CORS-open)
do you need to FIRE a state-changing request?    → web-csrf (no CORS needed)
does the flag come back in the CSRF's response?  → you can't read it — the
                                                    write must store it, OR
                                                    the endpoint is CORS-open
                                                    and it's a read
does the CSRF need the token?                    → if a CORS-open endpoint
                                                    returns it — a CORS-read
                                                    unlocks the CSRF-write
```

## 11. The probe — is the response readable?

```bash
# the CORS-open test on the endpoint
curl -i "$BASE/x" -H 'Origin: https://evil.com' | grep -i 'access-control'
# ACAO:* or ACAO:https://evil.com + ACAC:true → the response is
# cross-origin readable → a CORS-read is possible
```

## 12. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-interplay: token endpoint is CORS-open -> readable token"
```
