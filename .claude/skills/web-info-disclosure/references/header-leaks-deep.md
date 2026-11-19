# Deep header analysis — beyond Server/X-Powered-By

The secondary headers: ETag shapes, X-Cache, Via, timing headers, framework session-cookie names — each a fingerprint.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| ETag 'W/"len-mtime"' | Node/Express etag style | framework hint |
| X-Cache: HIT/MISS + Via | cache/proxy topology | smuggling leads |
| Set-Cookie name=laravel_session|connect.sid|JSESSIONID | framework fingerprint | framework-debug paths |
| X-Backend-* or X-Served-By | backend naming | vhost/topology |

## Steps

1. Collect headers from every response — Set-Cookie names fingerprint the framework.
2. ETag and cache headers reveal the serving stack and caching layer.
3. Via/X-Forwarded-* trace the proxy chain — each hop is a surface.
4. Cookie names: laravel_session (PHP), connect.sid (Express), JSESSIONID (Java), session (Django/Flask).

## Falsifier

Falsifier — stripped headers and generic cookies: framework must come from body/error analysis.

## Traps

- Cookie names are the most reliable framework fingerprint — can't be stripped as easily.
- X-Cache/Via chains map to request-smuggling's proxy topology.
- Duplicate/conflicting headers are themselves a finding.

## Commands

```bash
curl -s -D- -o /dev/null '$BASE/' | sort
```

## Cross-references

`header-disclosure.md` · `response-anatomy.md`
