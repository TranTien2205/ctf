# White-box hunt — finding the desync in source

## The proxy-config — the front+back pair

`docker-compose.yml` / `nginx.conf` / `haproxy.cfg` — the front-end
named — the backend named — the pair's known desyncs:

- `nginx` → `gunicorn`/`uwsgi` — CL.TE or TE.CL
- `nginx` → `node`/`express` — TE.TE or h2-downgrade
- `haproxy` → `apache`/`iis` — CL.CL or TE.CL
- `traefik`/`envoy` → `flask`/`django` — header-inheritance or h2
- `cloudflare`/`cloudfront` → origin — edge-case desyncs

## The CRLF-fold — the URL-interpolation sink

```python
requests.get(f"http://{host}/endpoint")
```

The `host` value interpolated raw — `%0d%0a` folds headers — grep for
`requests.get(`, `urllib.request.urlopen(`, `http.client.HTTPConnection(` —
any interpolation with a user-controlled part.

## The body-ignored route — the CL.0 candidate

```python
@app.route('/redirect')
def redirect():
    return redirect('/')     # never reads the body
```

A route that responds without reading the body — `GET`/`HEAD`/`OPTIONS`/
redirect handlers — the CL.0 candidates — `client-side-desync.md`.

## The internal-route — the loopback-only listener

```python
@app.route('/internal')
def internal():
    if request.remote_addr != '127.0.0.1':
        return 403
```

A route gated on `127.0.0.1` — reachable only via the smuggle —
`internal-routes.md`.

## The XFF-trust — `request.headers['X-Forwarded-For']`

```python
if request.headers['X-Forwarded-For'] != '127.0.0.1':
```

The app trusts `X-Forwarded-For` — the smuggle's own `XFF` — or the
front's injected `XFF` — the internal-route's gate.

## The cache-config — `Cache-Control`/`Vary`

```nginx
proxy_cache_key $uri;
add_header Vary Cookie;
```

The cache's key — a mis-keyed entry poisons — `cache-poison-via-smuggle.md`.

## The upgrade-route — `Upgrade: websocket`

```python
@app.websocket('/ws')
async def ws(websocket):
```

A ws route — the tunnel — `upgrade-smuggling.md`.

## The h2-config — `listen 443 http2`

```nginx
listen 443 ssl http2;
```

The front speaks h2 — the back may speak h1 — `http2-smuggling.md`.

## The log/store endpoint — the readback

```python
@app.route('/store', methods=['POST'])
def store():
    db.save(request.form['x'])
```

An endpoint that stores a param — the readback for the cookie-steal —
`session-hijack.md`.

## The grep patterns — the sinks

```bash
grep -rn "requests.get(" src/           # the URL-interpolation
grep -rn "urllib" src/                   # urllib sinks
grep -rn "X-Forwarded-For\|X-Real-IP" src/  # trusted-header
grep -rn "remote_addr\|127.0.0.1" src/   # loopback-gate
grep -rn "websocket\|Upgrade" src/        # the tunnel
grep -rn "Transfer-Encoding\|Content-Length" src/  # the desync
grep -rn "proxy_cache\|Cache-Control" src/        # the cache
```
