# Desync mechanism — the parser's job

## The first boundary — `\r\n\r\n`

```text
METHOD path HTTP/1.1\r\n
Header: value\r\n
\r\n
```

The `\r\n\r\n` ends the headers — the parser's first boundary —
`header-boundary.md`.

## The second boundary — `Content-Length` / `Transfer-Encoding` / `close`

```text
Content-Length: 4   → body = 4 bytes
Transfer-Encoding: chunked → body = 0-terminated
neither → body = connection-close
```

`theory-primitives.md` — the three boundary-signals.

## The precedence — which signal wins

RFC 7230 §3.3.3 — TE wins over CL — but "TE" means the parser RECOGNIZED
`chunked` — `obfuscation.md`.

## The parser-states — the byte-machine

```text
STATE: request-line
  → read METHOD path HTTP/1.1\r\n
STATE: headers
  → read Name: value\r\n until \r\n\r\n
STATE: body
  → read CL bytes OR chunked
STATE: done / next-request
```

The parser's state-machine — the desync is a state-boundary error —
`theory.md`.

## The re-emit — the front's translation

```text
front-parser → re-emit → back-socket
```

The front re-emits the parsed request — the re-emit's framing is where
the disagreement lands — `smuggle-mechanism.md`.

## The desync — the boundary-shift

```text
front-boundary: |req1|req2|
back-boundary:  |req1|req2|
```

Different positions — `theory-primitives.md`.

## The upgrade — the parser-exit

`Upgrade:`/`CONNECT` — the parser stops — the tunnel — `tunneling.md`.

## The downgrade — h2 → h1

h2 frames → h1 text — the translator invents the boundary —
`theory-downgrade-deep.md`.

## The keep-alive — the shared socket

`Connection: keep-alive` — the next request exists — `queue-management.md`.
