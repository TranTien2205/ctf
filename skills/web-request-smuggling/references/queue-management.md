# Queue management — the connection-pool mechanics

## The keep-alive pool — the shared socket

`Connection: keep-alive` — the front-end reuses one socket to the
back-end for many client requests — the desync needs the shared socket
— `Connection: close` removes it — `denied-conditions.md`.

## The request-queue — the FIFO order

```text
client-A: req-A → front → back-socket
client-B: req-B → front → back-socket
client-C: req-C → front → back-socket
```

The back-end processes them FIFO — a smuggle inside req-A lands in
front of req-B — req-B's response is the smuggle's — `response-poisoning.md`.

## The queue-drain timing — when the smuggle lands

The smuggle lands when the NEXT request arrives — a fast-draining queue
→ immediate; a slow queue → delayed — `second-order.md`.

## The socket-reuse — the same TCP connection

```text
req-1 → response-1 → req-2 → response-2 on the same socket
```

The reuse is what makes the smuggle's "next request" exist — the
queue-poison's mechanism.

## The max-keep-alive — the socket's lifetime

```nginx
keepalive_requests 100;
keepalive_timeout 75s;
```

The socket serves N requests or T seconds — then closes — a smuggle
past the limit never lands — the pool's eviction.

## The front-end's pool — the per-back-end pool

```nginx
upstream backend {
    server 127.0.0.1:8000;
    keepalive 32;
}
```

The `keepalive 32` — 32 pooled connections to the back-end — a smuggle
lands on ONE of the 32 — the victim's request has to hit the same pool
slot — the queue-poison's non-determinism.

## The connection-pinning — which victim hits your socket

On a pooled connection the victim's request is assigned to a pool slot —
a smuggle poisons one slot — the victim has to land on it — the
non-deterministic poison.

## The serial-poison — the self-poison

```text
your-req-1 [smuggle] → your-req-2 → response-2 is the smuggle's
```

Your own sequential requests hit the same socket → the self-poison is
deterministic — `response-poisoning.md`.

## The queue-overflow — the smuggle under load

Under load the queue drains fast — the smuggle lands immediately —
under low load the smuggle waits — the timing affects detection.

## The socket-state — the TLS/session state

A TLS socket's session-state persists across requests — the smuggle's
request inherits the socket's TLS context — a session-level smuggle.
