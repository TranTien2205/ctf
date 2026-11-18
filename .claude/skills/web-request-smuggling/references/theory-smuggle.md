# Theory — the smuggle's mechanism

## The request is a byte-stream — the boundary is computed

```text
POST /a HTTP/1.1\r\nHost: t\r\nContent-Length: 4\r\n\r\nA=1&
```

`theory-primitives.md` — the boundary is computed, not marked.

## The two parsers — the front and the back

```text
client → front-parser → re-emit → back-parser → handler
```

`smuggle-mechanism.md` — the front parses, re-emits, the back parses.

## The disagreement — the boundary-shift

```text
front-boundary:  |req1|req2|
back-boundary:   |req1|req2|
```

`theory-boundary.md` — the boundary-shift is the desync.

## The smuggle's landing — the bytes between boundaries

```text
front's body-bytes = back's next-request-bytes
```

The smuggle lives at the boundary-shift — `smuggle-landing.md`.

## The next-request — the keep-alive queue

`Connection: keep-alive` — the next request exists —
`queue-management.md`.

## The smuggle's response — the shifted queue

```text
back's response-N → the next socket-slot
```

`response-poisoning.md` — the queue-poison.

## The trust — the back trusts the front's output

The back-end trusts the front's re-emitted request — `frontend-bypass.md`.

## The upgrade — the parser-exit

`Upgrade:`/`CONNECT` — `tunneling.md`.

## The downgrade — h2 → h1

`theory-downgrade-deep.md`.

## The smuggle's impact — the ladder

`desync-ladder.md` — the escalation order.
