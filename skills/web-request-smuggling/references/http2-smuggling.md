# HTTP/2 smuggling — the binary-frame desync

## The model — h2 frames are binary, h1 is text

HTTP/2 measures a request's boundary by FRAME lengths — the front-end
knows exactly where request 1 ends. The disagreement is at the
**downgrade**: when the h2 front-end translates to h1 for the back-end,
the translator invents h1 boundaries that may not match what the back-end
computes.

## H2.CL — the h2 `content-length` header trust

```text
:method POST
:path /
:authority t
content-length 0
```

h2 request carrying `content-length: 0` → the front-end's frame says the
body is empty (it's measured by frames, not headers) → the h2→h1
downgrade emits `Content-Length: 0` AND the h2 DATA frame's actual bytes →
the back-end sees `CL: 0` + unexpected body bytes → desync.

## H2.TE — the injected `transfer-encoding`

```text
:method POST
:path /
:authority t
transfer-encoding chunked
```

h2 forbids `transfer-encoding`, but a front-end that translates without
stripping it emits `Transfer-Encoding: chunked` to the h1 back-end →
the back-end chunks the body the front measured by frames → desync.

## The pseudo-header smuggle — `:path` carrying a path

```text
:method GET
:path /admin
:authority t
```

Pseudo-headers map to the h1 request line — `:path /admin` translates to
`GET /admin HTTP/1.1` — a `:` prefixed value the front-end treats as
metadata but the back-end treats as the request line — a `:` smuggle.

## The request-line fold via `:path`

```text
:method GET
:path /?q=x HTTP/1.1\r\nHost: internal\r\n\r\nGET /admin
```

`:path` carrying literal `\r\n` → the downgrade emits them into the h1
request line → a request-line smuggle — the back-end sees two request
lines.

## The h2c cleartext upgrade — `Upgrade: h2c`

```text
GET / HTTP/1.1
Upgrade: h2c
Connection: Upgrade, HTTP2-Settings
HTTP2-Settings: AAMAAABkAARAAAAAAAIAAAAA
```

`h2c` upgrades h1 to h2 cleartext — the front-end then speaks h2 — the
back-end may still speak h1 → the tunnel carries h2 frames the back-end
re-parses as h1 — a downgrade smuggle.

## The h2 header-case trick — `Content-Length` vs `content-length`

h2 headers are lowercase — `Content-Length` (capitalized) is illegal h2 —
a front-end that forwards it to the h1 back-end may case-fumble → the
back-end sees `Content-Length` it parses, the front-end ignores it as
invalid-h2 — a case-desync.

## The h2 DATA-frame padding — the DATA boundary mismatch

h2 DATA frames carry an explicit length — a padded DATA frame whose
declared length != the payload size → the downgrade drops or keeps the
pad inconsistently → a length-desync at the padding.

## The front-end's h1-only downgrade — `X-HTTP2: no`

Some proxies translate h2→h1 unconditionally, emitting the h2 request's
h1 equivalent — the `content-length`, `transfer-encoding`, and pseudo-
headers all get re-emitted as h1 headers — each is a smuggle vector.

## The h2 SETTINGS frame — the HPACK desync

`HTTP2-Settings:` carries HPACK-compression state — a settings-frame
mismatch between front and back → different HPACK decoding → header
smuggle.

## The common h2 smuggle shapes — the checklist

| Shape | Desync |
|---|---|
| `content-length: 0` + DATA | H2.CL |
| `transfer-encoding: chunked` injected | H2.TE |
| `:path` with `\r\n` | request-line fold |
| `Upgrade: h2c` + h2 frames | cleartext-h2 |
| Capitalized h2 header | case-fumble |
| Padded DATA frame | padding-desync |
| `Connection: Upgrade, HTTP2-Settings` | h2c tunnel |
