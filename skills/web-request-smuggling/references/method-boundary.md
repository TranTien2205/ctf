# Method-boundary — the request-line desync

## The request-line as the boundary — `METHOD path HTTP/1.1`

The request-line is the first line — the parser's boundary-detection
starts there — a smuggle's request-line inside a body lands as the next
request-line.

## The method-case — `GET` vs `get` vs `Get`

```text
get /admin HTTP/1.1
```

Method is case-SENSITIVE per RFC — some parsers normalize — a lowercase
`get` rejected by the front, honored by the back — a method-case desync.

## The method-length — `GPOST`, `OPTIONSX`

```text
GPOST / HTTP/1.1
```

The CL.TE leftover `G` prefixes the next request — `GPOST` is malformed —
the parser's method-validation — `cl-te-desync.md`.

## The method-override — `X-HTTP-Method-Override`

```text
POST / HTTP/1.1
X-HTTP-Method-Override: PUT
```

The override header — a front-end that forwards it → the back-end treats
POST as PUT — `header-smuggling.md`.

## The method-body interaction — which methods carry bodies

- `GET`/`HEAD`/`OPTIONS`/`DELETE`/`TRACE` — usually bodiless → body
  ignored → CL.0 — `client-side-desync.md`
- `POST`/`PUT`/`PATCH` — body-carrying → the desync body

## The CONNECT method — the tunnel

```text
CONNECT internal:80 HTTP/1.1
```

`tunneling.md` — the raw-TCP tunnel.

## The OPTIONS `*` — the asterisk-form

```text
OPTIONS * HTTP/1.1
```

The `*` target — a parser that handles it vs one that rejects — a
boundary-desync.

## The absolute-URI — `GET http://internal/path`

```text
GET http://internal/path HTTP/1.1
```

The absolute-URI — a proxy routes on the URI host — `header-smuggling.md`.

## The authority-form — `CONNECT host:port` request-line

```text
CONNECT internal:80 HTTP/1.1
```

The authority-form — the CONNECT's request-line — a proxy that requires
it vs one that accepts the origin-form.

## The trailing-whitespace — `GET / HTTP/1.1 `

```text
GET / HTTP/1.1 
```

A trailing space after the version — a strict parser rejects, a lenient
parser trims — a boundary-desync.

## The double-request-line — `GET /a HTTP/1.1\r\nGET /b`

```text
GET /a HTTP/1.1
GET /b HTTP/1.1
```

Two request-lines — a parser that reads the first, the second is the
next request — or the second line is a malformed header — a request-line
desync.
