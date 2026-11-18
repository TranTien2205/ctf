# CTF shapes — how request-smuggling actually appears

## The classic — the reverse-proxy + backend pair

`nginx` or `haproxy` fronting `gunicorn`/`uwsgi`/`node` — the canonical
desync setup — the front-end's parser vs the back-end's parser disagree
on TE/CL — the handout's `docker-compose.yml` or `nginx.conf` shows the
pair — `whitebox-hunt.md`.

## The CRLF-into-URL — the SSRF-adjacent shape

```python
url = f"http://{host}/endpoint"
requests.get(url)
```

The `host` value is interpolated raw — `%0d%0a` folds headers into the
outbound request — the fold injects `Authorization`, `Host`, or a whole
second request — the `htb-weather-app` chain card — `crlf-injection.md`.

## The URL-param CRLF — `?host=a%0d%0aHost: internal`

```text
GET /fetch?host=example.com%0d%0aHost:%20internal HTTP/1.1
```

The `host` param lands raw inside the outbound `Host:` header — the
fold smuggles a second Host header — the back-end routes to `internal`.

## The websocket-tunnel — the upgrade escape

```text
GET /ws HTTP/1.1
Upgrade: websocket
```

The ws tunnel proxies raw frames — a smuggle inside a frame reaches the
back-end raw — `upgrade-smuggling.md`.

## The h2-downgrade — h2 front + h1 back

The front speaks h2, the back h1 — `content-length`/`transfer-encoding`
headers inside h2 get translated → desync — `http2-smuggling.md`.

## The admin-bot trigger — the client-side desync

A `POST` whose body the server ignores — the smuggle poisons the NEXT
visitor's request — the admin bot's request — `client-side-desync.md`.

## The internal-route readback — `GET /flag` smuggle

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /flag HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

`/flag` is loopback-only — the smuggle reaches it as the back-end —
the flag in the response — `internal-routes.md`.

## The queue-poison writeup-readback — `POST /store` smuggle

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

The victim's request lands inside `x=` → read `/store/last` → the
victim's cookie — `session-hijack.md`.

## The cache-poison — the desync → cached

The smuggle's response caches → every visitor gets the poison —
`cache-poison-via-smuggle.md`.

## The header-fold-into-SSRF — the `web-ssrf` sibling

`../web-ssrf/` — a URL param that lands in an outbound request — the
CRLF fold is the smuggle — the SSRF skill covers the URL-fetch, this
covers the fold — check both.

## The proxy-chain — `nginx → varnish → node`

Multiple proxies — each pair is a desync candidate — the handout's
proxy config names the chain — `whitebox-hunt.md`.

## The expected signals — what to look for in the handout

- `docker-compose` with `nginx`/`haproxy`/`traefik` + a backend
- a `requests.get(f"http://{x}")` interpolation — the CRLF-fold
- an `Upgrade:`/`websocket` route — the tunnel
- a `Host: ` interpolation — the host-fold
- a `Cache-Control`/`Vary` config — the cache-poison
