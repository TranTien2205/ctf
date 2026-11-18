# Parser quirks — the implementation-level differences

## The TE-value parser — `chunked` exact-match vs lenient

Strict parsers require exactly `chunked` — lenient parsers accept
`Chunked`, `chunked `, `xchunked`, `chunked;x` — `obfuscation.md`.

## The CL parser — numeric-strictness

Strict parsers require `[0-9]+` — lenient accept `+4`, ` 4`, `4 `,
`0x10`, `4a` — each is a desync candidate — `cl-manipulation.md`.

## The header-name parser — `Transfer_Encoding` / `TE:`

`Transfer_Encoding:` (underscore) and `TE:` are non-standard names —
some parsers match them — a name-synonym — `obfuscation.md`.

## The obs-fold — `value\r\n continuation`

```text
Header: value
 continuation
```

RFC 7230 deprecated obs-fold — strict parsers reject it, lenient join —
the continuation-desync.

## The chunk-extension — `5c;ext=x`

Chunk extensions are ignored — a parser that doesn't skip them reads
`5c;ext=x` as a different size — `chunked-encoding.md`.

## The chunk-size leading-zero — `005c`

```text
005c
<data>
```

Leading zeros — a parser that rejects vs one that accepts — a size-desync.

## The negative-chunk — `-1`

```text
-1
<data>
```

A parser treating size as signed → -1 → error; as unsigned → huge —
`chunked-encoding.md`.

## The `HTTP/1.1` version-strictness

```text
GET / HTTP/1.1
```

vs

```text
GET / HTTP/1.1 
```

Trailing space after the version — a strict parser rejects, a lenient
trims — `method-boundary.md`.

## The `Host:` requirement — h1.1 requires it

```text
GET / HTTP/1.1
```

No `Host:` — h1.1 REQUIRES `Host:` — a strict parser rejects, a lenient
accepts — the missing-Host desync.

## The `Content-Length` on GET — the method-body interaction

```text
GET / HTTP/1.1
Content-Length: 4

A=1&
```

A GET with a body — a parser that reads it vs one that ignores it —
the method-body desync — `method-boundary.md`.

## The pipelined-request — `GET /a\r\nGET /b`

```text
GET /a HTTP/1.1
GET /b HTTP/1.1
```

Two request-lines — the second is the next request or a malformed
header — `method-boundary.md`.

## The `Content-Length` overflow — `CL: 9999999999`

```text
Content-Length: 9999999999
```

A 64-bit CL — a parser that clamps vs one that waits — the overflow-desync.

## The tab-in-header — `Name:\tvalue`

```text
Content-Length:\t4
```

A tab after the colon — a parser that trims vs one that rejects —
`cl-manipulation.md`.

## The `Transfer-Encoding: chunked,identity` — the multi-value

```text
Transfer-Encoding: chunked, identity
```

`chunked` + `identity` — a parser honoring `identity` falls back to CL —
`obfuscation.md`.
