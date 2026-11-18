# Smuggle traps — the byte-level failure modes

## The off-by-one — `Content-Length` miscount

```text
Content-Length: 3    — drops the \n — smuggle truncated
Content-Length: 4    — correct — reads 5c\r\n
Content-Length: 5    — eats a byte of the next request
```

The `#1` failure — `cl-te-desync.md` — count the bytes, don't estimate.

## The chunk-size in decimal — `60` vs `3c`

```text
60\r\n<data>\r\n     — WRONG — reads 60 bytes
3c\r\n<data>\r\n     — correct — reads 60 bytes (0x3c)
```

Chunk sizes are HEX — `chunked-encoding.md`.

## The missing final-CRLF — the body never ends

```text
0\r\n
\r\n
```

The `\r\n` after the `0` is required — without it → hang —
`cl-te-desync.md`.

## The missing trailing fragment — the unbounded smuggle

```text
POST / [desync] [smuggle] [no trailing fragment]
```

The smuggle's own framing is unbounded — the connection hangs — append
`GET / HTTP/1.1` — `cl-te-desync.md`.

## The wrong `Host:` — the vhost 404

```text
GET /admin HTTP/1.1
Host: wrong
```

The smuggle's `Host:` must match the back-end's vhost — `internal-routes.md`.

## The non-shared connection — `Connection: close`

The desync needs a reused socket — `Connection: close` → no "next
request" — `denied-conditions.md`.

## The front re-parses — the tunnel doesn't escape

`Upgrade: websocket` — some proxies re-parse the tunnel → the smuggle
inside a frame is still parsed — `denied-conditions.md`.

## The pipelined-batch — the smuggle's position shifts

```text
GET /a + [smuggle] + GET /b
```

The smuggle inside a batch — the batch's boundary shifts —
`http-pipelining.md`.

## The TLS-resumption — the socket's TLS-state

A resumed TLS socket — the session-state persists — `smuggle-stability.md`.

## The TCP-buffer — the smuggle's bytes in flight

The smuggle's bytes sit in the TCP receive-buffer — `smuggle-stability.md`.

## The pool-slot — the non-deterministic poison

The victim's request has to hit the same pool slot — `queue-management.md`.

## The cachebuster missing — the production poison

A smuggle that caches poisons every visitor — use `?cb=xyz` —
`cache-poison-via-smuggle.md`.
