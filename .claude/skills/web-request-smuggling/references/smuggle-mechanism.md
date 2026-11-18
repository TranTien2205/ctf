# Smuggle mechanism — the byte-level mechanics

## The parse-then-re-emit — the front's job

```text
client-bytes → front-parser → front-re-emit → back-socket
```

The front parses your bytes — re-emits them as a new request to the
back — the re-emit's framing is where the disagreement lands —
`theory.md`.

## The back's parse — the second parse

```text
back-socket → back-parser → handler
```

The back-end parses the re-emitted bytes — computes its own boundary —
the disagreement — `theory.md`.

## The boundary-shift — what the desync IS

```text
front's boundary:  |req1-end|req2-start|
back's boundary:   |req1-end|req2-start|  — different position
```

The smuggle's bytes land at the boundary-shift — `theory-primitives.md`.

## The keep-alive — the next-request exists

`Connection: keep-alive` — the socket carries many requests — the
"next request" exists — `queue-management.md`.

## The pipeline — the batch

```text
req-1 + req-2 + req-3 on one socket
```

The pipelined batch — `http-pipelining.md`.

## The FIFO — the response-order

h1.1 responses come in request-order — a desync shifts the order —
`response-poisoning.md`.

## The smuggle's landing — where it lands

```text
[smuggle] lands at back's req-N boundary →
back runs it as a new request →
back's response goes to the next socket-slot
```

`smuggle-landing.md`.

## The readback — the next response

The smuggle's response goes to the next socket-slot — `smuggle-readback.md`.

## The trust — the back trusts the front

The back-end trusts the front's output — the smuggle bypasses the front's
checks — `frontend-bypass.md`.

## The smuggle's framing — the byte-count

The smuggle's own `Content-Length`/`Host:`/`trailing-fragment` must be
exact — `smuggle-traps.md`.
