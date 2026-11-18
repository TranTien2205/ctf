# Header boundary — where the headers end

## The end-of-headers — `\r\n\r\n`

```text
Header: value\r\n
\r\n
<body>
```

The `\r\n\r\n` terminates the headers — everything after is the body —
the parser's first boundary.

## The LF-only — `\n\n`

```text
Header: value\n
\n
<body>
```

A parser that accepts `\n` alone → the boundary is `\n\n` — a strict
parser rejects → waits for `\r\n` — a line-ending desync —
`parser-quirks.md`.

## The obs-fold — `value\r\n continuation`

```text
Header: value\r\n
 continuation\r\n
\r\n
```

The ` continuation` is a folded-continuation of the same header — a
parser that joins vs one that rejects — `parser-quirks.md`.

## The header-size-limit — `8192` bytes

```nginx
large_client_header_buffers 4 8k;
```

A header-block over 8k — a parser that truncates vs one that rejects —
the size-limit desync.

## The header-count-limit — `100` headers

A parser that rejects >100 headers — a header-count desync.

## The `Content-Length`/`Transfer-Encoding` inside headers — the boundary-headers

```text
Content-Length: 4\r\n
Transfer-Encoding: chunked\r\n
\r\n
<body>
```

Both headers inside the headers-section — the precedence-rule —
`cl-manipulation.md`.

## The duplicate-header — `Header: a\r\nHeader: b`

```text
Header: a\r\n
Header: b\r\n
```

Two same-name headers — first-wins, last-wins, join — `header-smuggling.md`.

## The missing-header — `Host:` required on h1.1

```text
GET / HTTP/1.1\r\n
\r\n
```

h1.1 requires `Host:` — a strict parser rejects, a lenient accepts —
`parser-quirks.md`.

## The header-name-case — `Content-Length` vs `content-length`

```text
content-length: 4
```

Case-insensitive per RFC — a strict-case parser — `parser-quirks.md`.

## The header-value-fold — the `value\r\nNext: x`

```text
Header: value\r\nNext: x\r\n
```

The fold inside a value — `header-smuggling.md`.
