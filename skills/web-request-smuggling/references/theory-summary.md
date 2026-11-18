# Theory summary — the desync in one file

## The request is a byte-stream with a computed boundary

```text
POST /a HTTP/1.1\r\nHost: t\r\nContent-Length: 4\r\n\r\nA=1&
```

The boundary between request N and N+1 is COMPUTED from `Content-Length`
or the chunked grammar — `theory-primitives.md`.

## Two parsers disagree — the front and the back

```text
client → front-parser → re-emit → back-parser → handler
```

The front parses, re-emits, the back parses — the disagreement between
the two parses is the desync — `smuggle-mechanism.md`.

## The pair-taxonomy — the seven disagreements

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

## The detection — the timing/differential oracles

`detection.md` — the hang (CL.TE), the 404-poison (TE.CL), the
obfuscation matrix (TE.TE), the dup-CL (CL.CL), the body-ignored (CL.0),
the h2 headers (H2.*), the fold (CRLF).

## The smuggle — the bytes between boundaries

`smuggle-landing.md` — the smuggle's bytes land at the boundary-shift —
the back-end runs them as a new request.

## The readback — the smuggle's output reaches you

`smuggle-readback.md` — the self-poison, the stored-param, the echo,
the OOB, the deferred.

## The impact — the ladder

`desync-ladder.md` — fold → desync → front-bypass → internal-route →
queue-poison → session-hijack → cache-poison → client-side-desync →
cross-protocol → upgrade-tunnel.

## The evidence — the verbatim excerpt

`evidence-rules.md` — a second response, a shifted queue, the smuggle's
output — never a timeout alone, never a 302, never an echo.

## The denied — the no-smuggle conditions

`denied-conditions.md` — no shared socket, strict-RFC front, h1-only
target, filtered fold.
