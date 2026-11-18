# Denied conditions — when the smuggle can't work

## No shared connection — `Connection: close`

A desync needs a REUSED keep-alive connection — the front-end pipelines
multiple requests on one socket. `Connection: close` or per-request
connections → no "next request" to poison → no desync.

## The front-end re-parses everything — the strict proxy

A proxy that re-parses every forwarded byte — re-chunks the body,
normalizes headers — removes the desync — the back-end sees the
normalized request, not yours.

## No TE/CL disagreement — both honor the same header

If front and back BOTH honor `Content-Length` or BOTH honor
`Transfer-Encoding` identically → no disagreement → no desync.

## The h1-only target — no h2 layer

`content-length`/`transfer-encoding` inside h2 headers only desync on
the h2→h1 downgrade — an h1-only target has no h2 layer to mistranslate.

## The strict-RFC parsers — the modern stacks

Newer nginx/HAProxy/envoy reject ambiguous requests — `400` on any
CL/TE conflict — the strict-RFC behavior removes the desync.

## The tunnel not removed — the proxy re-parses the upgrade

`Upgrade: websocket` doesn't always remove the front-end's parser —
some proxies re-parse the tunnel as HTTP → the smuggle inside a frame
is still parsed.

## The cookie/victim is on a different connection

Session-hijack needs the victim on the SAME connection — a per-client
socket or a front-end that doesn't pool → the victim never lands inside
your smuggle.

## The cache doesn't cache the smuggle's response

Cache-poison needs a cacheable response — `Cache-Control: private`,
`no-store`, or a Vary-keyed response → the smuggle's response doesn't
cache → no poison.

## The internal route is a different socket

`/admin` bound to `127.0.0.1:9000` — a separate listener — the smuggle
reaches the back-end's main listener, not `9000` — `Host: t:9000` may
route or may not.

## The CRLF-fold is filtered — the value is encoded

The `host` value is percent-encoded or validated → `%0d%0a` never
survives into the outbound request → no fold → no smuggle — the
falsifier in `../SKILL.md`.

## The record — the negative

Each denied-condition is a `denies` verdict — record it — the kill map
tells the next attempt which layers are dead:

```bash
python3 tools/hooks.py post-probe <name> \
  --request "POST / CL:0 TE:chunked body=GET /admin" \
  --verdict denies \
  --evidence "Connection: close" \
  --response "<the raw response>"
```
