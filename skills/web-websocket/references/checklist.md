# Checklist — the pass, box by box

## Recon

- [ ] `bundle_miner`/`web-source-map` the front-end → `wss?://|socket.io|
      sockjs|stomp|\.emit|\.send\(` → endpoint + client lib + schema
- [ ] the bundle's `ws.onopen`/`socket.emit`/`ws.send` → the first frames
- [ ] the handshake headers — `Cookie`/`Authorization`/`?token=`/`Origin`
- [ ] the `Set-Cookie: SameSite=` on the session cookie
- [ ] the framing — raw/Socket.IO/SockJS/STOMP/graphql-ws/protobuf

## Handshake-side

- [ ] foreign `Origin` → `101` or `403`? (the CSWSH check)
- [ ] the Origin-bypass set — `null`/`file:`/`*.target.com`/`target.evil`
- [ ] cookie-binding — does `Cookie: session=` bind the socket?
- [ ] a no-cookie `101` — an unauth channel?
- [ ] `?token=`/`?jwt=`/`?key=`/`?auth=` on the URL?
- [ ] `Sec-WebSocket-Protocol` — an alternate protocol accepted?
- [ ] `Authorization`/custom-header — does it select a privileged path?

## Message-side — one field per connection

- [ ] `id`/`object`/`doc`/`item` — another's object
- [ ] `room`/`channel`/`conversation`/`topic` — a restricted channel
- [ ] `user_id`/`user`/`uid`/`org`/`tenant` — another's record/tenant
- [ ] `to`/`target`/`recipient` — a write-routing gap
- [ ] `action`/`type`/`event`/`cmd`/`method` — a privileged action
- [ ] `role`/`perm`/`is_admin`/`debug`/`internal`/`scope` — a self-grant
- [ ] `from`/`sender`/`user_id`/`role` — an identity/role spoof
- [ ] `q`/`search`/`filter`/`where`/`name`/`file`/`xml`/`data` — injection

## The verify

- [ ] one field per connection — no concurrent payloads
- [ ] the reply is victim-data or a state-change — not a `pong`/`ok`
- [ ] `FAKE`/`FAKE2` (a second other-id) confirms the delta is the
      principal-class not a one-off
- [ ] the frame is the verdict — not the HTTP twin's `403`

## The record + route

- [ ] each confirmed frame → verbatim + the class route
- [ ] each uniform cell → a recorded negative
- [ ] the coverage matrix — every `endpoint × check` cell marked
- [ ] `../field-notes.md` updated
- [ ] the budget respected — 5/15 per mechanism class
