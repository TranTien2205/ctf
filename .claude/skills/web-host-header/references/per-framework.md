# Per-framework — every framework the host header gates, exhaustively

The framework map — a framework, the host-header check it gates.

---

## 1. Express / Node — `req.headers.host`, `req.hostname`, `req.get('host')`

```text
Express reads the host from `req.headers.host`, `req.hostname`, or `req.get('host')`.
A reflected host → the app's links point to attacker.com → a stored injection.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 2. Django — `request.get_host()`, `request.META['HTTP_HOST']`

```text
Django reads the host from `request.get_host()` or `request.META['HTTP_HOST']`.
A reflected host → the app's links point to attacker.com → a stored injection.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 3. Flask — `request.host`, `request.headers.get('Host')`

```text
Flask reads the host from `request.host` or `request.headers.get('Host')`.
A reflected host → the app's links point to attacker.com → a stored injection.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 4. Rails — `request.host`, `request.headers['Host']`

```text
Rails reads the host from `request.host` or `request.headers['Host']`.
A reflected host → the app's links point to attacker.com → a stored injection.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 5. Laravel / Symfony — `request.getHost()`, `request.headers.get('host')`

```text
Laravel / Symfony reads the host from `request.getHost()` or `request.headers.get('host')`.
A reflected host → the app's links point to attacker.com → a stored injection.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 6. Spring — `request.getServerName()`, `request.getHeader('Host')`

```text
Spring reads the host from `request.getServerName()` or `request.getHeader('Host')`.
A reflected host → the app's links point to attacker.com → a stored injection.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 7. ASP.NET — `Request.Host`, `Request.Headers["Host"]`

```text
ASP.NET reads the host from `Request.Host` or `Request.Headers["Host"]`.
A reflected host → the app's links point to attacker.com → a stored injection.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 8. Go — `r.Host`, `r.Header.Get("Host")`

```text
Go reads the host from `r.Host` or `r.Header.Get("Host")`.
A reflected host → the app's links point to attacker.com → a stored injection.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 9. FastAPI / Starlette — `request.headers.get('host')`, `request.url.hostname`

```text
FastAPI / Starlette reads the host from `request.headers.get('host')` or
`request.url.hostname`. A reflected host → the app's links point to attacker.com
→ a stored injection.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 10. Next.js / Nuxt — `req.headers.host`, `request.headers.get('host')`

```text
Next.js / Nuxt reads the host from `req.headers.host` or `request.headers.get('host')`.
A reflected host → the app's links point to attacker.com → a stored injection.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 11. Apache / Nginx — `%{HTTP_HOST}`, `$host`

```text
Apache / Nginx reads the host from `%{HTTP_HOST}` or `$host`. A reflected host →
the app's links point to attacker.com → a stored injection.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
```

## 12. The forwarded-header frameworks — `X-Forwarded-Host` / `Forwarded`

```text
a framework reads the host from `X-Forwarded-Host` or `Forwarded` — a reflected
forwarded header → the app's links point to attacker.com → a stored injection.
```

```bash
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'X-Forwarded-Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Forwarded: host=canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
```
