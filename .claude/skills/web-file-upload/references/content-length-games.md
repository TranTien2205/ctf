# Content-Length & Transfer-Encoding Games — the size-field lies

## The shape — the declared size doesn't match the real body

```
Content-Length: 100        while body is 10MB
Transfer-Encoding: chunked while Content-Length present
Content-Length: 0          with a real body
```

The validator may check `Content-Length` while the server reads the
actual body — or vice versa.

## Content-Length vs real body — the size-check bypass

- `Content-Length: 10` + 1MB body — a size validator reading the header
  accepts; the real body still lands
- the server's read path decides: php-fpm reads `CONTENT_LENGTH`; some
  frameworks read the stream
- test: `CL=1` + real file — accepted? the check reads the header; the
  store reads the body

## `Transfer-Encoding: chunked` — the bypass field

- TE chunked with `Content-Length` both present → HTTP/1.1 ambiguity —
  `web-request-smuggling`/`web-parser-differential` — the front-end may
  read CL, the back-end the chunks — a body-sized check sees the CL
  (small) while the chunked body lands (large)
- `TE: chunked` alone — the size check may not know to dechunk — a
  chunked-encoded file bypasses a size cap that reads CL only

## `Content-Encoding: gzip` — body-level compression

`Content-Encoding: gzip` + gzipped multipart body:

- the server decompresses → the size check saw the compressed size
- the multipart parser sees raw gzip bytes → parse confusion
- the filter checking magic bytes sees the gzip stream, not the file
- `Accept-Encoding`/`Content-Encoding` confusion between transport and
  content layers

## The `Expect: 100-continue` split — early validation

`Expect: 100-continue` — the server checks headers and replies `100`
before the body — a validator that runs at header-time sees only the
headers, not the body — the body lands after the check ran.

## `multipart` boundary + CL — the field-level lie

Inside a multipart body, each part has its own `Content-Length` (rare,
mostly ignored) and the outer request has `Content-Length` — which does
the validator trust?

## Detection — which size source does the check read?

```
1. CL: 10 + 1MB body → rejected by size? → the check reads real size
2. CL: 10 + 1MB body → accepted? → reads the header
3. chunked + CL → which was enforced?
```

## The `-1`/negative/overflow values

`Content-Length: -1`/`999999999999` — integer-overflow the size check —
a negative CL may pass a `< MAX` check while the real body is huge.

## Falsifiers

- the check reads the real body size uniformly
- TE chunked + CL = the server rejects (HTTP/1.1 spec-correct)

## Output to record

- which size source the check reads + whether the discrepancy is honored
