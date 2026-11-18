# Chunked encoding — the grammar the desync exploits

## The wire grammar — what `Transfer-Encoding: chunked` means

```text
<hex-size>\r\n
<data>\r\n
<hex-size>\r\n
<data>\r\n
0\r\n
\r\n
```

Each chunk: a hex length, CRLF, that many data bytes, CRLF. A `0\r\n\r\n`
terminates the body.

## The byte-count — every CRLF is 2 bytes

`5c\r\n` = 4 bytes on the wire — the `\r\n` is counted in the surrounding
framing, not in the data. A `Content-Length` mismatch with the chunk
layout is the desync.

## The chunk-size field — hex, optional extensions

```text
5c            — 92 bytes follow
5c;ext=x      — a chunk extension — ignored but parsed
0;x=y         — a terminating chunk with extensions
```

Chunk extensions (`;name=value`) are ignored — but a parser that doesn't
skip them reads `5c;ext=x` as a different size — an extension-desync.

## The chunk-size whitespace — `5c ` / ` 5c`

```text
5c \r\n        — trailing space
 5c\r\n        — leading space
5c\t\r\n       — tab
```

Some parsers trim, others reject — a whitespace-desync between front
and back.

## The negative/overflow sizes — `-1`, `ffffffff`

```text
-1\r\n          — a parser treating it as signed → -1 → error or huge
ffffffff\r\n    — 4GB — a parser truncates or wraps
8000000000000000\r\n  — 64-bit overflow
```

An overflow-size desync — one parser clamps, another wraps, a third
rejects.

## The chunk-size-on-next-line — `5c\n` LF-only

```text
5c\n<data>\n0\n\n
```

LF-only line endings — a strict parser rejects `\n` alone → falls back
to CL; a lenient parser accepts → chunks — desync on the line-ending.

## The early-terminator — `0` mid-body

```text
5c
<data>
0

GET /admin HTTP/1.1
```

The `0` terminates the body — the `GET /admin` is the next request —
the classic TE.CL desync body.

## The trailer headers — `0\r\nTrailer: x\r\n\r\n`

```text
5c
<data>
0
Trailer-Name: value

```

A chunked body may carry TRAILER headers after the `0` — one parser
reads them, another drops them — the trailer-desync.

## The missing-final-CRLF — the hang

```text
5c
<data>
0

```

vs

```text
5c
<data>
0

X
```

Without the final CRLF the body never terminates → the connection hangs
waiting for more → the "does it hang" detection.

## The pipelined-chunk — the second request inside a chunk

```text
5c
<data including GET /admin ...>
0

GET /admin HTTP/1.1
```

If the back-end sees `Content-Length` covering only `5c\r\n` — the rest
is the next request — TE.CL — `cl-te-desync.md`.

## The h1.0-fallback — `Transfer-Encoding` ignored

A back-end on h1.0 ignores `Transfer-Encoding` → falls back to CL →
desync on the protocol-version boundary.
