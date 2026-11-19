# Whitebox hunt — every host-header code pattern, exhaustively

The code map — a pattern, a grep, a meaning.

---

## 1. canonical-URL sinks — the generated links

```bash
grep -rn 'req.headers.host\|req.hostname\|req.get("host")\|req.get(.host.)' --include='*.js' --include='*.ts' .
grep -rn 'request.get_host()\|request.META\[.HTTP_HOST.\]' --include='*.py' .
grep -rn 'request.host\|request.headers.get(.Host.)' --include='*.py' .
grep -rn 'request.host\|request.headers\[.Host.\]' --include='*.rb' .
grep -rn 'request.getHost()\|request.headers.get(.host.)' --include='*.php' .
grep -rn 'request.getServerName()\|request.getHeader(.Host.)' --include='*.java' .
grep -rn 'Request.Host\|Request.Headers\["Host"\]' --include='*.cs' .
grep -rn 'r.Host\|r.Header.Get(.Host.)' --include='*.go' .
grep -rn 'request.headers.get(.host.)\|request.url.hostname' --include='*.py' .
grep -rn 'req.headers.host\|request.headers.get(.host.)' --include='*.js' --include='*.ts' .
grep -rn '%{HTTP_HOST}\|\$host' --include='*.conf' --include='*.cfg' .
grep -rn 'X-Forwarded-Host\|X-Forwarded-Proto\|X-Forwarded-Scheme\|X-Forwarded-Port' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'X-Host\|X-HTTP-Host-Override' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'X-Forwarded-Server\|X-Forwarded-User\|X-Forwarded-Email' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Forwarded' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'X-Original-URL\|X-Rewrite-URL\|X-Forwarded-Path\|X-Forwarded-Prefix\|X-Original-Path\|X-Real-Path' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'canonical\|link rel=.canonical.\|og:url\|sitemap\|robots' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'reset\|password.reset\|forgot.password\|reset.link' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'X-Cache\|X-Served\|Age\|cache.key\|cache-control' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'rewrite\|X-Original-URL\|X-Rewrite-URL\|X-Forwarded-Path\|X-Forwarded-Prefix\|X-Original-Path\|X-Real-Path' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
```

## 2. forwarded-header sinks — the generated links

```bash
grep -rn 'X-Forwarded-Host\|X-Forwarded-Proto\|X-Forwarded-Scheme\|X-Forwarded-Port' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'X-Host\|X-HTTP-Host-Override' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'X-Forwarded-Server\|X-Forwarded-User\|X-Forwarded-Email' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Forwarded' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'X-Original-URL\|X-Rewrite-URL\|X-Forwarded-Path\|X-Forwarded-Prefix\|X-Original-Path\|X-Real-Path' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'canonical\|link rel=.canonical.\|og:url\|sitemap\|robots' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'reset\|password.reset\|forgot.password\|reset.link' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'X-Cache\|X-Served\|Age\|cache.key\|cache-control' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'rewrite\|X-Original-URL\|X-Rewrite-URL\|X-Forwarded-Path\|X-Forwarded-Prefix\|X-Original-Path\|X-Real-Path' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
```

## 3. rewrite sinks — the generated links

```bash
grep -rn 'X-Original-URL\|X-Rewrite-URL\|X-Forwarded-Path\|X-Forwarded-Prefix\|X-Original-Path\|X-Real-Path' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'rewrite\|rewrite\(.path.\)\|rewrite\(.url.\)' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'rewrite\|rewrite\(.path.\)\|rewrite\(.url.\)' --include='*.conf' --include='*.cfg' .
grep -rn 'rewrite\|rewrite\(.path.\)\|rewrite\(.url.\)' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'rewrite\|rewrite\(.path.\)\|rewrite\(.url.\)' --include='*.conf' --include='*.cfg' .
grep -rn 'rewrite\|rewrite\(.path.\)\|rewrite\(.url.\)' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'rewrite\|rewrite\(.path.\)\|rewrite\(.url.\)' --include='*.conf' --include='*.cfg' .
```

## 4. cache sinks — the generated links

```bash
grep -rn 'X-Cache\|X-Served\|Age\|cache.key\|cache-control' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'cache.key\|cache-control\|cache-buster\|cache-buster' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'cache.key\|cache-control\|cache-buster\|cache-buster' --include='*.conf' --include='*.cfg' .
grep -rn 'cache.key\|cache-control\|cache-buster\|cache-buster' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'cache.key\|cache-control\|cache-buster\|cache-buster' --include='*.conf' --include='*.cfg' .
grep -rn 'cache.key\|cache-control\|cache-buster\|cache-buster' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'cache.key\|cache-control\|cache-buster\|cache-buster' --include='*.conf' --include='*.cfg' .
```

## 5. reset sinks — the generated links

```bash
grep -rn 'reset\|password.reset\|forgot.password\|reset.link' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'reset\|password.reset\|forgot.password\|reset.link' --include='*.conf' --include='*.cfg' .
grep -rn 'reset\|password.reset\|forgot.password\|reset.link' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'reset\|password.reset\|forgot.password\|reset.link' --include='*.conf' --include='*.cfg' .
grep -rn 'reset\|password.reset\|forgot.password\|reset.link' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'reset\|password.reset\|forgot.password\|reset.link' --include='*.conf' --include='*.cfg' .
```

## 6. canonical sinks — the generated links

```bash
grep -rn 'canonical\|link rel=.canonical.\|og:url\|sitemap\|robots' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'canonical\|link rel=.canonical.\|og:url\|sitemap\|robots' --include='*.conf' --include='*.cfg' .
grep -rn 'canonical\|link rel=.canonical.\|og:url\|sitemap\|robots' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'canonical\|link rel=.canonical.\|og:url\|sitemap\|robots' --include='*.conf' --include='*.cfg' .
grep -rn 'canonical\|link rel=.canonical.\|og:url\|sitemap\|robots' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'canonical\|link rel=.canonical.\|og:url\|sitemap\|robots' --include='*.conf' --include='*.cfg' .
```

## 7. Location sinks — the generated links

```bash
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.conf' --include='*.cfg' .
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.conf' --include='*.cfg' .
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.conf' --include='*.cfg' .
```

## 8. Set-Cookie sinks — the generated links

```bash
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.conf' --include='*.cfg' .
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.conf' --include='*.cfg' .
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Location\|set-cookie\|Set-Cookie\|cookie.domain' --include='*.conf' --include='*.cfg' .
```

## 9. forwarded sinks — the generated links

```bash
grep -rn 'Forwarded' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Forwarded' --include='*.conf' --include='*.cfg' .
grep -rn 'Forwarded' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Forwarded' --include='*.conf' --include='*.cfg' .
grep -rn 'Forwarded' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'Forwarded' --include='*.conf' --include='*.cfg' .
```

## 10. proxy sinks — the generated links

```bash
grep -rn 'proxy_pass\|proxy_set_header\|proxy_redirect\|proxy_cookie_domain\|proxy_cookie_path' --include='*.conf' --include='*.cfg' .
grep -rn 'proxy_pass\|proxy_set_header\|proxy_redirect\|proxy_cookie_domain\|proxy_cookie_path' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'proxy_pass\|proxy_set_header\|proxy_redirect\|proxy_cookie_domain\|proxy_cookie_path' --include='*.conf' --include='*.cfg' .
grep -rn 'proxy_pass\|proxy_set_header\|proxy_redirect\|proxy_cookie_domain\|proxy_cookie_path' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'proxy_pass\|proxy_set_header\|proxy_redirect\|proxy_cookie_domain\|proxy_cookie_path' --include='*.conf' --include='*.cfg' .
grep -rn 'proxy_pass\|proxy_set_header\|proxy_redirect\|proxy_cookie_domain\|proxy_cookie_path' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
```

## 11. middleware sinks — the generated links

```bash
grep -rn 'middleware\|app.use\|app.use\(.path.\)\|app.use\(.url.\)' --include='*.js' --include='*.ts' .
grep -rn 'middleware\|app.use\|app.use\(.path.\)\|app.use\(.url.\)' --include='*.conf' --include='*.cfg' .
grep -rn 'middleware\|app.use\|app.use\(.path.\)\|app.use\(.url.\)' --include='*.js' --include='*.ts' .
grep -rn 'middleware\|app.use\|app.use\(.path.\)\|app.use\(.url.\)' --include='*.conf' --include='*.cfg' .
grep -rn 'middleware\|app.use\|app.use\(.path.\)\|app.use\(.url.\)' --include='*.js' --include='*.ts' .
grep -rn 'middleware\|app.use\|app.use\(.path.\)\|app.use\(.url.\)' --include='*.conf' --include='*.cfg' .
```

## 12. auth sinks — the generated links

```bash
grep -rn 'auth\|authenticate\|authorize\|login\|logout\|session\|cookie' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'auth\|authenticate\|authorize\|login\|logout\|session\|cookie' --include='*.conf' --include='*.cfg' .
grep -rn 'auth\|authenticate\|authorize\|login\|logout\|session\|cookie' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'auth\|authenticate\|authorize\|login\|logout\|session\|cookie' --include='*.conf' --include='*.cfg' .
grep -rn 'auth\|authenticate\|authorize\|login\|logout\|session\|cookie' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'auth\|authenticate\|authorize\|login\|logout\|session\|cookie' --include='*.conf' --include='*.cfg' .
```

## 13. admin sinks — the generated links

```bash
grep -rn 'admin\|internal\|private\|debug\|preview\|api' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'admin\|internal\|private\|debug\|preview\|api' --include='*.conf' --include='*.cfg' .
grep -rn 'admin\|internal\|private\|debug\|preview\|api' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'admin\|internal\|private\|debug\|preview\|api' --include='*.conf' --include='*.cfg' .
grep -rn 'admin\|internal\|private\|debug\|preview\|api' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'admin\|internal\|private\|debug\|preview\|api' --include='*.conf' --include='*.cfg' .
```

## 14. internal sinks — the generated links

```bash
grep -rn 'internal\|private\|debug\|preview\|api\|admin' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'internal\|private\|debug\|preview\|api\|admin' --include='*.conf' --include='*.cfg' .
grep -rn 'internal\|private\|debug\|preview\|api\|admin' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'internal\|private\|debug\|preview\|api\|admin' --include='*.conf' --include='*.cfg' .
grep -rn 'internal\|private\|debug\|preview\|api\|admin' --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.php' --include='*.java' --include='*.cs' --include='*.go' .
grep -rn 'internal\|private\|debug\|preview\|api\|admin' --include='*.conf' --include='*.cfg' .
```
