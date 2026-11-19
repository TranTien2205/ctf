# Theory (deep) — the formal model of the WebSocket channel

## The protocol — the two phases

### Phase 1: the upgrade handshake — an HTTP request

```text
GET /ws HTTP/1.1
Host: target.com
Connection: Upgrade
Upgrade: websocket
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: <b64-16-bytes>
Sec-WebSocket-Protocol: <the-sub>
Origin: https://target.com
Cookie: session=<the-session>

<- HTTP/1.1 101 Switching Protocols
   Upgrade: websocket
   Connection: Upgrade
   Sec-WebSocket-Accept: <sha1(key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11")>
   Sec-WebSocket-Protocol: <the accepted sub>
```

The handshake is HTTP — it carries the HTTP auth (cookie/`Authorization`/
`?token=`), the `Origin` (the CSWSH surface), the `Sec-WebSocket-*`
negotiation. A `101` = the protocol switches; a `401`/`403`/`400`/`426`
= it did not.

### Phase 2: the frame stream — a bidirectional pipe

```text
frame = FIN|RSV|opcode|masked|len | mask-key | payload
opcode = 0x0 continuation | 0x1 text | 0x2 binary | 0x8 close | 0x9 ping
         | 0xA pong
masked = 1 for client->server | 0 for server->client
```

The frames are full-duplex — the client and server send independently;
a reply does NOT carry a request-id (except the app's own). The
application's message is the payload; the WS framing is the transport.

## The security model — the four gaps

### Gap 1: the Origin is not enforced by default

The browser SENDS `Origin` on the `new WebSocket` upgrade — but the
server is not REQUIRED to check it. A server that does not check the
`Origin` accepts a socket opened by ANY origin's page — and the browser
attaches the victim's cookies. This is the CSWSH precondition.

### Gap 2: the auth is a one-shot upgrade

The cookie/`?token=`/`Authorization` is read at the `101` — the socket
then lives for its duration. A message inside carries NO credentials —
the channel trusts the handshake's identity, not the frame's claimed
`user_id`/`role`/`from`.

### Gap 3: the message-side is unauthenticated by default

```python
async for msg in websocket:
    handler(msg)                    # NO per-message authz
```

The HTTP app's per-request `authorize(user, path)` becomes a per-frame
`dispatch(action, fields)` — the per-message `authorize(user, action,
field)` is routinely missing. The message-side IS the unenforced twin.

### Gap 4: the transport is a second API

The WS channel is a parallel API to the HTTP one — the same objects,
the same actions, a DIFFERENT authz implementation. The HTTP `403` on
`GET /api/objects/x` does NOT transfer to `{"action":"read","id":"x"}`.

## The trust-boundary model

```text
[the internet] --HTTP-upgrade--> [the WS server] --frames--> [the app]
                                    ^
                                    | the authz lives here —
                                    | if it checks only the upgrade,
                                    | the message-side is open
```

The boundary is the per-frame `dispatch` — the HTTP app's checks live
in the request-handler; the WS's checks must live in the frame-dispatch.
A frame-dispatch that does not re-check = the gap.

## The SameSite/CORS caveat — the browser defense

- `SameSite` is a BROWSER defense — it stops the victim's browser from
  sending the cookie on a cross-site `new WebSocket`
- the server still accepts the foreign `Origin` — the server-side gap
  remains; the browser just does not complete the chain
- a non-browser client (an attacker's socket) sends ANY `Origin` —
  the server-side check is what matters; the browser check is the
  exploitability of the cross-site chain

## The frame-vs-HTTP authz asymmetry

```text
HTTP:   GET /api/objects/x  -> authorize(cookie-user, objects, x) -> 403
WS:     {"action":"read","id":"x"} -> dispatch(read, {id:x}) -> the obj
        (no authorize(user, read, x) — the gap)
```

The asymmetry is the finding — the same resource, the same scope, a
different enforcement point.

## The theory-record

`theory: <the model>: <the gap it produces>` — the model names the gap;
the gap is measured, not assumed.
