# Headers deep — the full request-header surface for CSRF

Every header on a cross-origin request — what the browser sets, what
you can control, and what the server reads as a gate.

---

## 1. The headers a form sends

```text
POST /x HTTP/1.1
Host: target.com
Origin: https://attacker.com          ← set on cross-origin POST
Referer: https://attacker.com/page    ← per referrer-policy
Content-Type: application/x-www-form-urlencoded  ← or text/plain or multipart
Cookie: session=...                   ← per SameSite
Sec-Fetch-Site: cross-site            ← the Fetch Metadata set
Sec-Fetch-Mode: navigate              ← a form nav is 'navigate'
Sec-Fetch-Dest: document              ← the destination
Sec-Fetch-User: ?1                    ← if user-initiated
```

## 2. Fetch Metadata — the `Sec-Fetch-*` gate

```text
Sec-Fetch-Site: cross-site | same-site | same-origin | none
Sec-Fetch-Mode: navigate | cors | no-cors | websocket | ...
Sec-Fetch-Dest: document | iframe | image | script | empty | ...
Sec-Fetch-User: ?1 (user-initiated) — absent on a script-fired nav
```

A server can CSRF-gate on `Sec-Fetch-Site` — reject when it's
`cross-site`. But the bypass shapes:

| `Sec-Fetch-Site` value | When sent |
|---|---|
| `same-origin` | the request is same-origin — a stored page |
| `same-site` | a sibling-subdomain request |
| `cross-site` | a different-site request — gated |
| `none` | a user-typed URL, a bookmark, a direct nav — no site context |

The `none` value is the open case — a request with NO site context
(a typed URL, a redirect that loses it) sends `none` and bypasses a
`cross-site`-only check.

## 3. The `none` bypass — a redirect that launders the site

```html
<!-- a redirect that loses the site context -->
<a href="https://t/x?a=1">x</a>
<!-- a direct nav sends Sec-Fetch-Site: none — no site context -->
```

```text
the server checks 'if Sec-Fetch-Site == cross-site: reject' —
a top-level typed URL or a redirect-through-another-hop sends
'none' — the check doesn't fire. a javascript: or data: nav may
also send none.
```

## 4. The headers you CAN'T set — the browser's own

```text
these are browser-controlled — JS can't set them:
- Origin (always browser-set on cross-origin non-GET)
- Referer (set by referrer-policy, suppressible but not spoofable
  to an arbitrary value via JS)
- Cookie (the browser attaches; you can't forge it in a header)
- Sec-Fetch-* (browser-computed)
- Host (the URL decides)
- User-Agent (page-level — a fetch can set a custom UA? no — the
  UA header is forbidden in fetch)
- Content-Length (computed)
```

## 5. The headers you CAN set — the safelisted set

```text
in a no-cors fetch or a form, you can only send 'CORS-safelisted'
headers:
- Accept, Accept-Language, Content-Language
- Content-Type — restricted to text/plain, urlencoded, multipart
- Range
any other header (X-CSRF-Token, Authorization, X-Custom) triggers
a preflight — which fails without CORS-open.
```

A CSRF can't send a custom header without a preflight — so a header-
checked token (`X-CSRF-Token`) can't be shipped cross-origin unless
the endpoint also reads it from a body field.

## 6. The Content-Type header — the carrier decision

```text
a form sets Content-Type to its enctype:
- application/x-www-form-urlencoded (default)
- text/plain
- multipart/form-data
a fetch in no-cors can set Content-Type to the same three.
a custom content-type (application/json, application/xml) needs a
preflight — unshippable in no-cors.
```

## 7. The Cookie header — the ambient credential

```text
the browser attaches cookies per the SameSite/Domain/Path rules —
you can't add a Cookie header, but the browser sends the real ones.
the CSRF uses the ambient cookie — the whole point.
```

## 8. The Origin header — when it appears

```text
- a cross-origin POST/PUT/DELETE → Origin: https://attacker.com
- a same-origin request → Origin often absent on GET
- a fetch always sends Origin on non-GET
- a form POST sends Origin cross-origin
- a GET nav may omit Origin
- a data:/opaque origin → Origin: null
```

The `Origin` absence-on-GET and the `null`-on-opaque are the bypass
levers — a check that requires Origin present-but-correct fails open
on a GET or a null.

## 9. The Referer header — the suppressible one

```text
- set by the page's referrer-policy
- <meta name=referrer content=no-referrer> suppresses it
- a Referrer-Policy: no-referrer response suppresses it
- a data:/about:/javascript: origin sends no Referer
- you can't set it to an arbitrary value — only suppress it
```

The absent-Referer-bypass works when the check is `if (!referer)
allow` — suppress it and the check opens.

## 10. The proxy/trust headers — the spoofable layer

```text
X-Forwarded-For, X-Real-IP, X-Forwarded-Host, Forwarded —
these are SET BY PROXIES, not the browser. a CSRF page can't set
them (they're not safelisted and a custom header needs preflight).
but the GATE that reads them is spoofable by a DIRECT request —
just not by a browser CSRF.

the card's lesson: a remote_ip gate reads the SOCKET, not these —
the headers can't carry a CSRF to a socket-peer gate.
```

## 11. The request-header audit — what the server reads

```bash
# what headers does the endpoint's check read?
grep -rnoE 'headers\.|get_header|request\.headers|HTTP_|referer|origin|sec-fetch|x-forwarded|x-real-ip|host' \
  <src> | head -30
```

## 12. The header→gate table

| Gate reads | The CSRF bypass |
|---|---|
| `Origin` exact-match | can't spoof — but absent-Origin or null |
| `Origin` substring | a target.com.evil.com origin |
| `Referer` present+correct | can't spoof — but no-referrer strips it |
| `Sec-Fetch-Site` cross-site | a none-context nav or a stored page |
| `X-CSRF-Token` custom header | can't ship — needs a body-field fallback |
| `Cookie` ambient | SameSite decides |
| `X-Forwarded-*` | not a browser CSRF vector — a direct-request one |
| `Content-Type` json | can't ship — text/plain the carrier |

## 13. The falsifier

```text
the endpoint requires a header the browser won't let you set (a
custom X-CSRF-Token) AND doesn't accept it via a body field AND
preflight fails — the CSRF can't produce the required header. the
header gate holds; pivot.
```
