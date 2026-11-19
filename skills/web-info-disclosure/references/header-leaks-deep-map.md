# Deep header analysis — beyond Server/X-Powered-By — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| ETag 'W/"len-mtime"' | Node/Express etag style | framework hint |
| X-Cache: HIT/MISS + Via | cache/proxy topology | smuggling leads |
| Set-Cookie name=laravel_session|connect.sid|JSESSIONID | framework fingerprint | framework-debug paths |
| X-Backend-* or X-Served-By | backend naming | vhost/topology |

## Falsifier

Falsifier — stripped headers and generic cookies: framework must come from body/error analysis.
