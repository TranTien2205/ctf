# Theory — why CORS exists and why it breaks

The same-origin policy's safety valve, and the exact places the
valve leaks.

---

## 1. The problem CORS solves

```text
the same-origin policy stops a page on origin A from READING a
response from origin B — otherwise any site could read your Gmail.
but legitimate apps NEED cross-origin reads: an SPA on
app.example.com reading api.example.com. CORS is the opt-out
mechanism — the server declares which origins may read, and the
browser enforces it.
```

## 2. The two CORS checks

```text
the SIMPLE request (GET, HEAD, POST with a safelisted content-type
and no custom headers) — fires immediately; the response's ACAO
decides whether the JS may read the body.

the PREFLIGHTED request (a non-simple method or a custom header) —
an OPTIONS preflight asks permission first; if the preflight allows
the method+headers, the real request fires and its ACAO is checked.
```

## 3. The credential rule — the vuln's hinge

```text
a CORS read is 'credentialed' when it carries the session cookie.
two gates must align:
- ACAO must name YOUR origin (a reflected or allowlisted value) —
  a `*` is NOT allowed with credentials.
- ACAC:true must be present — the server must allow credentials.
both → the browser lets the JS read the response.
```

## 4. Why reflection is the canonical vuln

```text
the correct CORS config is an allowlist of trusted origins. the
misconfig is a server that REFLECTS the request's Origin back in
the ACAO — 'whoever you are, I allow you'. a reflected ACAO+ACAC
lets ANY site read the session's data cross-origin.
```

## 5. Why `*` isn't the vuln

```text
a `*` ACAO says 'any origin may read this NON-CREDENTIALED' — the
browser refuses `*`+credentials. a `*` endpoint is a public API —
it reads data anyone can fetch without a session. the vuln needs a
NAMED origin allowed WITH credentials.
```

## 6. Why `null` is a vuln

```text
the `null` origin is what a sandboxed iframe, a data: URL, or a
redirected file sends. if the allowlist contains `null`, an
attacker's opaque-origin page reads the credentialed data. it's a
subtle misconfig — 'null' looks like 'nothing', not 'attack'.
```

## 7. The subdomain-trust vuln

```text
an allowlist entry '*.target.com' trusts every subdomain — a
subdomain XSS, a subdomain takeover, or a CTF-supplied subdomain
reads the credentialed data. the trust is broader than the intent.
```

## 8. Why preflight is a separate gate

```text
a non-simple request needs a preflight — a separate origin-check
with its own ACAO/ACAM/ACAH. a permissive ACTUAL but strict
PREFLIGHT blocks custom-header requests; a simple-request bypass
avoids the preflight entirely.
```

## 9. The SameSite interaction — the modern gate

```text
SameSite=Lax/Strict cookies don't attach to cross-site fetches —
a CORS read of them is non-credentialed regardless of ACAO. the
SameSite attribute is the second line of defense that made naive
CORS reads much rarer.
```

## 10. Why CORS-read + CSRF-write chain

```text
a CORS-read leaks the CSRF token; the CSRF-write uses it — the
read breaks the write's defense. a CORS-open /api/csrf-token
endpoint is a two-class vuln.
```

## 11. The readback model

```text
the proof is the exfil — the data reaching your listener. the CORS
read is only 'real' when the victim's browser actually fetched and
the data arrived. the ACAO is a necessary condition; the exfil is
the sufficient evidence.
```
