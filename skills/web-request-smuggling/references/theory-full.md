# Theory — the complete model

## The request — a text-stream with computed boundaries

```text
POST /a HTTP/1.1\r\n
Host: t\r\n
Content-Length: 4\r\n
\r\n
A=1&
```

One byte-stream — the boundaries are computed — `theory-primitives.md`.

## The two parsers — the front and the back

```text
client → front-parser → re-emit → back-parser → handler
```

`smuggle-mechanism.md`.

## The boundary-signals — three ways to find the body's end

```text
Content-Length: N       — N bytes
Transfer-Encoding: chunked — 0-terminated
neither                 — connection-close
```

`theory-primitives.md`.

## The precedence — TE wins over CL

RFC 7230 §3.3.3 — but "TE" means the parser RECOGNIZED `chunked` —
`obfuscation.md`.

## The parser-states — the byte-machine

```text
request-line → headers → body → next-request
```

`desync-mechanism.md`.

## The pair-taxonomy — the disagreements

| Pair | Front | Back |
|---|---|---|
| CL.TE | CL | TE |
| TE.CL | TE | CL |
| TE.TE | TE-obf | TE-obf |
| CL.CL | CL-A | CL-B |
| CL.0 | CL | none |
| H2.CL | h2 | CL |
| H2.TE | h2 | TE |

`desync-taxonomy.md`.

## The keep-alive — the next-request

`Connection: keep-alive` — `queue-management.md`.

## The trust — the back trusts the front's output

`frontend-bypass.md`.

## The upgrade — the parser-exit

`Upgrade:`/`CONNECT` — `tunneling.md`.

## The downgrade — h2 → h1

`theory-downgrade-deep.md`.

## The smuggle — the bytes between boundaries

`smuggle-landing.md`.

## The readback — the smuggle's output

`smuggle-readback.md`.

## The impact — the ladder

`desync-ladder.md`.
