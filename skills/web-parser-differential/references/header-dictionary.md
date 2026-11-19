# Header dictionary — every proxy header, in one corpus

The complete list of headers the proxy may add, strip, or trust.

---

## 1. The X-Forwarded-* family — the proxy's forwarded headers

```text
X-Forwarded-For         → the client IP — a local-vs-remote check
X-Forwarded-Host        → the app's host — a URL-rewrite
X-Forwarded-Scheme      → the app's scheme — a scheme check
X-Forwarded-Proto       → the app's proto — a proto check
X-Forwarded-Port        → the app's port — a port check
X-Forwarded-Uri         → the app's URI — a URI check
X-Forwarded-Server      → the server name — a server check
X-Forwarded-Domain      → the domain — a domain check
X-Forwarded-Ssl         → an ssl flag — an ssl check
X-Forwarded-Email       → the client email — an auth check
X-Forwarded-User        → the client user — an auth check
```

## 2. The X-Original-*/X-Rewrite-* family — the path-rewrite headers

```text
X-Original-URL          → a rewritten path — a route check
X-Rewrite-URL           → a rewritten path — a route check
X-Original-Request-URI  → a rewritten request-URI — a route check
X-Original-Path         → a rewritten path — a route check
X-Original-Host         → a rewritten host — a host check
X-Original-Method       → a method-override — a method check
```

## 3. The client-IP family — the IP headers

```text
X-Real-IP               → the client IP — a local-vs-remote check
X-Forwarded-For         → the client IP — a local-vs-remote check
X-Client-IP             → the client IP — a local-vs-remote check
X-Remote-IP             → the client IP — a local-vs-remote check
CF-Connecting-IP        → a Cloudflare client IP
True-Client-IP          → an Akamai client IP
Forwarded: for=<ip>     → an RFC 7239 client IP
```

## 4. The internal/admin family — the flag headers

```text
X-Internal              → an internal flag — an internal-route check
X-Admin                 → an admin flag — an admin check
X-Debug                 → a debug flag — a debug check
X-Preview               → a preview flag — a preview check
X-Authenticated         → an auth flag — an auth check
```

## 5. The host/scheme family — the URL-rewrite headers

```text
X-Forwarded-Host        → the app's host — a URL-rewrite
X-Host                  → the app's host — a URL-rewrite
X-Forwarded-Scheme      → the app's scheme — a scheme check
X-Forwarded-Proto       → the app's proto — a proto check
Forwarded: host=<host>  → an RFC 7239 host
Forwarded: proto=<scheme> → an RFC 7239 scheme
```

## 6. The method family — the method-override headers

```text
X-HTTP-Method-Override  → a method-override — a method check
X-Original-Method       → a method-override — a method check
X-Method-Override       → a method-override — a method check
```

## 7. The Forwarded family — the RFC 7239 header

```text
Forwarded: for=<ip>            → the client IP
Forwarded: host=<host>         → the app's host
Forwarded: proto=<scheme>      → the app's scheme
Forwarded: by=<proxy>          → the proxy ID
```

## 8. The CDN family — the CDN-specific headers

```text
CF-Connecting-IP        → a Cloudflare client IP
CF-Ray                  → a Cloudflare request ID
CF-Visitor              → a Cloudflare visitor
True-Client-IP          → an Akamai client IP
Akamai-Origin-Hop       → an Akamai hop
X-Amzn-Trace-Id         → an AWS trace ID
```

## 9. The hop-by-hop family — the Connection-controlled headers

```text
Connection: keep-alive, X-Real-IP        → the proxy strips X-Real-IP
Connection: keep-alive, X-Forwarded-For  → the proxy strips X-Forwarded-For
Connection: keep-alive, X-Forwarded-Host → the proxy strips X-Forwarded-Host
Connection: keep-alive, X-Internal       → the proxy strips X-Internal
Connection: keep-alive, X-Admin          → the proxy strips X-Admin
```

## 10. The header-to-effect map — which header produces which effect

```text
X-Real-IP          → a local-vs-remote check (the app's trust check)
X-Forwarded-For    → a local-vs-remote check (the app's trust check)
X-Forwarded-Host   → a URL-rewrite (the app's links use YOUR host)
X-Forwarded-Scheme → a scheme-downgrade (the app's links use http)
X-Original-URL     → a path-rewrite (the app serves a different route)
X-Internal         → an internal-route check (an internal flag)
X-Admin            → an admin check (an admin flag)
```

## 11. The header-strip sweep — which headers the proxy strips

```bash
# the header-strip sweep — which headers the proxy strips
for h in 'X-Real-IP' 'X-Forwarded-For' 'X-Forwarded-Host' 'X-Internal' 'X-Admin' 'X-Original-URL' 'X-Rewrite-URL' 'X-Forwarded-Scheme' 'X-Forwarded-Proto' 'X-Forwarded-Port' 'X-Forwarded-Uri' 'X-Forwarded-Server' 'X-Client-IP' 'X-Host' 'X-Forwarded-Email' 'X-Forwarded-User' 'X-Debug' 'X-Preview' 'X-Authenticated'; do
  curl "$BASE/api/restricted" -H "Connection: keep-alive, $h"
done
```

## 12. The falsifier — when nothing is trusted

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
```
