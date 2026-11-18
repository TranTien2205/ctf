# Host-header SSRF — the trusted-header fetch-source

The url isn't a param — it's a HEADER the app trusts to build a
fetch — Host, X-Forwarded-Host, Referer, X-Original-URL. The
header-injection reaches the fetch-target — the host-header attack
meets SSRF.

---

## 1. The header-surface — which headers feed a fetch

```text
Host:                    — the request-host — the app may fetch
                           "the host you named" — or build urls
                           from it — password-reset-links, cache-
                           keys, absolute-urls
X-Forwarded-Host:        — the proxy-set host — the app trusts it —
                           the host-header attack's classic —
                           the app uses it for url-generation or
                           a fetch
X-Forwarded-Server:      — the server-name — the proxy-set
X-Forwarded-Domain:      — the domain
X-Host:                  — the host-header alias
X-Original-Host:         — the original-host
X-Original-URL:          — the original-url — the rewrite-headers
X-Rewrite-URL:           — the rewrite-target — the proxy passes
                           the "real" url — the app uses it
Referer:                 — the referring-url — analytics/webhooks
                           may re-fetch it — the referer-fetch —
                           the app crawls the referer
X-Forwarded-Uri:         — the uri
X-Forwarded-Proto:       — the scheme — http-vs-https tricks
X-Proxy-Url:             — a proxy-target
X-Target-Url:            — a target-url
X-Api-Url / X-Backend-Url — the backend-target
X-Callback-Url:          — the callback
X-Webhook-Url:           — the webhook
Origin:                  — the origin-header — cors-adjacent — a
                           fetch may use it
```

## 2. The host-header fetch — the mechanism

```text
the app does: fetch("http://" + req.headers["X-Forwarded-Host"] + path)
   — the header IS the fetch-target — the host-header controls the
     host — the fetch goes to your header-value — the host-header
     is the url
   — this is SSRF via header — the class is web-ssrf (server-side
     fetch of attacker-controlled) — the host-header is the vector
   — the "password-reset-link poisoning" uses this — the reset-mail
     links to your-host — the mail-target is the user — different
     from ssrf — the host-header class covers the link-poisoning
   — the FETCH is the ssrf — the link-poison is the host-header —
     the same header, different sinks
```

## 3. The Referer-fetch — the analytics-crawl

```text
the app crawls the Referer — "where did you come from" — the
  analytics-service fetches the referer-url → the referer is a
  fetch-target → put the internal-url in Referer → the analytics
  fetches it → the internal-content in the analytics-record —
  the deferred-referer-fetch
```

## 4. The X-Forwarded-* trust-model

```text
the app trusts X-Forwarded-* headers because "the proxy sets
them" — but the proxy may NOT overwrite a client-sent one — the
client sends X-Forwarded-Host: internal → the proxy passes it →
the app reads it → the header reaches the fetch — the proxy's
header-handling is the gate — the proxy-strip-test:
  send X-Forwarded-Host: your-host → does the app use yours or
  the proxy's? — if yours → the header is client-controlled →
  the fetch-target is yours
```

## 5. The cache-poisoning intersection

```text
the Host/X-Forwarded-Host is often a cache-KEY — a fetch keyed
on the host — the cached-response is stored under your host —
the next-viewer gets your-poisoned-entry — the web-cache-poisoning
class — the host-header + the cache — the fetch-poisons the cache
— different class boundary — the host-header + cache-key +
  stored-response → cache-poison — see web-cache-poisoning
```

## 6. The absolute-uri in the request-line

```text
GET http://internal/x HTTP/1.1   — the absolute-form request-line —
  the proxy-request-shape — a proxy-app treats the request-target
  as a url → the request-line IS the fetch-target — the absolute-
  uri — the proxy-handlers' standard form — the app that fronts
  a proxy reads it
```

## 7. The header-to-url pipeline — the trace

```text
the path: header → app-logic → fetch-target
  - header → the app's url-builder → the fetch — the composed-url
  - header → the app's redirect → the Location — the redirect-target
  - header → the app's cache-key → the keyed-content
  - header → the app's "my-origin" → the outbound-request's Host —
    the Host-header the app SENDS — the internal-request's Host
    is yours — vhost-routing!
```

## 8. The host-header + the fetch — the chains

```text
chain-1: X-Forwarded-Host: internal → app fetches internal —
  the direct-header-ssrf
chain-2: X-Forwarded-Host: attacker.com → app fetches you → the
  callback proves the header is the target → then the internal-
  url — the header is controllable → the internal-target
chain-3: Host: admin.internal → the app vhosts — the admin-vhost
  served — the vhost-routing — the host-header picks the vhost
chain-4: the host-header + a redirect — the header → the app's
  redirect → the redirect-target — the chain-of-trust
```

## 9. The detection — which headers feed a fetch

```text
the map:
  - send X-Forwarded-Host: YOUR-CALLBACK → the callback fires →
    the header is the fetch-target → confirmed
  - send Host: YOUR → the app uses it? — the absolute-url in the
    response, the reset-link's domain, the callback
  - send Referer: YOUR → the analytics-fetch
  - send X-Original-URL: YOUR — the rewrite-headers
each header to the canary — the ones that fire are the surface —
the header-as-fetch-target map
```

## 10. The sibling-classes — which class applies

```text
- host-header → server-FETCH → web-ssrf (this skill)
- host-header → url-generation → link-poisoning → web-host-header
- host-header → cache-key → cache-poison → web-cache-poisoning
- host-header → redirect-target → open-redirect → web-open-redirect
- host-header → password-reset-link → account-takeover →
  web-auth-session
the SINK decides the class — the same header, different sinks
```

## 11. The proxy-strip — the gate

```text
the proxy decides which client-headers pass:
  nginx:    proxy_set_header X-Forwarded-Host $host; — overwrites —
            client-sent dies — the proxy's version wins
  apache:   RequestHeader set X-Forwarded-Host ... — overwrites
  no-strip: the proxy passes the client's — the header is yours
the test — send X-Forwarded-Host: YOUR → the callback-fires? →
  the header survives → the gate is open
```

## 12. The header-shape tricks — the same-families

```text
the header-values take the same url-tricks — the header carries
the full url-syntax — the @/#/?/encoding/port tricks work in the
header-position — X-Forwarded-Host: internal@allowed — the host-
header's own parsing
```
