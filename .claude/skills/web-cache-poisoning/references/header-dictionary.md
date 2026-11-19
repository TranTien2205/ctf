# Header dictionary — every header the cache may ignore

The complete list of headers — the unkeyed-input surface.

---

## 1. The X-Forwarded-* family — the proxy-trust headers

```text
X-Forwarded-Host        — the app's URLs use YOUR host — a URL-rewrite
X-Forwarded-Scheme      — the app's URLs use YOUR scheme — a downgrade
X-Forwarded-Proto       — a proto-honoring input
X-Forwarded-Port        — a port input
X-Forwarded-For         — a client-IP input (usually keyed if read)
X-Forwarded-Uri         — a URI input
X-Forwarded-Server      — a server-name input
X-Forwarded-Domain      — a domain input
X-Forwarded-Ssl         — an ssl-honoring input
```

## 2. The X-Original-*/X-Rewrite-* family — the path-rewrite headers

```text
X-Original-URL          — the app honors it — a rewritten path
X-Rewrite-URL           — a rewrite-honoring input
X-Original-Request-URI  — a request-URI input
X-Original-Path         — a path input
X-Original-Host         — a host input
```

## 3. The reflection family — the headers the app echoes

```text
User-Agent              — the app personalizes on it — a per-UA input
Referer                 — the app reflects it — a reflected input
Accept-Language         — the app localizes on it — a localized input
Accept-Charset          — the app decodes on it — a charset input
Accept-Encoding         — the app compresses on it — a per-encoding input
Accept                  — the app varies on it — a per-accept input
X-Requested-With        — the app reflects it
Origin                  — the app reflects it
```

## 4. The auth family — the session-state headers

```text
Cookie                  — the session cookie (usually keyed via Vary)
Authorization           — the auth header (usually keyed via Vary)
X-Auth-Token            — an auth-token input
X-API-Key               — an API-key input
```

## 5. The client-IP family — the IP headers

```text
X-Forwarded-For         — the client IP (usually keyed if read)
X-Real-IP               — a client-IP input
X-Client-IP             — a client-IP input
CF-Connecting-IP        — a Cloudflare client-IP
True-Client-IP          — an Akamai client-IP
X-Remote-IP             — a remote-IP input
```

## 6. The method family — the method-override headers

```text
X-HTTP-Method-Override  — a method-override input
X-Original-Method       — a method-override input
X-Method-Override       — a method-override input
```

## 7. The custom family — the app-specific headers

```text
X-Custom-<name>         — a custom app header
X-Debug                 — a debug input
X-Preview               — a preview input
X-Frame-Options         — a framing input
X-Forwarded-Email       — an email input
X-Forwarded-User        — a user input
```

## 8. The Forwarded family — the RFC 7239 header

```text
Forwarded: for=<ip>            — a client-IP input
Forwarded: host=<host>         — a host input
Forwarded: proto=<scheme>      — a scheme input
Forwarded: by=<proxy>          — a proxy input
```

## 9. The header-to-effect map — which header produces which effect

```text
X-Forwarded-Host        → URL-rewrite (the app's links use YOUR host)
X-Forwarded-Scheme      → scheme-downgrade (the links use http)
X-Original-URL          → path-rewrite (the app serves a different route)
User-Agent              → per-UA response (a mobile-vs-desktop confusion)
Referer                 → reflected input (the page echoes it)
Accept-Language         → localized response (a per-language copy)
Accept-Charset          → charset confusion (a charset injection)
Accept-Encoding         → per-encoding copy (a compression confusion)
Cookie                  → per-session copy (usually keyed via Vary)
X-Forwarded-For         → per-IP copy (usually keyed if read)
X-HTTP-Method-Override  → method-override (a per-method confusion)
```

## 10. The header-keyedness check — send it and confirm the store

```bash
# for each candidate header — send it → check the stored copy
for h in 'X-Forwarded-Host' 'X-Original-URL' 'X-Rewrite-URL' 'X-Forwarded-Scheme' 'User-Agent' 'Referer' 'Accept-Language' 'Accept-Charset' 'X-Forwarded-Server' 'X-Host' 'X-Real-IP' 'X-HTTP-Method-Override' 'X-Forwarded-Proto'; do
  curl "$BASE/page?cb=<unique>" -H "$h: <marker>"
  curl "$BASE/page?cb=<unique>" | grep '<marker>' && echo "$h UNKEYED"
done
```

## 11. The header's keyedness — the Vary and the config

```text
a Vary'd header → keyed → a per-input entry.
a header in proxy_cache_key → keyed → a per-input entry.
a header in vcl_hash → keyed → a per-input entry.
a header not in the key → unkeyed → the poisoning vector.
```

## 12. The falsifier — when nothing is unkeyed

```text
every candidate header IS keyed → no unkeyed input → no poisoning
vector → a different class.
```
