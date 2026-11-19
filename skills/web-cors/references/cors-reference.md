# Knowledge base — the CORS corpus's consolidated reference

The distilled knowledge — every fact an agent needs to reason about
a CORS surface without re-deriving it.

---

## The mechanism — how the read works

```text
1. a page on origin A fetches origin B with credentials:'include'
2. the browser fires the request — the cookie may ride (SameSite-gated)
3. the response arrives — the browser checks the ACAO
4. if ACAO names origin A (or `*` for non-credentialed) AND ACAC:true
   when credentials rode → the JS may read the response body
5. else → a CORS error — the response is opaque to the JS
```

## The two-gate model — the vuln's requirements

```text
gate 1 — the ACAO must allow YOUR origin:
  reflected (echoes the request's Origin) → any origin
  null (allows 'null')                    → an opaque-origin page
  fixed allowlist                          → a named origin — bypass or closed
  subdomain-trust (*.t.com)                → a controlled subdomain
  prefix/suffix/substring                  → a lookalike origin
  regex                                    → a pattern bypass
  *                                        → public — never credentialed

gate 2 — the credential must ride:
  ACAC:true (the server allows credentials)
  AND the credential attaches:
    a SameSite=None+Secure cookie          → attaches cross-site
    a Bearer header                         → needs a preflight + the token
    a Lax/Strict cookie                     → doesn't attach — a public read
```

## The request-shape model — simple vs non-simple

```text
a SIMPLE request (GET/HEAD/POST + safelisted headers + safelisted
content-type) — fires immediately, no preflight; the actual ACAO
gates the read.

a NON-SIMPLE request (a custom header, a non-simple method, a
non-safelisted content-type) — an OPTIONS preflight first; its
ACAO/ACAM/ACAH gate whether the request fires.
```

## The credential model — what can ride

```text
a cookie        → credentials:'include' + SameSite=None+Secure
a Bearer        → headers:{Authorization} + a preflight + the token
an API key      → a header (preflight) or a query param (simple)
a client cert   → mTLS — browser-managed
a Basic-auth    → an Authorization: Basic header — preflight
```

## The same-site-vs-same-origin distinction — the subtle gate

```text
a fetch 'app.t.com' → 'api.t.com' is:
  CROSS-ORIGIN  → CORS applies (different origins)
  SAME-SITE     → a SameSite=Lax cookie ATTACHES (registrable-domain match)
→ a Lax cookie rides a same-site-cross-origin fetch — the SameSite
  gate doesn't help; only the CORS gate does.
```

## The check-shape model — every allowlist's failure mode

```text
reflect          → echoes the Origin — any origin passes
null-allow       → 'null' in the list — an opaque-origin page passes
allowlist        → exact-match — only the listed pass — closed
prefix           → startswith('https://t.com') — 't.com.evil.com' passes
suffix           → endswith('t.com') — 'evilt.com' passes
substring        → 't.com' in origin — 'evil-t.com' passes
regex            → a pattern — a loose-pattern bypass
subdomain        → '*.t.com' — a controlled sub passes
url-parse        → an @/?/# confusion — a parse bug
```

## The read-target model — which endpoint carries the flag

```text
a session-data endpoint    → /api/me, /api/user, /api/profile
a flag endpoint            → /api/flag, /admin
a capability endpoint      → /api/token, /api/csrf
a config endpoint          → /api/config — may carry a key
```

## The delivery model — how the page reaches the victim

```text
a /report bot    → the page rides the bot's session
a stored page    → the page IS on the target — same-origin
a data: URL      → a null-origin page — airgapped-compatible
a subdomain      → a trusted-origin page
a phishing link  → the victim clicks
```

## The exfil model — how the data leaves

```text
a fetch GET      → the canonical
an img GET       → a no-CORS channel
a beacon         → a fire-and-forget
a ws             → a live channel
a write-back     → the data lands on the target
a DOM-writeback  → a screenshotting bot
a postMessage    → a parent-frame channel
a DNS            → a blocked-domain bypass
```

## The alternate-read model — when CORS is closed

```text
a JSONP endpoint      → a <script src> read — no CORS
a JS-served endpoint  → XSSI — a global-setter capture
a ws endpoint         → a websocket read — CSWSH
a postMessage page    → a broadcast read
an XSS surface        → a same-origin read — CORS moot
an XS-leak            → a side-channel measure
```

## The evidence model — what proves the read

```text
a CANDIDATE  → a measured ACAO+ACAC that allows the read
a CONFIRMS   → the exfil — the sensitive data reaches your listener
a FLAG       → the flag in the exfil — gated through pre-flag
```

## The falsifier model — what rules the read out

```text
a `*` endpoint                → public — never the vuln
ACAC absent                   → non-credentialed — limited
a SameSite-gated cookie        → doesn't attach — non-credentialed
a strict allowlist + no bypass → closed
a strict preflight + no simple → closed for non-simple
a public endpoint              → nothing sensitive
```

## The framework-config model — where the CORS lives per stack

```text
Express   → cors({origin,credentials})
Flask     → flask_cors.CORS(app,origins,supports_credentials)
Django    → corsheaders + CORS_* settings
Go        → rs/cors or hand-rolled Set(A-C-A-Origin)
Spring    → @CrossOrigin / addCorsMappings
Rails     → rack-cors origins
Laravel   → fruitcake config/cors.php
ASP.NET   → AddCors policy
FastAPI   → CORSMiddleware
nginx     → add_header Access-Control-*
```

## The boundary model — what's NOT CORS

```text
a no-cors write     → CSRF — the request fires; CORS doesn't gate it
a same-origin read  → not CORS — no cross-origin question
a script-tag serve  → JSONP/XSSI — a different read primitive
a page broadcast    → postMessage-hijack
a ws channel        → CSWSH — the web-websocket class
a server-side fetch → SSRF
a side-channel      → XS-leak
```
