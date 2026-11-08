# CL/TE desync: the classic disagreement

The front end reads `Content-Length`, the back end reads `Transfer-Encoding`
(or the reverse). The bytes one layer calls "body" the other calls "next
request".

## The measurement shape

Always send the ambiguous request **in one TCP write** and count the HTTP
status lines that come back — a real desync produces a response for a request
the front end never saw.

**Probe that worked** (Proxy):

```text
POST /allowed HTTP/1.1
Host: target
Content-Length: 7
Content-Type: application/json

{"a":1}

POST /banned-by-proxy-filter HTTP/1.1
Host: <alternate-encoded-internal-address>
Content-Length: 5

x=1
```

`{"a":1}` is 6 bytes + `\r\n` = 8, but `Content-Length: 7` leaves the front end
1 byte short — it forwards the tail of the "body" plus the whole second
request. The back end consumed the real boundary differently, and the banned
route answered.

Expected: two status lines for one client request, or the banned route's
response where the front end's filter should have stopped it. Falsifier: one
status line, or a dropped connection that answers nothing — the layers share a
body-length parse.

## The alphabet of desync

| Variant | What differs |
|---|---|
| `TE: chunked` + `CL: n` | which boundary each layer believes |
| `Transfer-Encoding: chunked ` (space/case/dupe) | whether a layer "saw" TE at all |
| `CL: 0` + real body | front ends at 0, back ends reads the body |
| bare `\n` vs `\r\n` chunk endings | strict vs lenient chunk parser |

## Falsifier

Every ambiguous byte shape produces either one clean answer or a rejected
request — no second status line ever appears. A timeout or dropped socket alone
is not a signal: it proves nothing reached the back end as a second request.

## Traps

- Count status lines, not "did it error" — a response belonging to a request
  the front end never saw is the only real confirmation.
- An internal address may need an alternate encoding (decimal, hex, IPv6 form)
  to pass the front end's own URL filter while the back end resolves it.
