# Deep header analysis — beyond Server/X-Powered-By — checklist

The secondary headers: ETag shapes, X-Cache, Via, timing headers, framework session-cookie names — each a fingerprint.

## Checklist

- [ ] Collect headers from every response — Set-Cookie names fingerprint the framework.
- [ ] ETag and cache headers reveal the serving stack and caching layer.
- [ ] Via/X-Forwarded-* trace the proxy chain — each hop is a surface.
- [ ] Cookie names: laravel_session (PHP), connect.sid (Express), JSESSIONID (Java), session (Django/Flask).

## Abort conditions

- Cookie names are the most reliable framework fingerprint — can't be stripped as easily.
- X-Cache/Via chains map to request-smuggling's proxy topology.
- Duplicate/conflicting headers are themselves a finding.

## Falsifier

Falsifier — stripped headers and generic cookies: framework must come from body/error analysis.
