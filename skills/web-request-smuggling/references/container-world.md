# Container world — the smuggle inside a containerized app

## The docker-compose pair — `nginx` + `app`

```yaml
services:
  nginx:
    image: nginx
    ports: ["80:80"]
  app:
    image: myapp
```

The `docker-compose.yml` — the front+back pair — the desync's home —
`whitebox-hunt.md`.

## The internal-network — `app:8000` inside the compose

```yaml
app:
  expose: ["8000"]
```

The app's port is internal-only — the smuggle reaches it — `internal-routes.md`.

## The service-name DNS — `http://app:8000`

```text
GET http://app:8000/flag HTTP/1.1
```

The compose's service-name resolves inside the network — the smuggle's
`Host: app` or absolute-URI `http://app:8000` — `internal-routes.md`.

## The loopback listener — `127.0.0.1:9000` inside the container

```python
app.run(host='127.0.0.1', port=9000)
```

A listener on the container's loopback — the smuggle's `Host: t:9000`
reaches it — `internal-routes.md`.

## The sidecar — the adjacent container

```yaml
app:
sidecar:
  image: redis
```

A sidecar service — `redis://sidecar:6379` — the smuggle's URL-fetch —
`../web-ssrf/`.

## The healthcheck — the `HEALTHCHECK` route

```dockerfile
HEALTHCHECK CMD curl -f http://localhost:8000/health
```

The `/health` route — the internal health-check — the smuggle reaches it.

## The env-var flag — `FLAG=flag{...}`

```dockerfile
ENV FLAG=flag{...}
```

The flag in the env — `/proc/self/environ` or a debug route — `../file-read-primitives/`.

## The proxy-config — `nginx.conf` inside the container

```nginx
location /internal {
    allow 127.0.0.1;
    deny all;
}
```

The internal-location — the loopback-gate — the smuggle bypasses it —
`internal-routes.md`.

## The host-network — `network_mode: host`

```yaml
app:
  network_mode: host
```

The app shares the host's network — `127.0.0.1:port` is the HOST's —
the smuggle reaches host-internal services.

## The multi-stage — the build-args flag

```dockerfile
ARG FLAG=flag{...}
RUN echo $FLAG > /flag.txt
```

The flag baked into the image — the smuggle's `GET /flag` or a file-read
— `flag-locations.md`.
