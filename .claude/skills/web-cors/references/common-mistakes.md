# Common mistakes — the ways CORS analysis goes wrong

Each a real failure mode: what it looks like, why it fails, the fix.

---

## 1. "ACAO reflected" ≠ "exploitable"

```text
a reflected Origin is only HALF the check — without ACAC:true the
read carries no credentials. a reflected ACAO alone is a candidate
for a non-credentialed read, not the vuln.
```

Fix: check ACAC alongside — the pair decides.

## 2. "ACAO:*" on a sensitive endpoint — the trap

```text
a `*` looks open but the browser rejects `*`+credentials — a `*`
endpoint NEVER carries the session cookie. a `*` on /api/me reads
public data only — NOT exploitable.
```

Fix: `*` = public read; record not-exploitable, not the vuln.

## 3. Forgetting the SameSite gate

```text
a reflected ACAO + ACAC:true — BUT the session cookie is SameSite=
Lax → the fetch doesn't attach it → a non-credentialed read. the
CORS headers are open but the credential doesn't ride.
```

Fix: check the cookie's SameSite — the credential must attach.

## 4. "The endpoint returns the flag" ≠ "I can read it"

```text
the endpoint returns sensitive data — but the ACAO is a fixed
allowlist that excludes your origin. the data exists; the read is
closed. CORS needs BOTH the data AND the allowed origin.
```

Fix: the read needs an allowed origin, not just sensitive data.

## 5. Assuming a custom header can be sent

```js
fetch(url,{headers:{'X-Custom':'v'},credentials:'include'})
// a custom header needs a preflight — which fails without a
// permissive preflight. the request never fires.
```

Fix: use a simple request (no custom headers) or confirm the
preflight allows the header.

## 6. The preflight-vs-actual confusion

```text
a permissive preflight + a strict actual → the request fires but
the actual denies. OR a strict preflight that blocks before the
actual is even reached. read BOTH.
```

Fix: measure the preflight's ACAO AND the actual's separately.

## 7. The Max-Age cache trap

```text
a long Max-Age caches the permissive preflight — a 'fixed' CORS
still uses the cached permissive answer. a test in the same browser
session sees the stale cache.
```

Fix: test in a fresh context/incognito.

## 8. Reading `Origin` instead of testing it

```text
assuming the server validates Origin because it's 'supposed to' —
many endpoints reflect it without checking. TEST a foreign Origin;
don't assume.
```

Fix: the foreign-Origin replay is the measurement.

## 9. The `null` origin oversight

```text
the check is a strict allowlist — but 'null' is allowed. a
sandboxed/data: page's `Origin: null` passes. a common miss: not
testing 'null'.
```

Fix: always include `Origin: null` in the battery.

## 10. Confusing 'the endpoint exists' with 'the read works'

```text
an endpoint that returns data — but the fetch gets a CORS error.
the endpoint exists; the read is closed. the fetch's CORS error is
a real falsifier, not a 'try harder'.
```

## 11. A stored page that already reads it

```text
fighting the CORS check when a stored-XSS context on the target
reads the endpoint same-origin trivially. a stored page is the
stronger primitive.
```

## 12. Over-crediting a JSONP endpoint

```text
a JSONP endpoint is a READ primitive WITHOUT CORS — but it needs a
callback param AND the tag sends cookies (SameSite-gated). a
SameSite=Strict cookie blocks the JSONP read too.
```

## 13. The "I can set Origin" confusion

```text
you CAN'T set Origin via JS — it's browser-set. the only 'Origin'
values you can produce are your real origin and 'null' (via opaque
contexts). a `curl -H 'Origin: evil.com'` tests the SERVER's check;
a real browser page's Origin is fixed by its context.
```

## 14. The exfil-without-readback

```text
claiming 'the CORS works' without the exfil reaching your listener —
the read may fail silently (a cookie that didn't attach, a parse
error). the OOB hit is the proof.
```

## 15. A `*`+`ACAC` misread

```text
'ACAO:* AND ACAC:true' — the browser rejects this combo; the
request fails with a CORS error. reading it as 'credentialed read
open' is wrong — it's a failed request.
```
