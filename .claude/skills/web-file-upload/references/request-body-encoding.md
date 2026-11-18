# Request-Body Encoding — Content-Encoding / charset games

## The shape — the body arrives encoded, the parser sees raw

`Content-Encoding: gzip`/`deflate`/`br`/`zstd` — the HTTP-level body
compression — sits between transport and the multipart parser:

- the multipart parser may read the gzipped bytes verbatim → parse fails
- the server may decompress first → the check sees real body
- the filter reads `Content-Length` (the compressed size) but the
  decompressed size is the real one

## `Content-Encoding` variants — which the server honors

```
Content-Encoding: gzip
Content-Encoding: deflate
Content-Encoding: br          (brotli — many parsers don't)
Content-Encoding: zstd
Content-Encoding: identity    (no-op — the null transform)
Content-Encoding: gzip,br     (stacked)
```

A validator checking magic bytes sees the gzip stream — your `.png`
inside the gzip isn't detected as png — the check's "does it start with
PNG magic" reads the compressed form.

## The charset trick — `Content-Type: ...; charset=utf-16`

- `charset=utf-16` — the body is utf-16 — a filter checking for `<?php`
  bytes in utf-8 sees the null-interleaved utf-16 — `\x3c\x00?\x00p\x00`
  not `<?php`
- `charset=ibm037`/EBCDIC — a non-ASCII-compatible charset — the check's
  byte patterns miss
- the parser that decodes the charset sees the real text — a check
  running pre-decode vs post-decode disagreement

## `Transfer-Encoding` vs `Content-Encoding` — the layering

```
request → chunked TE → gzip CE → multipart → file
```

Each layer transforms the bytes the next sees — a filter at layer N
misses what the parser at layer N+1 sees. `web-request-smuggling`/
`web-parser-differential` cover the TE games; this is the CE layer.

## The "the filter reads a compressed body" — classic filter-bypass

A form whose `Content-Type: multipart/form-data` + `Content-Encoding:
gzip` — the server's multipart parser may:
- decompress first (correct) → normal processing
- read raw gzip bytes as the body → boundary never found → reject or
  different parse

Different stacks handle it differently — `web-parser-differential`.

## The "charset=binary" trick — declare a binary charset

`charset=binary`/`charset=x-user-defined` — parsers that skip decoding
leave the bytes raw — the check sees the body's literal form.

## `Content-Encoding` + multipart — which boundary wins?

The boundary inside a gzipped multipart body — if the parser decompresses
before parsing, the boundary is found inside the decompressed text; if
not, no boundary found.

## The size-differential — compressed Content-Length vs real

- `Content-Encoding: gzip` + a 1KB gzipped body containing a 10MB file —
  the size check reads `Content-Length` (~1KB) — the decompressed 10MB
  lands — size check bypassed.

## Detection — which encodings the stack honors

```
1. POST with Content-Encoding: gzip + gzipped multipart → file lands?
2. charset=utf-16 body → how does it parse?
3. Content-Encoding: br → does the server try to decompress?
```

## Falsifiers

- the server rejects non-identity Content-Encoding uniformly
- the charset is ignored AND the bytes checked at every layer

## Output to record

- which Content-Encoding/charset values the stack decodes + at what
  stage the filter reads
