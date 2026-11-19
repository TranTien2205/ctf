# Troubleshoot deep — the CORS failure modes, exhaustively

Every way the CORS read breaks, its root cause, and the exact next step.

---

## 1. The read returns a CORS error — which gate

```text
symptom: fetch() throws a 'blocked by CORS policy' error.
cause: the actual response's ACAO doesn't allow your origin —
a fixed allowlist, or a `*`+credentials, or no ACAO.
next: the curl replay shows the REAL ACAO — is YOUR origin named?
```

## 2. The read returns 200 but 'unauthorized' — the credential gate

```text
symptom: fetch() returns data but it's public/unauthenticated.
cause: the credential didn't ride — a SameSite-gated cookie, or no
credentials:'include', or the ACAC is absent.
next: check the cookie's SameSite; verify credentials:'include' is set.
```

## 3. The request never fires — a preflight block

```text
symptom: the fetch errors before the server sees it — no request
in the server log.
cause: a non-simple request whose preflight's ACAO/ACAM/ACAH denies it.
next: a simple request (GET/urlencoded POST, no custom headers) skips
the preflight.
```

## 4. The `*+ACAC` rejection — the invalid combo

```text
symptom: ACAO:* + ACAC:true — the fetch fails with a 'wildcard'
error.
cause: `*` never carries credentials — a universal browser rule.
next: the `*` endpoint is a public read — a different target.
```

## 5. The exfil fails — the read worked, the exfil didn't

```text
symptom: the CORS read returns the data but the exfil fetch to your
listener errors.
cause: a CSP on the exfil page, a blocked domain, an unreachable
listener.
next: a no-CORS exfil (img/beacon/form); check the listener is up.
```

## 6. The `null` origin isn't reflected — a strict check

```text
symptom: a data: URL page's fetch fails — Origin 'null' not allowed.
cause: 'null' isn't in the allowlist — the check rejects it.
next: 'null' only works when literally allowed — test it explicitly.
```

## 7. The lookalike origin doesn't pass — a strict allowlist

```text
symptom: target.com.evil.com / eviltarget.com / sub.target.com all fail.
cause: the check is an exact-match allowlist — no substring/prefix/
suffix/subdomain bypass.
next: a strict allowlist has no origin bypass — pivot to a different
vector or an alternate-read channel.
```

## 8. The bot can't reach your page — a delivery failure

```text
symptom: the bot endpoint accepts the URL but no fetch fires.
cause: an airgapped bot — it can't reach attacker.com.
next: a data: URL page, a stored-XSS context, or a write-back exfil.
```

## 9. The bot's session isn't the flag-holder's — a context failure

```text
symptom: the read works but returns a non-flag session's data.
cause: the bot isn't logged in as the flag-holder — or its session
cookie is different.
next: verify the bot carries the flag session — a flag cookie, an
admin context.
```

## 10. The cookie doesn't ride — a SameSite block

```text
symptom: the read works but returns unauthenticated data — the
cookie didn't attach.
cause: a SameSite=Lax/Strict cookie — a fetch() doesn't carry it.
next: a non-cookie credential (a Bearer) or a same-site-cross-origin
fetch (app.t.com → api.t.com rides a Lax cookie).
```

## 11. A `Vary: Origin` cache lies — a stale response

```text
symptom: the ACAO differs between your test and a real browser.
cause: a shared cache keyed on a different Origin — the response you
see is cached.
next: a unique Origin per test; check `Vary` — a `Vary: Origin`
response is per-origin.
```

## 12. The Max-Age cache persists a permissive answer

```text
symptom: a 'tightened' CORS still allows the request.
cause: a long Access-Control-Max-Age — the browser cached the
permissive preflight.
next: a fresh browser context / incognito — bypass the cache.
```

## 13. The endpoint is JSON but the read scrapes it wrong

```text
symptom: the read returns the JSON but the flag extraction fails.
cause: the read method wrong — .text() on JSON works but the regex
may miss the flag's format.
next: .json() for a JSON API; a looser flag-regex for HTML.
```

## 14. A redirect breaks the read — a CORS-on-final-response

```text
symptom: the fetch follows a redirect then errors.
cause: a redirect during a CORS fetch — the FINAL response's ACAO
is checked; a redirect to a different origin is a new CORS question.
next: the final URL's ACAO matters — or use `redirect:'error'` to
catch it early.
```

## 15. The JSONP endpoint needs a specific param name

```text
symptom: ?callback=x returns plain JSON — no JS wrapper.
cause: the param name is wrong — cb, jsonp, callback_, or a custom
name.
next: grep the front-end for the callback param; try the alternates.
```

## 16. The XSSI capture fires too late — a race

```text
symptom: the global-setter capture misses the endpoint's global-set.
cause: the setter wasn't installed before the script loaded — or the
endpoint uses a different mechanism.
next: install the Object.defineProperty BEFORE the <script src>.
```

## 17. The ws handshake fails — a non-ws endpoint

```text
symptom: a websocket read fails at the handshake.
cause: the endpoint isn't ws — or requires a subprotocol/auth you
don't have.
next: verify the ws endpoint exists — a 101 upgrade response.
```

## 18. The bot's Origin isn't what you expect

```text
symptom: the exploit works on YOUR browser but not the bot's.
cause: the bot's page has a different Origin — a data: URL is 'null',
not your domain; a sandboxed iframe is 'null'.
next: match the exploit's expected Origin to the bot's actual Origin —
the CORS allowlist must include IT.
```

## 19. The exfil hits but the data is truncated

```text
symptom: the OOB hit arrives but the flag is cut off.
cause: a query-string exfil caps ~8KB — a large payload truncates.
next: a POST/ws exfil for large data; or a chunked exfil.
```

## 20. The two-ACAO confusion — a proxy+app double-header

```text
symptom: the response has TWO ACAO headers; the read behavior is
inconsistent.
cause: the app AND the proxy both set ACAO — the browser takes the
last (or rejects on ambiguity).
next: test end-to-end — which ACAO actually applies — and check the
proxy's CORS config.
```

## The failure-mode index — symptom → cause → next

```text
a CORS error           → the actual ACAO gate       → check the real ACAO
200 + public data      → the credential gate         → SameSite/credentials:'include'
request never fires    → the preflight gate          → a simple request
*+ACAC fails           → the invalid combo           → a `*` endpoint — pivot
the exfil fails        → a CSP/reachability gate     → a no-CORS exfil
'null' not allowed     → a strict check              → a different vector
a lookalike fails      → a strict allowlist          → pivot
an airgapped bot       → a delivery failure          → a data:/stored/write-back
the wrong session      → a context failure           → verify the bot's session
the cookie doesn't ride → a SameSite gate            → a Bearer/same-site fetch
a cached answer        → a Vary/Max-Age edge         → a unique origin / fresh ctx
a truncated exfil      → a size cap                  → a POST/ws exfil
```
