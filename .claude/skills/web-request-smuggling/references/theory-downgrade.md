# Theory — the downgrade desync

## The translation-layer — h2 → h1

```text
client-h2 → front-end (h2) → translate → back-end (h1)
```

The front-end translates h2 frames into h1 text — the translation
INVENTS the h1 boundary — the boundary may not match what the back-end
computes — `http2-smuggling.md`.

## The pseudo-header → request-line — `:path` → `GET /path`

```text
:method GET
:path /admin
```

→

```text
GET /admin HTTP/1.1
```

The pseudo-headers map to the request-line — a `:` value carrying
`\r\n` folds the request-line — `http2-smuggling.md`.

## The h2 headers → h1 headers — `content-length` → `Content-Length`

```text
:method POST
:path /
content-length 0
```

→

```text
POST / HTTP/1.1
Content-Length: 0
```

The h2 `content-length` header re-emits as h1 `Content-Length` — the
back-end honors it — H2.CL.

## The h2 forbids TE — but the downgrade emits it

```text
:method POST
transfer-encoding chunked
```

h2 forbids `transfer-encoding` — a front-end that forwards it → the
h1 back-end honors it → H2.TE.

## The DATA-frame → body-bytes — the frame-length trust

h2 DATA frames carry explicit lengths — the front measures the body
by frames — the h1 re-emit may carry a different `Content-Length` —
the frame-vs-header desync.

## The h2 SETTINGS → HPACK — the compression-state

`HTTP2-Settings:` carries HPACK state — a settings-mismatch → different
HPACK decoding → header-desync.

## The h2 RST_STREAM — the abort-frame

```text
RST_STREAM stream-id
```

A stream-abort — the back-end's h1 equivalent is a connection-close —
a state-desync.

## The h2 PRIORITY — the stream-order

h2 PRIORITY frames reorder streams — the h1 re-emit has no priority —
an order-desync.

## The h2-only headers — `:authority` → `Host:`

```text
:authority t
```

→

```text
Host: t
```

The `:authority` maps to `Host:` — a `:authority` carrying a smuggle —
`virtual-host.md`.

## The h2 CONTINUATION — the header-block split

```text
HEADERS + CONTINUATION frames
```

A header-block split across frames — the h1 re-emit joins them — a
header-block desync.
