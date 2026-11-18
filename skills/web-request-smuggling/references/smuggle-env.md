# Smuggle environment — where the desync lives

## The production front — the proxy at the edge

```text
client → [CDN/WAF] → [load-balancer] → [reverse-proxy] → [app]
```

Each layer is a parser — each pair is a desync candidate — `proxy-behavior.md`.

## The dev front — `webpack-dev-server` / `vite` / `flask --debug`

```text
client → [dev-proxy] → [app]
```

The dev-proxy's lenient parser — `Upgrade: websocket` tunnel —
`upgrade-smuggling.md`.

## The serverless front — `API Gateway` / `CloudFront`

```text
client → API-Gateway → lambda
```

The API-Gateway's h2→h1 downgrade — `http2-smuggling.md`.

## The microservice mesh — `istio` / `envoy` / `linkerd`

```text
client → ingress → sidecar-envoy → app
```

The service-mesh's sidecar — a strict-RFC envoy — the desync-resistant —
`denied-conditions.md`.

## The legacy front — `apache` / `iis` / `squid`

```text
client → [legacy-proxy] → [app]
```

The legacy parser's leniencies — obs-fold, case-fumble, dup-CL —
`proxy-behavior.md`.

## The container front — `docker-compose` / `k8s-ingress`

```yaml
nginx:
  ports: ["80:80"]
app:
  expose: ["8000"]
```

`container-world.md` — the compose pair.

## The lab front — `socat` / `nc` / a hand-rolled proxy

```text
socat TCP-LISTEN:80,fork TCP:app:8000
```

A hand-rolled proxy — the rawest front — the smuggle's easiest target —
`whitebox-hunt.md`.

## The TLS-terminator — the front that decrypts

```text
client → [TLS-terminator] → [plain-HTTP back-end]
```

The TLS-terminator — the SNI/ALPN layer — `advanced-reach.md`.

## The multi-proxy — `nginx → haproxy → node`

```text
client → nginx → haproxy → node
```

The chain — each pair is a desync — `whitebox-hunt.md`.

## The same-process — the app's own HTTP-server

```python
app.run()   # no proxy — the app IS the front
```

No front-end — no desync — a direct-connection — `denied-conditions.md`.
