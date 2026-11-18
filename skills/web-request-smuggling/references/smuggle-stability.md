# Smuggle stability — making the desync reliable

## The determinism — the pair must work every time

A desync that works 1-in-N times isn't enough — the byte-count, the
trailing fragment, the keep-alive all have to be exact —
`cl-te-desync.md`.

## The byte-count discipline — the `#1` failure

`Content-Length` counts BYTES — every `\r\n` is 2 — the chunk-size is
hex — the trailing fragment is required — count exactly, never estimate.

## The keep-alive lifetime — the socket's N-request limit

```nginx
keepalive_requests 100;
keepalive_timeout 75s;
```

The socket serves N requests then closes — a smuggle past the limit
never lands — `queue-management.md`.

## The pool-slot — which socket the victim hits

On a pooled connection the victim's request is assigned a pool slot —
your smuggle poisons one slot — the victim must hit it — `queue-management.md`.

## The timing-window — the queue-drain

The smuggle lands when the NEXT request arrives — a fast-draining queue
→ immediate — a slow queue → delayed — `queue-management.md`.

## The retry-safe — the idempotent smuggle

A smuggle that repeats the same `GET /admin` is retry-safe — a smuggle
that mutates state isn't — `internal-routes.md`.

## The connection-close signal — the socket's end

`Connection: close` on the smuggle's LAST request — the socket closes
after the smuggle — no tail-poison — `queue-management.md`.

## The back-pressure — the slow-back-end

A back-end that's slow to consume → the smuggle's bytes sit in the
socket-buffer → the desync's timing is off — the back-pressure problem.

## The TLS-resumption — the socket's TLS-state

A resumed TLS socket — the session-state persists — the smuggle's
request inherits it — a session-level smuggle — `queue-management.md`.

## The socket-buffer — the TCP-window

The smuggle's bytes sit in the TCP receive-buffer — the back-end's
parser reads them — the buffer's size affects the desync's timing.

## The pipelined-batch — the smuggle's position

```text
GET /a + GET /b + [smuggle] + GET /c
```

The smuggle inside a pipelined batch — the batch's boundary shifts —
`http-pipelining.md`.
