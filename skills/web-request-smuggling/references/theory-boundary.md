# Theory — the request-boundary problem

## The byte-stream — the request is text

```text
POST /a HTTP/1.1\r\nHost: t\r\nContent-Length: 4\r\n\r\nA=1&
```

One byte-stream — the boundary between request N and N+1 is COMPUTED —
there's no frame marker — the parser finds the boundary — `theory.md`.

## The boundary-computation — three signals

```text
1. \r\n\r\n — end of headers
2. Content-Length: N OR Transfer-Encoding: chunked — end of body
3. (neither) — connection-close
```

`theory-primitives.md`.

## The parser's state — the byte-machine

```text
request-line → headers → body → next-request
```

The parser's state-machine — `desync-mechanism.md`.

## The disagreement — two parsers, two boundaries

```text
front-boundary:  |req1|req2|
back-boundary:   |req1|req2|
```

Different positions — `theory-primitives.md`.

## The precedence — `Transfer-Encoding` over `Content-Length`

RFC 7230 §3.3.3 — TE wins — but "TE" means the parser RECOGNIZED `chunked`
— `obfuscation.md`.

## The keep-alive — the next-request exists

`Connection: keep-alive` — the socket carries many requests —
`queue-management.md`.

## The trust — the back trusts the front's output

The back-end trusts the front's re-emitted request — `smuggle-mechanism.md`.

## The upgrade — the parser-exit

`Upgrade:`/`CONNECT` — the parser stops — `tunneling.md`.

## The downgrade — h2 → h1

h2 frames → h1 text — the translator invents the boundary —
`theory-downgrade-deep.md`.

## The parser's quirks — the implementation-level

`parser-quirks.md` — the specific behaviors.
