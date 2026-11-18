# Error analysis — reading the desync's error surface

## The 400 on the outer — the front rejected

A `400 Bad Request` on the DESYNC request — the front-end rejected the
ambiguous request — the smuggle never reached the back-end — `denies`.

## The 400 on the NEXT — the back rejected

A `400` on the NEXT normal request — the back-end rejected the smuggle —
the desync reached it but the smuggle's framing was wrong — check the
byte-count, the Host, the trailing fragment.

## The timeout — the hang

A response that hangs — the back-end is waiting for the rest of the
smuggle's incomplete request — a CL.TE signal — but needs 3x +
absent-on-control — `detection.md`.

## The connection-reset — the socket died

`ECONNRESET`/`RST` — the back-end killed the socket — the smuggle's
malformed request crashed the parser — or the front-end detected the
desync — a `denies` or a `inconclusive`.

## The 500 — the back-end's internal error

`500` — the smuggle reached the back-end and broke it — the smuggle
ran but errored — the byte-count or the path is wrong.

## The 404 — the smuggle's path is wrong

`404` — the smuggle ran but the path doesn't exist — the desync works,
the smuggle's path is wrong — check `internal-routes.md` for the
real path.

## The 302 — the redirect

`302` — the app's normal response — the smuggle didn't land — or the
route redirects — `evidence-rules.md`.

## The double-response — `HTTP/1.1 200` + `HTTP/1.1 404`

TWO status lines for one request — the back-end answered a request
the front never sent — `confirms` — `response-poisoning.md`.

## The "response to a different request" — the shifted queue

The response's headers/body match a DIFFERENT request than the one
sent — the queue is misaligned — `confirms`.

## The empty-response — the desync swallowed it

No response — the desync ate the response — the back-end's answer
went to a different socket — the queue is misaligned — `inconclusive`
unless repeatable.

## The error-body — the parser's message

`Bad Request: invalid chunk size` — the back-end's parser-rejection —
the chunk-grammar is wrong — `chunked-encoding.md`.

`Bad Request: duplicate Content-Length` — the dup-CL rejected —
`cl-manipulation.md`.

`Bad Request: header line too long` — the injected headers overflow —
the fold's size limit.

## The status-line-delta — `HTTP/1.0` vs `HTTP/1.1`

The smuggle's response carries a different protocol-version than the
normal — the back-end's h1.0 vs h1.1 — a protocol-version signal.
