# Theory primitives — the parsing model

## The byte-stream — the request is bytes, not a structure

```text
POST /a HTTP/1.1\r\nHost: t\r\nContent-Length: 4\r\n\r\nA=1&
```

One contiguous byte-stream — the parser finds `\r\n\r\n` (end of headers)
then reads `Content-Length` bytes (the body) — what's left is the NEXT
request — the boundary is COMPUTED, not marked.

## The two parsers — the front and the back

```text
client → front-parser → re-emit → back-parser → handler
```

The front parses your bytes, re-emits a request to the back — the back
parses the re-emitted bytes — the disagreement between the two parses
is the desync — `theory.md`.

## The boundary-signals — `Content-Length` / `Transfer-Encoding` / `close`

```text
Content-Length: N       — body = N bytes
Transfer-Encoding: chunked — body = 0-terminated chunks
(neither)               — body = connection-close
```

Three ways to find the body's end — a parser honoring a different one
than its peer → desync.

## The precedence-rule — RFC 7230 §3.3.3

If both CL and TE are present, TE wins — but "TE" means the parser
RECOGNIZED `chunked` — a malformed TE that isn't recognized falls back
to CL — the obfuscation-desync — `obfuscation.md`.

## The request-line — `METHOD path HTTP/1.1`

```text
GET /admin HTTP/1.1\r\n
```

The parser's first task — a smuggle's request-line inside a body lands
as the NEXT request-line — `method-boundary.md`.

## The headers — `Name: value\r\n` until `\r\n\r\n`

The headers end at `\r\n\r\n` — a `\r\n` inside a value (obs-fold or a
CRLF-injection) shifts the boundary — `header-smuggling.md`.

## The chunk-grammar — `<hex>\r\n<data>\r\n0\r\n\r\n`

```text
5c\r\n<92 bytes>\r\n0\r\n\r\n
```

Hex sizes, CRLF-delimited, `0` terminates — `chunked-encoding.md`.

## The upgrade — `Upgrade:`/`Connection: Upgrade`

After an upgrade the front proxies raw bytes — the HTTP parser is
bypassed — `upgrade-smuggling.md`.

## The h2 frame — binary length-prefixed

h2 requests are length-prefixed frames — the front knows the exact
boundary — the desync is at the h2→h1 re-emit — `http2-smuggling.md`.

## The trust-boundary — the front filters, the back trusts

The front checks auth/paths/headers — the back trusts the front's
output — the smuggle bypasses the front's checks — `frontend-bypass.md`.

## The keep-alive queue — the shared socket

`Connection: keep-alive` — one socket, many requests — the desync's
"next request" exists only on a shared socket — `queue-management.md`.
