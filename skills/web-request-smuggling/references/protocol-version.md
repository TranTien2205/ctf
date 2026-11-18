# Protocol version — the h1.0 / h1.1 / h2 / h3 boundaries

## The version-declaration — `HTTP/1.0` vs `HTTP/1.1` vs `HTTP/2`

```text
POST / HTTP/1.0
```

vs

```text
POST / HTTP/1.1
```

The version determines the parser's rules — h1.0 has no
`Transfer-Encoding`, no keep-alive by default — h1.1 has both — h2 is
binary.

## The h1.0 boundary — the connection-close

h1.0's body boundary is the connection-close — no `Content-Length` means
"body runs to close" — a front-end that upgrades h1.0 to h1.1 re-frames
the body — the boundary shifts — `tunneling.md`.

## The h1.0 keep-alive — `Connection: keep-alive`

h1.0 + explicit `keep-alive` → the socket pipelines → a front-end that
doesn't expect h1.0 pipelining → desync.

## The h1.1 keep-alive — the default

h1.1's default is keep-alive — the shared socket — the desync's
prerequisite.

## The h2 frame-boundary — the binary parser

h2 requests are length-prefixed frames — the front-end knows exactly
where request N ends — the desync is at the h2→h1 downgrade —
`http2-smuggling.md`.

## The h2 pseudo-headers — `:method`, `:path`, `:authority`, `:scheme`

```text
:method GET
:path /admin
:authority t
:scheme https
```

Pseudo-headers map to the h1 request-line — the `:` values carry the
smuggle — `http2-smuggling.md`.

## The h3 QUIC — the UDP layer

HTTP/3 over QUIC — the frame-boundary is at the QUIC layer — a
downgrade-chain h3→h2→h1 multiplies the desync surface.

## The version-mismatch — `HTTP/1.0` request to an h1.1 back-end

```text
POST / HTTP/1.0
Content-Length: 4

GET /admin HTTP/1.1
```

The h1.0 request's body-boundary is the connection-close — the
`GET /admin` is INSIDE the body — a front-end that re-frames to h1.1
splits it — desync.

## The `Connection:` header — `keep-alive` / `close` / `upgrade`

```text
Connection: keep-alive    — the shared socket
Connection: close         — no desync possible
Connection: Upgrade       — the tunnel
Connection: Upgrade, HTTP2-Settings   — the h2c upgrade
```

The `Connection:` header's values control the pipelining and the
upgrade — the desync's prerequisite.

## The version-downgrade attack — `HTTP/1.1` → `HTTP/1.0`

```text
POST / HTTP/1.1
Connection: close
```

Forcing h1.0 semantics on an h1.1 connection — the boundary rules
change — a version-desync.

## The version-in-smuggle — `GET / HTTP/1.0` inside an h1.1 request

```text
POST / HTTP/1.1
Content-Length: 45

GET /admin HTTP/1.0
```

The smuggle's version differs from the outer — a parser that version-
checks vs one that doesn't.
