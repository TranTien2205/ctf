# Framework matrix deep — the per-proxy behavior, exhaustively

The per-proxy matrix — which headers each proxy adds, which each strips.

---

## 1. nginx — the most common reverse proxy

```nginx
# the nginx config — a proxy that adds headers
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Proto $scheme;
# a client-supplied Connection: keep-alive, X-Real-IP strips X-Real-IP
# before forwarding — the hop-by-hop bypass is the vector
```

```text
nginx adds: X-Real-IP, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
nginx strips: a header named in Connection — the hop-by-hop bypass
nginx passes: a client-supplied proxy header (unless the config strips it)
```

## 2. Traefik — the verified card's proxy

```text
Traefik adds: X-Real-IP, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Traefik strips: a header named in Connection — the hop-by-hop bypass
Traefik's strip: the verified card's mechanism — the proxy's own X-Real-IP
  stripped → the app treats the request as local → the token_required
  check bypassed
```

## 3. Apache — the mod_proxy pattern

```apache
# the Apache config — a proxy that adds headers
ProxyPreserveHost On
RequestHeader set X-Forwarded-Proto "https"
RequestHeader set X-Forwarded-For "%{REMOTE_ADDR}e"
```

```text
Apache adds: X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Apache strips: a header named in Connection — the hop-by-hop bypass
Apache passes: a client-supplied proxy header (unless the config strips it)
```

## 4. HAProxy — the TCP-layer proxy

```text
HAProxy adds: X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
HAProxy strips: a header named in Connection — the hop-by-hop bypass
HAProxy passes: a client-supplied proxy header (unless the config strips it)
```

## 5. Cloudflare — the edge proxy

```text
Cloudflare adds: CF-Connecting-IP, CF-Ray, CF-Visitor, CF-IPCountry,
               X-Forwarded-For, X-Forwarded-Proto
Cloudflare strips: a client-supplied CF-* — the CDN's own headers
Cloudflare passes: a client-supplied X-Forwarded-* — the CDN's forwarded
```

## 6. CloudFront — the AWS edge

```text
CloudFront adds: X-Amzn-Trace-Id, X-Forwarded-For, X-Forwarded-Host,
               X-Forwarded-Proto, CloudFront-Viewer-Country
CloudFront strips: a client-supplied X-Amzn-* — the CDN's own headers
CloudFront passes: a client-supplied X-Forwarded-* — the CDN's forwarded
```

## 7. Akamai — the enterprise edge

```text
Akamai adds: True-Client-IP, Akamai-Origin-Hop, X-Forwarded-For
Akamai strips: a client-supplied True-Client-IP — the CDN's own header
Akamai passes: a client-supplied X-Forwarded-* — the CDN's forwarded
```

## 8. Varnish — the caching proxy

```text
Varnish adds: X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Varnish strips: a header named in Connection — the hop-by-hop bypass
Varnish passes: a client-supplied proxy header (unless the config strips it)
```

## 9. Squid — the forward/reverse proxy

```text
Squid adds: X-Forwarded-For
Squid strips: a header named in Connection — the hop-by-hop bypass
Squid passes: a client-supplied proxy header (unless the config strips it)
```

## 10. The per-proxy strip-map — which headers each strips on Connection

```text
a proxy strips a header named in Connection — the hop-by-hop bypass —
the strip is the mechanism — the proxy's own header (the one the app
trusts) is the strip's target — the app's missing-header fallback is
the bypass's reach.
```

## 11. The per-proxy pass-map — which headers each passes

```text
a proxy passes a client-supplied proxy header unless the config strips
it — the client-supplied bypass is the vector — the app's trust check
reads the client-supplied header's value — a forged local IP → a local
request → the trust check bypassed.
```

## 12. The per-proxy verify-map — which headers each verifies

```text
a proxy that verifies the header it added → a client-supplied header is
rejected → the client-supplied bypass fails → the hop-by-hop bypass is
the vector.
```

## 13. The per-proxy normalization-map — which paths each normalizes

```text
a proxy normalizes a path before forwarding — a traversal, an encoding,
a case difference — the app's route reads the normalized path — a
normalization differential — the proxy's check reads a different path
than the app's.
```

## 14. The per-proxy boundary-map — which checks each gates

```text
a proxy's header gates a check — an authenticated-only route, an
internal route, a restricted endpoint — the app's trust check reads
the missing or client-supplied header's effect — the differential's
reach is the gated route.
```

## 15. The matrix's falsifier — when the proxy is dead

```text
a proxy that doesn't strip its own header → the hop-by-hop bypass fails
a proxy that strips a client-supplied header → the client-supplied
  bypass fails → the hop-by-hop bypass is the vector
a proxy that verifies the header it added → the client-supplied bypass
  fails → the hop-by-hop bypass is the vector
the proxy and the app normalize the same way → no confusion
```
