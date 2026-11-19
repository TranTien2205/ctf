# Input dictionary — every unkeyed input, in one corpus

The complete list of request parts the app may read but the cache may ignore.

---

## 1. The forwarded-host family — the URL-rewrite inputs

```text
X-Forwarded-Host        — the app's absolute URLs use YOUR host
X-Host                  — a host-honoring app's input
X-Forwarded-Server      — a server-name input
X-Forwarded-Domain      — a domain input
Forwarded: host=...     — the RFC 7239 Forwarded header
Host                    — the request's Host (usually keyed; check)
```

## 2. The forwarded-scheme family — the scheme/port inputs

```text
X-Forwarded-Scheme      — the app's URLs use YOUR scheme (http/https)
X-Forwarded-Proto       — a proto-honoring app's input
X-Forwarded-Port        — a port input
X-Forwarded-Uri         — a URI input
X-Forwarded-Ssl         — an ssl-honoring input (on/off)
Forwarded: proto=...    — the RFC 7239 Forwarded proto
```

## 3. The forwarded-URL family — the path-rewrite inputs

```text
X-Original-URL          — the app honors it — a rewritten path
X-Rewrite-URL           — a rewrite-honoring app's input
X-Original-Request-URI  — a request-URI input
X-Forwarded-Uri         — a URI input
X-Original-Path         — a path input
```

## 4. The forwarded-IP family — the IP inputs

```text
X-Forwarded-For         — a per-IP input (usually keyed if read)
X-Real-IP               — a client-IP input
X-Client-IP             — a client-IP input
CF-Connecting-IP        — a Cloudflare client-IP input
True-Client-IP          — an Akamai client-IP input
Forwarded: for=...      — the RFC 7239 Forwarded for
```

## 5. The reflection family — the headers the app echoes

```text
User-Agent              — the app personalizes on it — a per-UA input
Referer                 — the app reflects it — a reflected input
Accept-Language         — the app localizes on it — a localized input
Accept-Charset          — the app decodes on it — a charset input
Accept-Encoding         — the app compresses on it — a per-encoding input
Accept                  — the app varies on it — a per-accept input
X-Requested-With        — the app reflects it
Origin                  — the app reflects it (a CORS interplay)
```

## 6. The cookie family — the per-cookie inputs

```text
Cookie: theme=<v>       — a theme-preference cookie
Cookie: lang=<v>        — a language cookie
Cookie: session=<v>     — a session cookie (usually keyed via Vary)
Cookie: <custom>=<v>    — a custom app cookie
```

## 7. The param family — the per-param inputs

```text
?utm=<v>                — a tracking param (usually keyed)
?fbclid=<v>             — a tracking param
?gclid=<v>              — a tracking param
?_=<v>                  — a cache-buster param (keyed by design)
?cb=<v>                 — a cache-buster param
?<custom>=<v>           — a custom app param
```

## 8. The path family — the normalization inputs

```text
/static/../admin        — a path-traversal normalization boundary
/%2e%2e/admin           — an encoded path
/static/%2e%2e/admin    — a mixed-encoding path
/Page                   — a case-normalization boundary
/page/                  — a trailing-slash boundary
/page//admin            — a double-slash boundary
```

## 9. The auth family — the deception inputs

```text
Cookie: session=<auth>  — an authenticated request — the page's key
Authorization: <auth>   — an auth header — the page's key
```

```text
the auth state IS the deception's surface — the cache keys on the
URL, not the auth — the stored copy is the privileged page.
```

## 10. The method family — the per-method inputs

```text
GET                     — the usual keyed method
POST                    — a POST keyed separately or uncached
HEAD                    — a HEAD keyed separately
OPTIONS                 — an OPTIONS keyed separately
```

## 11. The custom-header family — the app-specific inputs

```text
X-Custom-<name>         — a custom app header
X-Debug                 — a debug input
X-Preview               — a preview input
X-Original-Method       — a method-override input
X-HTTP-Method-Override  — a method-override input
X-Frame-Options         — a framing input
```

## 12. The input-to-effect map — which input produces which effect

```text
X-Forwarded-Host        → URL-rewrite (the app's links use YOUR host)
X-Forwarded-Scheme      → scheme-downgrade (the links use http)
X-Original-URL          → path-rewrite (the app serves a different route)
User-Agent              → per-UA response (a mobile-vs-desktop confusion)
Referer                 → reflected input (the page echoes it)
Accept-Language         → localized response (a per-language copy)
Accept-Charset          → charset confusion (a charset injection)
Accept-Encoding         → per-encoding copy (a compression confusion)
Cookie: theme           → per-cookie response (a theme confusion)
?utm                    → tracking-param copy (a keyed-vs-unkeyed check)
/static/../admin        → route confusion (a normalization boundary)
```

## 13. The input-keyedness check — send it and confirm the store

```bash
# for each candidate input — send it → check the stored copy
for h in 'X-Forwarded-Host' 'X-Original-URL' 'User-Agent' 'Referer' 'Accept-Language' 'Accept-Charset' 'X-Forwarded-Scheme' 'X-Host'; do
  curl "$BASE/page?cb=<unique>" -H "$h: <marker>"
  curl "$BASE/page?cb=<unique>" | grep '<marker>' && echo "$h UNKEYED"
done
```

## 14. The falsifier — when nothing is unkeyed

```text
every candidate input IS keyed → no unkeyed input → no poisoning
vector → a different class.
```
