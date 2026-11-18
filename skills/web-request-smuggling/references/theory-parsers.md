# Theory — the parsers that disagree

## The front-end parser — the translating parser

```text
client → front-parser → re-emit → back-parser
```

The front-end parses the client's bytes — re-emits them to the back-end —
the re-emit is where the disagreement lands — `theory.md`.

## The back-end parser — the consuming parser

The back-end parses the re-emitted bytes — the boundary it computes is
the desync's boundary — `theory.md`.

## The parser-behaviors — the taxonomy

| Behavior | Meaning |
|---|---|
| strict-RFC | reject CL+TE |
| TE-wins | honor TE over CL |
| CL-wins | honor CL over TE |
| first-header | honor the first dup |
| last-header | honor the last dup |
| lenient-TE | `Transfer_Encoding`, `cow` |
| obs-fold | join `\r\n ` |
| chunk-ext | `5c;ext=x` |

`parser-quirks.md`.

## The pair-table — which pair disagrees

`desync-taxonomy.md` — the CL.TE / TE.CL / TE.TE / CL.CL / CL.0 / H2.*.

## The disagreement-sources — the ambiguity

```text
Content-Length: 4
Content-Length: 7     — which CL?
```

```text
Transfer-Encoding: chunked
Transfer-Encoding: cow    — which TE?
```

```text
Content-Length: 4
Transfer-Encoding: chunked    — which wins?
```

`ambiguity-catalog.md`.

## The protocol-version — h1.0 / h1.1 / h2

```text
HTTP/1.0 — no TE, no keep-alive
HTTP/1.1 — TE, keep-alive
HTTP/2   — binary frames
```

`protocol-version.md`.

## The downgrade — h2 → h1

```text
h2 frames → translate → h1 text
```

`theory-downgrade.md`.

## The upgrade — `Upgrade:`/`CONNECT`

```text
Upgrade: websocket → raw frames
CONNECT host:port → raw TCP
```

`tunneling.md`.

## The body's parsers — `Content-Type`

```text
application/json → JSON-parser
application/x-www-form-urlencoded → form-parser
multipart/form-data → multipart-parser
```

`content-type-boundary.md`.
