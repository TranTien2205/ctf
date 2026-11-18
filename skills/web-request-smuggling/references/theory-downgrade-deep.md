# Theory deep — the downgrade's mechanics

## The h2 frame-structure — the binary format

```text
[length:3][type:1][flags:1][stream-id:4][payload]
```

Every h2 frame carries an explicit length — the front-end knows exactly
where the request's bytes end — `theory-downgrade.md`.

## The HEADERS frame — the pseudo-headers + headers

```text
HEADERS:
  :method GET
  :path /admin
  :authority t
  :scheme https
  content-length 0
```

The `:method`/`:path`/`:authority`/`:scheme` are pseudo-headers — they
map to the h1 request-line — `http2-smuggling.md`.

## The DATA frame — the body

```text
DATA:
  [length bytes of body]
```

The DATA frame's length IS the body-length — the front-end's body-
boundary is the frame-length — `http2-smuggling.md`.

## The translation — `:path` → `GET /path`

```text
:method GET :path /admin → GET /admin HTTP/1.1
```

The translator maps pseudo-headers to the request-line — a `:path`
carrying `\r\n` folds — `http2-smuggling.md`.

## The headers → headers — `content-length` → `Content-Length`

```text
content-length 0 → Content-Length: 0
```

The h2 `content-length` header re-emits as h1 `Content-Length` — the
back-end honors it — H2.CL — `http2-smuggling.md`.

## The forbidden-headers — `transfer-encoding` in h2

h2 FORBIDS `transfer-encoding` — a front-end that forwards it → the
h1 back-end honors it → H2.TE — `http2-smuggling.md`.

## The h2-only frames — RST_STREAM / PRIORITY / SETTINGS

```text
RST_STREAM stream-id    — abort
PRIORITY stream-id       — reorder
SETTINGS                 — HPACK state
```

No h1 equivalent — a translator that drops them vs one that fakes them —
`theory-downgrade.md`.

## The CONTINUATION frame — the header-block split

```text
HEADERS + CONTINUATION + CONTINUATION
```

A header-block split across frames — the h1 re-emit joins them —
`theory-downgrade.md`.

## The ALPN — the protocol-negotiation

```text
TLS ALPN: h2
```

The ALPN negotiates h2 — a client forcing `h2` when the back expects
`h1` — `advanced-reach.md`.

## The HPACK — the header-compression

The h2 headers are HPACK-compressed — a SETTINGS-frame mismatch →
different HPACK decoding — `theory-downgrade.md`.
