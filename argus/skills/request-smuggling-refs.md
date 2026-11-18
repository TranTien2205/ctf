# Request smuggling — depth reference

Load once `probe_smuggle` confirmed a front/back parse disagreement and you
need the variant that fits the chain. Its raw sends write each ambiguous
request in one TCP write — then count status lines: a real desync answers a
request the front end never saw.

## The variant alphabet

| Variant | Disagreement |
|---|---|
| `TE: chunked` + `CL: n` | which length each layer believes (CL.TE vs TE.CL below) |
| `Transfer-Encoding: chunked␣` / case / duplicate | whether one layer even *saw* TE |
| `CL: 0` + real body | front reads 0 bytes, back reads the body |
| bare `\n` vs `\r\n` chunk endings | strict vs lenient chunk parser |
| `HTTP/1.1` pipelining on a shared front-end connection | response queue poisoning, not just desync |

## CL.TE — front trusts CL, back trusts TE

```text
POST / HTTP/1.1
Host: target
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

Front forwards 6 body bytes (`0\r\n\r\nG` — the smuggled `G` prefixes the next
request on the back-end connection). Confirmation: the *next* client request
gets a `G`-prefixed error (e.g. `GPOST`), not this request's response.

## TE.CL — front trusts TE, back trusts CL

```text
POST / HTTP/1.1
Host: target
Content-Length: 4
Transfer-Encoding: chunked

12
GET /404-or-forbidden HTTP/1.1

0


```

Front ends the message at the `0` chunk; the back reads `Content-Length: 4`
bytes of body (`12\r\n`) and treats `GET /404...` as a new request. Probe a
path that answers distinctly (planted 404 marker, proxy-blocked route).

## The measurement that matters

Send the ambiguous request in **one write** and count HTTP status lines:

- two status lines for one client request → desync confirmed
- the *next* request's response poisoned → queue poisoning confirmed
- one clean answer or dropped socket → falsified (layers share the parse)

A bare timeout proves nothing — nothing reached the back end as a second
request. `probe_smuggle` runs the clean control + CL.TE + TE.CL shapes and
reports which variant held; only escalate manually when its verdict is
ambiguous.

## Hidden-path smuggling

Front-end ACLs (e.g. `/admin` blocked at proxy) die when the back parses a
different request boundary — smuggle a request for the blocked path inside a
smuggled prefix, then confirm via the blocked content appearing in a later
response. Alternate-encode the internal address (decimal/hex/IPv6 forms) if
the front filter pattern-matches it.

## Upgrade smuggling (101 channel)

After `101 Switching Protocols` the proxy may forward bytes opaquely while
the back keeps parsing HTTP — a second request rides the "tunnel". Needs a
valid 101 with correct `Upgrade`/`Connection` headers and a non-default port
on the fetcher (default ports hit the proxy's own upgrade logic). Falsifier:
post-101 bytes dropped or socket closed — both layers ended HTTP together.

## Traps

- Keep the smuggled request complete in one write — a partial line buffers as
  "body" or "websocket data" and never parses.
- A poisoned shared connection can hit *other users'* responses on a live
  front end — confirm on your own sequential requests; note the blast radius
  honestly in the finding.
- HTTP/2-to-1.1 downgrade chains have their own class (H2.CL/H2.TE) — if
  `fingerprint` reported h2c or an h2 front end, the pseudo-header smuggling
  skill applies instead of this file.

## Severity guide

- Response-queue poisoning or hidden-path reach demonstrated: high
- Desync confirmed but exploitable surface not shown: medium-high
- Only ambiguous parse without a second request ever answering: note, not a
  finding
