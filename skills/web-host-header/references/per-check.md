# Per-check — every check the host header gates, exhaustively

The check map — a header the app reads, a check the header gates.

---

## 1. The canonical-URL check — the generated links

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
```

## 2. The reset-link check — the account takeover

```bash
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
```

## 3. The Location check — the open redirect

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 4. The Set-Cookie check — the session fixation

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
```

## 5. The cache-key check — the cache-poisoning feed

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
```

## 6. The rewrite check — the ACL bypass

```bash
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
```

## 7. The forwarded check — the RFC 7239 form

```bash
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
```

## 8. The duplicated Host check — the parsing differential

```bash
curl -s -D - -H 'Host: good.example' -H 'Host: evil.example' "$BASE/"
curl -s -D - -H 'Host: evil.example' -H 'Host: good.example' "$BASE/"
```

## 9. The malformed Host check — the parsing edge

```bash
curl -s -D - -H 'Host: evil.example:80' "$BASE/"   # a forged port
curl -s -D - -H 'Host: evil.example.' "$BASE/"   # a trailing dot
curl -s -D - -H 'Host: ' "$BASE/"   # an empty host
```

## 10. The absolute-URI check — the request-line differential

```bash
curl -s -D - "$BASE/" --request-target 'http://evil.example/'   # an absolute-URI
```

## 11. The multi-header check — the combined injection

```bash
curl "$BASE/api/internal" -H 'Host: evil.example' -H 'X-Internal: true'   # a host + an internal
curl "$BASE/api/admin" -H 'Host: evil.example' -H 'X-Admin: true'   # a host + an admin
curl "$BASE/api/user" -H 'Host: evil.example' -H 'X-Forwarded-User: admin'   # a host + a user
```

## 12. The multi-proxy check — the chained normalization

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the edge strips it; the origin doesn't
```
