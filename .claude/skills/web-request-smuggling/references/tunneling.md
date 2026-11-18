# Tunneling — raw bytes through a non-HTTP channel

## The CONNECT method — the explicit tunnel

```text
CONNECT internal:80 HTTP/1.1
Host: t
```

`CONNECT` opens a raw TCP tunnel — the proxy forwards bytes verbatim —
HTTP requests inside the tunnel reach `internal:80` directly — no
front-end parsing, no filtering.

## The upgrade-tunnel — `Upgrade: websocket` or `h2c`

After the upgrade the proxy proxies raw frames — HTTP inside a frame
reaches the back-end's parser — `upgrade-smuggling.md`.

## The HTTP/1.0 keep-alive tunnel — `Connection: keep-alive` h1.0

```text
POST / HTTP/1.0
Connection: keep-alive
Content-Length: 4

GET /admin HTTP/1.0
```

An h1.0 keep-alive connection — the front-end may pipeline multiple
requests on one h1.0 socket — the smuggle inside the tunnel.

## The proxy-pipelining — `HTTP/1.1 pipelining`

```text
GET / HTTP/1.1
Host: t

GET /admin HTTP/1.1
Host: t
```

Two requests in one TCP write — h1.1 pipelining — a front-end that
doesn't support pipelining reads them as one malformed request →
desync.

## The TLS-in-TLS — `CONNECT` inside `CONNECT`

```text
CONNECT proxy:443 HTTP/1.1
CONNECT internal:443 HTTP/1.1
```

Nested CONNECT — a proxy chain — the tunnel through the tunnel reaches
the innermost internal host.

## The raw-socket framing — when HTTP stops

After `Upgrade` or `CONNECT` the bytes are no longer HTTP — the tunnel
carries ANY protocol — the back-end's protocol determines what's
smuggleable — HTTP inside a ws frame, Redis inside a TCP tunnel.

## The front-end's parser-exit — the bypass point

The tunnel removes the front-end's HTTP parser — Host rewriting, header
injection, WAF inspection all stop — the smuggle inside the tunnel
reaches the back-end raw — the tunnel is the escape hatch.

## The common tunnel-shapes — the checklist

| Shape | Tunnel |
|---|---|
| `CONNECT host:port` | raw TCP |
| `Upgrade: websocket` | ws frames |
| `Upgrade: h2c` | h2 cleartext |
| `Connection: keep-alive` h1.0 | pipelined h1.0 |
| pipelined requests | HTTP/1.1 pipeline |
| nested CONNECT | proxy chain |

## The smuggle-inside-tunnel — the raw bytes

```text
CONNECT internal:80 HTTP/1.1
Host: t

GET /admin HTTP/1.1
Host: internal
```

After the CONNECT's `200` — the `GET /admin` inside the tunnel reaches
`internal:80` directly — the front-end never parses it.

## The evidence — the tunnel's response

The tunneled `GET /admin` returns the internal route's content — the
response arrives on the same socket — verbatim excerpt.
