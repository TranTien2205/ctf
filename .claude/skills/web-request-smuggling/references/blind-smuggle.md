# Blind smuggle — when the response isn't yours

## The shape — the smuggle's output goes to a different socket

A desync smuggle's response goes to the NEXT request's socket — you
don't see it — the smuggle is "blind" — the readback has to come
through a side-channel.

## The stored readback — `POST /store` + read `/store/last`

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

The victim's request inside `x=` → `/store` stores → `GET /store/last`
reads it — `session-hijack.md`.

## The echoed readback — `GET /search?q=X`

```text
GET /search?q=MARKER HTTP/1.1
```

smuggled → the next response echoes `MARKER` — the echo-readback —
`smuggle-readback.md`.

## The self-poison readback — `POST [desync] + GET /`

```text
POST / [desync: GET /marker] → GET / → the GET returns /marker
```

Your next request IS the readback — `response-poisoning.md`.

## The timing readback — the smuggle's delay

```text
GET /slow HTTP/1.1
```

smuggled → the next response is slow — the timing-readback — weakest,
`inconclusive` alone — `evidence-rules.md`.

## The error readback — the smuggle's error-body

```text
GET /invalid-path HTTP/1.1
```

smuggled → the 404-body names the path — the error-readback.

## The OOB readback — the smuggle triggers an out-of-band fetch

```text
GET /?url=http://oob.t/x HTTP/1.1
```

smuggled → the back-end fetches `oob.t` — the OOB-listener captures it —
the OOB-readback — `skills/web-ssrf/references/blind-ssrf.md`.

## The `oob_listener` — the repo's OOB tool

```bash
python3 tools/web/oob_listener.py serve --port 8000
python3 tools/web/oob_listener.py hits
```

`tools/web/oob_listener.py` — the OOB-listener — the smuggle's URL-fetch
lands on it — the hit-list confirms.

## The deferred readback — the async job

```text
store the smuggle → the job runs it → the job's log shows it
```

`webhook-deferred.md`.

## The no-readback case — the pure-DoS

A smuggle that only corrupts the queue — no readback — `denies` the
smuggle's usefulness — the queue-poison is detectable but not
exploitable.

## The evidence — the verbatim excerpt

The readback's output — the stored-param's content, the echo, the
OOB-hit — the verbatim excerpt — `evidence-rules.md`.
