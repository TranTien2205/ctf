# Upgrade smuggling: the 101 channel

A protocol upgrade (`Upgrade: websocket`) ends HTTP parsing on that socket for
one layer but not necessarily the other. After `101 Switching Protocols`, what
the proxy forwards as opaque bytes may still be parsed as HTTP by the backend —
a second request rides through inside the "tunnel".

## Probe that worked (Percetron)

```text
GET /healthcheck?url=http://<your-host>:<non-default-port>/
    # your listener answers a bare 101 Switching Protocols
# then, on the same socket:
GET /healthcheck-dev?url=http://127.0.0.1:3000/
```

The fetch to the attacker host answered `101` — from that point the proxy
stopped parsing HTTP on the connection, but the backend's connection handling
still did. The second request, written as ordinary HTTP, reached the internal
`-dev` endpoint that the proxy's routing would never expose.

Expected: the internal endpoint's response arrives on a socket that, per the
proxy, is no longer HTTP at all. Falsifier: the second request is ignored or
the socket is closed after 101 — both layers ended HTTP together.

## Why the non-default port matters

The upgrade path must not be one the proxy already owns. A `url=` pointing at
port 443/80 may be short-circuited by the proxy's own upgrade logic; an
unusual port goes through the generic fetcher, which is where the divergent
handling lived.

## Falsifier

Every post-101 byte is dropped or the socket closes: both layers agree the
protocol switched and there is no tunnel to ride.

## Traps

- Your listener must send a *valid* `101` response with the right
  `Upgrade`/`Connection` headers — a malformed 101 may be rejected before the
  tunnel opens.
- Keep the second request small and complete in one write; a partial request
  can be buffered as "websocket data" and never parsed.
