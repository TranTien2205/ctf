# Framework matrix — the proxy layer per stack

The proxy-trust surface per proxy — where the strip and the header live.

---

## 1. nginx — the dominant CTF proxy

```text
nginx's proxy_pass — the proxy adds X-Real-IP, X-Forwarded-For,
X-Forwarded-Host, X-Forwarded-Proto — the app trusts them — a
client-supplied header IS trusted unless the config strips it.
nginx honors Connection — a Connection: keep-alive, X-Real-IP strips
it → the hop-by-hop bypass.
```

## 2. Traefik — the verified card's stack

```text
Traefik's forward — the proxy adds X-Real-IP, X-Forwarded-For,
X-Forwarded-Host, X-Forwarded-Proto — the app trusts them — the
verified card's stack — a Connection: keep-alive, X-Real-IP strips
it → the hop-by-hop bypass → the token_required check skipped.
```

## 3. Apache — the mod_proxy proxy

```text
Apache's mod_proxy — the proxy adds X-Forwarded-For, X-Forwarded-Host,
X-Forwarded-Proto — the app trusts them — a client-supplied header IS
trusted unless the config strips it.
Apache honors Connection — the hop-by-hop bypass.
```

## 4. HAProxy — the load-balancer proxy

```text
HAProxy's forward — the proxy adds X-Forwarded-For, X-Forwarded-Host,
X-Forwarded-Proto — the app trusts them — a client-supplied header IS
trusted unless the config strips it.
HAProxy honors Connection — the hop-by-hop bypass.
```

## 5. Squid — the caching proxy

```text
Squid's forward — the proxy adds X-Forwarded-For — the app trusts it —
a client-supplied header IS trusted unless the config strips it.
Squid honors Connection — the hop-by-hop bypass.
```

## 6. Cloudflare — the CDN edge

```text
Cloudflare's edge — the proxy adds CF-Connecting-IP, CF-Ray, CF-Visitor —
the app trusts them — a client-supplied header IS trusted unless the
config strips it.
Cloudflare's edge strips some headers — a per-rule config.
```

## 7. CloudFront — the AWS edge

```text
CloudFront's edge — the proxy adds X-Amzn-Trace-Id, X-Forwarded-For —
the app trusts them — a client-supplied header IS trusted unless the
config strips it.
```

## 8. Akamai — the enterprise edge

```text
Akamai's edge — the proxy adds True-Client-IP, Akamai-Origin-Hop —
the app trusts them — a client-supplied header IS trusted unless the
config strips it.
```

## 9. Varnish — the VCL proxy

```text
Varnish's backend — the proxy adds X-Forwarded-For — the app trusts
it — a client-supplied header IS trusted unless the VCL strips it.
```

## 10. The per-proxy strip-map — which proxies honor Connection

```text
nginx      → honors Connection — a strip
Traefik    → honors Connection — a strip
Apache     → honors Connection — a strip
HAProxy    → honors Connection — a strip
Squid      → honors Connection — a strip
Cloudflare → a per-rule config — some strips
Varnish    → a per-VCL config — some strips
```

## 11. The per-proxy header-map — which headers each proxy adds

```text
nginx      → X-Real-IP, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Traefik    → X-Real-IP, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Apache     → X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
HAProxy    → X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Squid      → X-Forwarded-For
Cloudflare → CF-Connecting-IP, CF-Ray, CF-Visitor
CloudFront → X-Amzn-Trace-Id, X-Forwarded-For
Akamai     → True-Client-IP, Akamai-Origin-Hop
Varnish    → X-Forwarded-For
```

## 12. The per-proxy falsifier — when the strip doesn't apply

```text
a proxy that doesn't honor Connection's strip → the header passes
through → the app's check reads it → the bypass fails → a different
class.
```
