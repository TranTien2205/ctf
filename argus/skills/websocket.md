# WebSocket security

**When:** `ws://`/`wss://` endpoints, Socket.IO (`/socket.io/`),
live features (chat, feeds, games, collab). HTTP tools can't speak the
channel directly - map the handshake first, then reason about the protocol.

## Handshake checks (http_request CAN do this)

1. GET the ws endpoint with `Upgrade: websocket`, `Connection: Upgrade`,
   `Sec-WebSocket-Key: <b64>`, `Sec-WebSocket-Version: 13`, and
   `Origin: https://evil.example` ->
   - `101` with a foreign Origin accepted = **cross-site WebSocket
     hijacking** (CSWSH): a victim's browser opens an authenticated ws from
     your page. Same impact class as CSRF+CORS combined.
2. Replays/missing auth: is the handshake itself authenticated? A ws that
   opens with no cookie at all on a privileged channel is its own finding.
3. `Sec-WebSocket-Protocol` confusion: some apps authorize on subprotocol
   strings.

## Message-channel reasoning (read the JS first)

js_recon output tells you message shapes (`{"type":"x","data":{...}}`).
For each shape the front-end sends, ask:

- Is the message JSON reachable into a SQL/command/template sink? Ws
  injection = same classes as HTTP.
- Are there server->client messages only meant for other users?
  Subscribe to other channels/rooms: `{"join":"room-<other-tenant>"}`.
- Rate limiting on messages? Usually none - note flood/abuse potential.

## Socket.IO specifics

`GET /socket.io/?EIO=4&transport=polling` returns the session handshake
as JSON - you can read message traffic over plain polling HTTP. Unauth
polling endpoints leak channels and sometimes message history.

## Falsifier

Origin enforced, auth required on handshake, per-channel authz on
subscribe, and message payloads validated like HTTP input.

## Severity guide

CSWSH on authenticated channel: high. Cross-tenant message read: high.
Injection into sinks via messages: rate as that class. Missing
rate-limit alone: low-info.
