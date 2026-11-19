# Deep header analysis — beyond Server/X-Powered-By — case catalogue

The secondary headers: ETag shapes, X-Cache, Via, timing headers, framework session-cookie names — each a fingerprint.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | ETag 'W/"len-mtime"' | Node/Express etag style | framework hint |
| 2 | X-Cache: HIT/MISS + Via | cache/proxy topology | smuggling leads |
| 3 | Set-Cookie name=laravel_session|connect.sid|JSESSIONID | framework fingerprint | framework-debug paths |
| 4 | X-Backend-* or X-Served-By | backend naming | vhost/topology |

## Falsifier

Falsifier — stripped headers and generic cookies: framework must come from body/error analysis.
