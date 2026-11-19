# Attack surface — the complete CORS-read entry-point inventory

Every place a CORS read can enter: the endpoints, the credentials,
the delivery channels, and the exfil paths.

---

## 1. The entry-point classes — where the read begins

```text
an API endpoint — /api/* — the canonical CORS-read target
a page-endpoint — /admin, /dashboard — a DOM-scrape read
a token endpoint — /api/csrf, /api/token — a capability read
a config endpoint — /api/config — a key/secret read
a file endpoint — /api/export — a data read
```

## 2. The credential entry-points — what rides

```text
a session cookie — the canonical; SameSite-gated
an Authorization header — a Bearer; needs a preflight + the token
an API key — a header or a query param
a client cert — mTLS
a Basic-auth credential — an Authorization: Basic header
```

## 3. The origin entry-points — where the page's Origin comes from

```text
an attacker-hosted page — evil.com — a foreign origin
a data: URL — 'null' origin
a sandboxed iframe — 'null' origin
a controlled subdomain — sub.target.com — a trusted origin
a stored page on the target — the target's own origin (same-origin)
```

## 4. The delivery entry-points — how the page reaches the victim

```text
a /report bot endpoint — the canonical
a stored-XSS context — the page IS the target
an open redirect — a trusted-domain bounce
a phishing link — the victim clicks
a subdomain — a CTF-supplied or taken-over sub
```

## 5. The exfil entry-points — how the data leaves

```text
a GET to your listener — the canonical
an img/script GET — a no-CORS channel
a beacon — a fire-and-forget
a websocket — a live channel
a write-back — the data lands on the target
a DOM-writeback — a screenshotting bot
a postMessage — a parent-frame channel
a DNS query — a blocked-domain bypass
```

## 6. The read-target inventory — which endpoints carry the flag

```text
/api/me        — the session's own data — the canonical target
/api/flag      — the flag — the direct target
/api/user      — the user's data
/api/profile   — the profile — may carry the flag
/api/admin     — admin data — a privileged read
/api/token     — a capability — the chain target
/api/csrf      — a CSRF token — the write's key
/api/config    — a config — may carry a key/secret
/api/account   — account data — a balance/flag
/api/settings  — the session's settings
/api/export    — a data export — may carry everything
```

## 7. The defense-surface inventory — what gates the read

```text
the ACAO — which origin may read
the ACAC — may the credential ride
the SameSite — does the cookie attach
the preflight ACAM/ACAH — may the non-simple request fire
the origin-check shape — reflect/allowlist/null/regex/subdomain
the Vary — is the response per-origin
the CSP — does the page's exfil get blocked
the endpoint's auth — does the read even reach the session data
```

## 8. The surface-to-probe table — the inventory's probes

```bash
# the endpoint surface
for ep in /api/me /api/flag /api/token /api/admin /api/config; do
  curl -s -o /dev/null -w "$ep %{http_code}\n" -b "$CJ" "$BASE$ep"; done

# the ACAO surface
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | grep -i 'access-control'

# the cookie surface
curl -s -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'

# the bot surface
grep -rnoiE 'bot|report|visit|admin|puppeteer' <src> | head -10

# the alternate-read surface
curl -s -b "$CJ" "$BASE/api/me?callback=x" | head -1
```

## 9. The surface-map — the read's full path

```text
the page (origin) --fetch--> the endpoint --response--> the page
   |                            |                          |
   +-- the cookie rides --------+                          |
   |                            |                          |
   +-- the ACAO gates the read --+                          |
                                                            |
   +-- the exfil <--------------------------------------------+
```

## 10. The surface-inventory ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-surface: ep=<ep> cred=<cookie|bearer> origin=<o> delivery=<d> exfil=<e>"
```
