# Common mistakes — why the desync doesn't work

## The byte-count — `Content-Length` is off by one

`Content-Length` counts BYTES — every `\r\n` is 2 — a one-byte-off CL
either truncates the body or hangs the connection — count the bytes,
don't estimate.

## The chunk-size is decimal — `60` means 60, not 0x60

Chunk sizes are HEX — `5c` = 92 bytes — writing `60` reads 60 bytes
which is NOT 0x60 (96) — convert to hex.

## The missing final-CRLF — the body never ends

`0\r\n\r\n` — the `\r\n` after the `0` is required — without it the
connection hangs waiting for the terminator.

## The smuggle without the trailing fragment

After the smuggled request append a fragment (`GET / HTTP/1.1`) so the
connection has something to close on — without it the smuggle's own
framing is unbounded → hang.

## The `Host:` doesn't match the vhost

The smuggle's `Host:` must match the back-end's vhost — `Host: t` vs
`Host: internal` route differently — a wrong Host 404s the smuggle.

## The connection isn't shared — keep-alive off

Desync needs a REUSED connection — `Connection: close` or per-request
connections can't desync — there's no "next request" to poison.

## The front-end re-parses the tunnel

`Upgrade: websocket` doesn't always remove the front-end's parser —
some proxies re-parse the tunnel as HTTP → the smuggle is still parsed.

## A timeout ≠ desync

A hang could be congestion — a desync-timeout repeats consistently +
is absent on the control — one timeout is `inconclusive`.

## A 400 ≠ rejection-of-the-smuggle

The front-end rejecting a malformed request is a parser-error, not a
desync — the smuggle never reached the back-end.

## A 302 ≠ confirmation

A redirect is the app's normal response — not proof the smuggle ran.

## The echo ≠ the smuggle

An echo of your input is reflection — a desync needs a SECOND response
or a shifted queue — `evidence-rules.md`.

## The smuggle works once — the cache poisons

A one-shot smuggle that caches poisons every subsequent visitor — use
a cachebuster `?cb=xyz` — `cache-poison-via-smuggle.md`.

## The h2-only desync on an h1 target

`content-length`/`transfer-encoding` inside h2 headers only desync on
the h2→h1 downgrade — an h1-only target doesn't have the h2 layer —
`http2-smuggling.md`.

## The `--selftest` not run

`tools/web/crlf_probe.py --selftest` — the tool proves itself offline —
run it before trusting the tool's output.
