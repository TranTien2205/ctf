# Smuggle readback — getting the smuggle's output

## The problem — the smuggle's response goes to the wrong socket

A desync smuggle's response goes to the NEXT request on the queue —
you need a readback channel — the smuggle's output has to reach you.

## The self-poison — your own next request

```text
POST / [desync: GET /marker]  →  then  GET /  →  the GET returns /marker
```

Your next request's response IS the smuggle's output — the self-poison
— `response-poisoning.md`.

## The stored-param — the smuggle writes to a store

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

The victim's request lands inside `x=` — `/store` stores it — read
`/store/last` — the smuggle's body is the victim's request —
`session-hijack.md`.

## The echoed-param — the smuggle's query echoes

```text
GET /search?q=MARKER HTTP/1.1
```

smuggled → `/search` echoes `q` — the next response carries `MARKER` —
the echo-readback.

## The Location-header readback — the redirect

```text
GET /redirect?to=/marker HTTP/1.1
```

smuggled → `/redirect` `Location: /marker` — the next response's
Location carries the marker — the redirect-readback.

## The status-readback — the smuggle's status lands

```text
GET /admin HTTP/1.1
```

smuggled → `/admin` returns 200/403 — the next response's STATUS is the
smuggle's — the status-readback.

## The internal-route content — the `/flag` readback

```text
GET /flag HTTP/1.1
```

smuggled → `/flag` returns the flag — the next response's BODY is the
flag — the content-readback — verbatim excerpt — `evidence-rules.md`.

## The delayed-readback — the async job's output

```text
store the smuggle → trigger the job → read the job's log
```

`webhook-deferred.md` — the deferred readback.

## The error-readback — the smuggle's error leaks

```text
GET /invalid HTTP/1.1
```

smuggled → the 404/500 error-body names the route — the error-readback.

## The header-readback — the smuggle's headers reflect

```text
GET / HTTP/1.1
X-Debug: marker
```

smuggled → the next response's debug-output names `X-Debug: marker` —
the header-readback.

## The timing-readback — the smuggle's delay

```text
GET /slow HTTP/1.1
```

smuggled → the next response's timing is slow — the timing-readback —
weakest, `inconclusive` alone.

## The response-pair — the socket-accounting

Send the desync + a normal request on the same socket — count the
responses — the back-end answered a request the front never sent —
`detection-oracle.md`.
