# Advanced headers — the routing and trust headers

## `X-Forwarded-*` family — the trust headers

```text
X-Forwarded-For: 127.0.0.1
X-Forwarded-Host: internal
X-Forwarded-Proto: https
X-Forwarded-Port: 443
X-Forwarded-Server: internal
X-Forwarded-Uri: /admin
```

Each `X-Forwarded-*` may override the request's real value — a front-
end that forwards them lets the smuggle spoof source/host/scheme/path —
`internal-routes.md`.

## `X-Real-IP` — the source-IP override

```text
X-Real-IP: 127.0.0.1
```

The real-IP header — the back-end reads it as the client IP — the
loopback-gate bypass.

## `X-Original-URL` / `X-Rewrite-URL` — the IIS path-override

```text
X-Original-URL: /admin
```

IIS/ARR honors `X-Original-URL` as the request path — the smuggle's
`X-Original-URL` routes to `/admin` — `header-smuggling.md`.

## `X-HTTP-Method-Override` — the method-override

```text
POST / HTTP/1.1
X-HTTP-Method-Override: PUT
```

The method-override — `method-boundary.md`.

## `X-Original-Method` — the method-synonym

```text
POST / HTTP/1.1
X-Original-Method: DELETE
```

A framework that honors `X-Original-Method` — the method-smuggle.

## `Via:` — the proxy-chain info

```text
Via: 1.1 internal-proxy
```

The `Via` chain — a proxy appends it — the chain-info leaks the topology.

## `Forwarded:` — the RFC 7239 structured header

```text
Forwarded: for=127.0.0.1;host=internal;proto=https
```

The structured `Forwarded:` — the RFC form of `X-Forwarded-*` — a
parser that honors it vs one that only reads `X-Forwarded-*`.

## `Referer:` — the routing-Referer

```text
Referer: http://t/admin
```

An app that routes on Referer — the internal path — `header-smuggling.md`.

## `Cookie:` — the session carrier

```text
Cookie: session=abc
```

The victim's `Cookie:` inside the smuggle — `session-hijack.md`.

## `Authorization:` — the forged auth

```text
Authorization: Basic YWRtaW46YWRtaW4=
```

The fold injects `Authorization` — the outbound request carries it —
`crlf-injection.md`.

## `Trailer:` — the post-body headers

```text
Trailer: X-Smuggle
```

Declares headers that come after the chunked body — `extended-corpus.md`.

## `Expect: 100-continue` — the interim response

```text
Expect: 100-continue
```

The `100 Continue` interim — the front sends it → the client sends the
body — a middleware that auto-sends it early shifts the boundary —
`extended-corpus.md`.

## `TE:` — the client-TE (different from Transfer-Encoding)

```text
TE: trailers, deflate
```

The `TE:` request-header declares acceptable transfer-encodings —
DIFFERENT from `Transfer-Encoding:` — a parser that confuses them —
a name-synonym desync.

## `Upgrade:` — the protocol-upgrade

```text
Upgrade: websocket
Upgrade: h2c
Upgrade: TLS/1.2
```

`upgrade-smuggling.md` — the tunnel.
