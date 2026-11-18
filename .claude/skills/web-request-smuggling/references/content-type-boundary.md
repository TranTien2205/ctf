# Content-Type boundary — the body-parser desync

## The shape — the Content-Type determines the body-parser

```text
Content-Type: application/x-www-form-urlencoded
Content-Type: application/json
Content-Type: multipart/form-data; boundary=X
```

The Content-Type selects the body-parser — a parser disagreement on
the Content-Type shifts the body boundary.

## The multipart boundary — `boundary=X` disagreement

```text
Content-Type: multipart/form-data; boundary=----x

------x
Content-Disposition: form-data; name="a"

1
------x--
```

The `boundary=` parameter — a parser that reads it vs one that doesn't —
the body ends at `------x--` for one, at CL for the other — a
boundary-desync.

## The multipart smuggle — `boundary=` inside the body

```text
Content-Type: multipart/form-data; boundary=X
Content-Length: 4

------X
... the smuggle inside the multipart body
```

The multipart-boundary contains the smuggle — the back-end parses the
multipart differently — the smuggle lands inside a part.

## The `application/x-www-form-urlencoded` vs `application/json`

```text
Content-Type: application/json
Content-Length: 4

{"a":1}
```

vs the same body as `form-urlencoded` — different parsers → different
body interpretation → a parser-mismatch.

## The `charset` boundary — `charset=utf-16`

```text
Content-Type: text/plain; charset=utf-16
Content-Length: 4
```

A UTF-16 body — the byte-count vs the char-count differ — a front-end
counting chars vs the back counting bytes — a charset-desync.

## The `Content-Encoding` — gzip + chunked

```text
Content-Type: application/json
Content-Encoding: gzip
Transfer-Encoding: chunked
```

A gzip-body inside chunks — the front de-chunks then re-compresses —
the compression-boundary — `extended-corpus.md`.

## The `Content-Type` missing — the default parser

```text
POST / HTTP/1.1
Content-Length: 4

A=1&
```

No Content-Type — the back-end's default parser — a parser-mismatch
desync.

## The `Content-Type` case — `Application/JSON`

```text
Content-Type: Application/JSON
```

Case-insensitive per RFC — some parsers exact-match — a case-desync.

## The body-vs-CL — the parser's boundary

The body-parser reads the body differently than the CL declares — a
`multipart` body that ends before CL — a `json` body that validates —
each is a parser-boundary desync.
