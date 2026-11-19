# Troubleshoot — when the CORS read doesn't work

Each symptom, its cause, and the fix.

---

## 1. `curl` shows ACAO reflected, the browser fetch fails

```text
cause: a SameSite=Lax/Strict cookie — the browser doesn't attach it;
the fetch succeeds but reads UNAUTHENTICATED data. OR the ACAO is a
`*` and ACAC:true — the browser rejects the credentialed fetch.
fix: check the cookie's SameSite; check the exact ACAO value — a `*`
never carries credentials.
```

## 2. The fetch returns a CORS error, no data

```text
cause: the actual ACAO doesn't allow your origin — a fixed allowlist,
or a `*` with credentials. the browser blocks the READ.
fix: the curl replay shows the real ACAO — is YOUR origin allowed?
```

## 3. The read works but returns 'unauthorized' / public data

```text
cause: the credential didn't ride — a SameSite-gated cookie, a
Bearer the fetch can't carry, a session that needs a non-cookie
credential.
fix: the fetch's credentials:'include' carries the cookie; if it's
SameSite=Lax it doesn't attach — a non-credentialed read only.
```

## 4. A preflight is rejected

```text
cause: your fetch is non-simple — a custom header (Authorization,
X-Token, application/json) triggers OPTIONS; the preflight's ACAO/
ACAM/ACAH doesn't allow it → the request never fires.
fix: use a simple request (GET or urlencoded POST, no custom headers)
OR confirm the preflight allows your method+headers.
```

## 5. The exfil doesn't arrive

```text
cause: the read worked but the exfil fetch failed — a CSP on the
exfil page, a fetch to a blocked domain, the listener not up.
fix: the listener up: oob_listener serve; a CSP-free exfil (a
<script src> or an <img>); check the hit log.
```

## 6. The `null` origin isn't reflected

```text
cause: 'null' isn't in the allowlist — the check rejects it. a
sandboxed/data: page's Origin still fails.
fix: 'null' only works when it's literally allowed — test it.
```

## 7. The lookalike origin doesn't reflect

```text
cause: the check is a proper allowlist — exact-match origins, not
substring/regex.
fix: the bypass battery tells you which check shape it is — a strict
allowlist has no origin-bypass; a different vector or a non-CORS class.
```

## 8. `Vary: Origin` — the cached response lies

```text
cause: a shared cache keyed on Origin — the response you see is
cached for a different Origin.
fix: a unique Origin per test; check `Vary` — a `Vary: Origin`
response is per-origin.
```

## 9. The bot can't reach your exploit page

```text
cause: an airgapped bot — no external fetch. the page must come
from the target itself or a data: URL.
fix: a stored-XSS context on the target, or a data: URL whose
Origin is 'null' (needs a null-allowed CORS).
```

## 10. The exploit works on YOUR browser, not the bot's

```text
cause: your browser has the cookie; the bot's session is different,
or the bot's cookie is SameSite-gated differently, or the bot is
headless with no cookie.
fix: the bot carries ITS session — the exploit must read under the
bot's context, not yours.
```

## 11. A JSONP endpoint doesn't fire

```text
cause: the callback param name is wrong, or the endpoint needs a
specific param (callback/jsonp/cb), or the content-type is
application/json (not JS) → the tag can't execute it.
fix: grep the front-end for the callback param; check the response
Content-Type.
```

## 12. The `Access-Control-Allow-Headers` blocks a custom header

```text
cause: your fetch needs X-Token/Authorization; the preflight's ACAH
doesn't list it → the request never fires.
fix: find a non-custom-header path — a cookie session (no
Authorization header needed) or a query/body-carried token.
```

## 13. A `null`+credentials read returns nothing

```text
cause: `null`+ACAC is allowed but the cookie still doesn't ride —
a SameSite=Lax cookie doesn't attach even to a `null` origin.
fix: SameSite=None+Secure is required for the cookie to attach on a
cross-site fetch regardless of origin value.
```

## 14. The endpoint reads, but the data isn't sensitive

```text
cause: the CORS read works but the endpoint returns public/nonsensitive
data — the flag is on a different endpoint.
fix: enumerate the sensitive endpoints — the read target must carry
the flag.
```

## 15. A proxy/CDN eats the CORS headers

```text
cause: the origin app emits the ACAO but the CDN/proxy strips or
overrides it.
fix: check the response headers end-to-end — the CDN's CORS config
may differ from the app's.
```
