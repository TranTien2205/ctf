# Cookie and session — the credential that rides the CORS read

The session cookie is the credential the fetch carries — its
SameSite attribute decides whether the read is credentialed.

---

## 1. The SameSite matrix — does the cookie attach

```text
SameSite=None; Secure   → attaches to cross-site fetches — the
                          credentialed read works.
SameSite=Lax            → attaches on top-level navigation GETs only —
                          a fetch() does NOT carry it — non-credentialed.
SameSite=Strict         → never attaches cross-site — non-credentialed.
no SameSite             → Lax-by-default in modern browsers — non-
                          credentialed for a fetch.
```

```bash
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
#   session=...; SameSite=None; Secure → attaches
#   session=...; SameSite=Lax          → doesn't attach
#   session=...; (no SameSite)         → Lax-by-default
```

## 2. The Secure requirement — SameSite=None needs it

```text
SameSite=None without Secure is REJECTED by the browser — the
cookie must be Secure to ride a cross-site fetch. the pair:
'SameSite=None; Secure' — both required.
```

## 3. The `credentials:'include'` — the fetch's ask

```js
// the fetch must EXPLICITLY ask to send credentials
fetch('https://t/api/me',{credentials:'include'})
// 'include' — always send; 'same-origin' — default, no cross-site;
// 'omit' — never send
```

Without `credentials:'include'` the fetch sends no cookie — the
read is non-credentialed regardless of the cookie's SameSite.

## 4. The XHR equivalent — `withCredentials`

```js
var x=new XMLHttpRequest();
x.open('GET','https://t/api/me');
x.withCredentials=true;   // the credentials:'include' equivalent
x.send();
```

## 5. The cookie-domain edge — a parent/child scope

```text
a cookie scoped to 'target.com' (Domain=target.com) rides requests
to target.com AND its subdomains — a fetch to 'api.target.com'
carries it. a fetch to 'evil.com' never carries it — the cookie's
domain gates where it attaches.
```

## 6. The non-cookie credentials — Bearer/API-key

```text
a Bearer token — needs the fetch to set 'Authorization: Bearer <t>'
— a custom header → a preflight. the token must reach the page —
a readable token endpoint, a leaked JWT, or a known value.
an API key — a query param or a header — the header case needs a
preflight.
```

## 7. The session-cookie-vs-JWT split — where the credential lives

```text
a session COOKIE — the fetch's credentials:'include' carries it;
SameSite-gated.
a JWT in a HEADER — the fetch sets it explicitly; needs the token
in the page's JS; a custom header → preflight.
a JWT in a COOKIE — SameSite-gated like any cookie.
```

## 8. The mTLS client-cert — a non-HTTP credential

```text
a client certificate — the TLS layer carries it — a credentialed
read needs the fetch to present the cert — the cert's presence is
browser/OS-managed, not fetch-controllable.
```

## 9. The cookie-jar distinction — YOUR cookie vs the bot's

```text
the exploit page fetches under the VICTIM's cookie jar — YOUR curl
test uses YOUR cookie; the bot's fetch uses ITS cookie. the read
works if the BOT's cookie attaches — the SameSite applies to the
bot's cookie too.
```

## 10. The multiple-cookie case — which rides

```text
a session cookie + a CSRF cookie + a tracking cookie — the fetch
sends all matching-domain cookies; the read needs the SESSION
cookie to attach — check its specific SameSite.
```

## 11. The SameSite-override edge — a fetch that LOOKS same-site

```text
a fetch from 'app.target.com' to 'api.target.com' — a same-SITE
fetch (registrable domain match) — a Lax cookie attaches! 'same-site'
≠ 'same-origin' — the Lax gate cares about the SITE, not the ORIGIN.
the CORS gate still applies (different origins) but the cookie rides.
```

## 12. The same-site-cross-origin edge — the key insight

```text
a fetch 'app.target.com' → 'api.target.com' is CROSS-ORIGIN (CORS
applies) but SAME-SITE (a Lax cookie attaches). a CORS-open
api.target.com + a Lax-cookie session + a page on app.target.com
reads the credentialed data — the Lax gate doesn't help.
```

## 13. The white-box cookie read

```bash
# the session cookie's attributes
grep -rnoiE 'SameSite|same_site|sameSite|set_cookie|setCookie|cookie.*Secure|secure.*cookie|Domain.*cookie' <src> | head -20
# the cookie's name — the session's identifier
grep -rnoiE 'session|sid|auth|token|jwt|access|refresh' <src> | grep -i 'cookie' | head -10
```

## 14. The cookie-ride decision table

```text
SameSite=None+Secure + credentials:'include'  → credentialed read
SameSite=Lax + credentials:'include'          → non-credentialed fetch
SameSite=Strict + credentials:'include'       → non-credentialed fetch
no credentials:'include'                       → non-credentialed fetch
a Bearer header                               → needs the token + a preflight
a same-site-cross-origin fetch                 → Lax cookie attaches + CORS gates
```
