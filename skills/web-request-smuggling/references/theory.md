# Theory — why two parsers disagree

## The model — the request is a byte-stream, not a structure

HTTP/1.1 is a TEXT protocol — the boundary between request N and
request N+1 is computed by parsing bytes — there's no frame marker —
the boundary is wherever a parser decides `Content-Length` or the
chunked grammar says it is. Two parsers that compute the boundary
differently see DIFFERENT requests.

## The authoritative-length problem — which header wins?

RFC 7230 §3.3.3: if both `Transfer-Encoding` and `Content-Length` are
present, `Transfer-Encoding` wins. But:

- the rule is a SHOULD, not a MUST — implementations differ
- `Transfer-Encoding: chunked` is the ONLY valid TE for h1.1 — what
  counts as "chunked" varies
- a malformed TE header may not be recognized as TE at all → the
  parser falls back to CL

The disagreement is the desync.

## The request-line boundary — `\r\n\r\n` + the body

```text
METHOD path HTTP/1.1\r\n     — request line
Header: value\r\n             — headers
\r\n                          — end of headers
<body>                        — CL bytes or chunked
```

The parser's job: find the end-of-headers (`\r\n\r\n`), then the
end-of-body (CL bytes or the `0\r\n\r\n` terminator) — whatever's
left is the NEXT request.

## The keep-alive pipeline — why "next request" exists

`Connection: keep-alive` (the h1.1 default) → one TCP socket carries
many requests — each request's boundary is computed relative to the
previous — a boundary-error shifts every subsequent request.

## The front-end's role — the translating parser

A reverse proxy PARSES the client's request, then RE-EMITS it to the
back-end — the re-emit is where the disagreement lands:

- the front parses body-boundary X
- the front re-emits the bytes it parsed, plus its own headers
- the back parses the re-emitted bytes — computes a different boundary

The disagreement between the front's parse and the back's parse is
the desync — the bytes the front calls "body" the back calls "next
request".

## The trust-boundary — the front-end's auth vs the back-end's

The front-end enforces auth, filters paths, injects headers — the
back-end trusts the front-end's output — a smuggle bypasses the front's
checks → the back-end runs the unfiltered request.

## The downgrade — h2 → h1

HTTP/2 is binary — frame boundaries are explicit lengths — the front
knows exactly where request N ends. When it translates to h1 it INVENTS
the h1 boundary — `content-length`/`transfer-encoding` headers inside
the h2 request get re-emitted → the back-end's h1 parser honors them →
the boundary shifts.

## The parser-taxonomy — the differing behaviors

| Behavior | Parsers |
|---|---|
| strict-RFC — reject CL+TE | nginx 1.17+, envoy, caddy |
| TE-wins | most modern |
| CL-wins | older apache, some frameworks |
| first-header-wins | some proxies |
| last-header-wins | some frameworks |
| lenient-TE-match | IIS, older stacks |
| obs-fold-accept | RFC-noncompliant |
| chunk-extension-skip | strict vs lenient |

## The request-smuggling exploit-classes — the impact ladder

1. **frontend-bypass** — the smuggle reaches a filtered route —
   `frontend-bypass.md`
2. **internal-route** — the smuggle reaches a loopback-only route —
   `internal-routes.md`
3. **queue-poison** — the smuggle's response goes to the wrong socket —
   `response-poisoning.md`
4. **session-hijack** — the smuggle's `Cookie:` takes the victim's —
   `session-hijack.md`
5. **cache-poison** — the smuggle's response caches — `cache-poison-via-smuggle.md`
6. **client-side-desync** — the smuggle runs as the next victim —
   `client-side-desync.md`
