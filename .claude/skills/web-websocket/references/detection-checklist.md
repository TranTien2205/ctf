# Detection checklist — the detection pass, box by box

## The endpoint inventory

- [ ] `bundle_miner`/`web-source-map` the front-end
- [ ] `grep` the bundle for `wss?://|new WebSocket|socket\.io|SockJS|
      stomp|pusher|ably|graphql-ws|createClient`
- [ ] the ws endpoint path(s) — `/ws`/`/socket`/`/socket.io/`/`/sockjs`/
      `/stomp`/`/graphql`/`/api/ws`
- [ ] the client library — raw/Socket.IO/SockJS/STOMP/Pusher/Ably/
      graphql-ws — the framing
- [ ] the URL params — `?token=`/`?jwt=`/`?key=`/`?auth=`/`?EIO=`/
      `?transport=`/`?sid=`
- [ ] a live feature (chat/presence/feed/doc/metric) that names the socket

## The handshake detection

- [ ] the baseline `101`/`401`/`403` — the channel opens / is authed
- [ ] the `Origin` probe — `101`-foreign/`403`-checked
- [ ] the `Cookie`/`Authorization`/`?token=` binding — the auth mechanism
- [ ] the `Set-Cookie: SameSite=` on the login — the CSWSH leg
- [ ] the `Sec-WebSocket-Protocol` the client requests — the sub-protocol
- [ ] the `Sec-WebSocket-Accept`/`Sec-WebSocket-Version`/`Sec-WebSocket-
      Extensions` — the negotiated params

## The schema detection

- [ ] the bundle's `ws.send`/`socket.emit`/`stompClient.send` — the
      first frames + the action set
- [ ] the bundle's `ws.onmessage`/`socket.on`/`stompClient.subscribe` —
      the reply shapes
- [ ] the field names — `action`/`type`/`event`/`id`/`room`/`channel`/
      `user_id`/`role`/`from`/`q`/`filter`/`file`/`token`/`subscribe`
- [ ] the framing — raw/`42[...]`/`a[...]`/STOMP/`{"type":...}`/binary

## The auth-model detection

- [ ] the handshake auth — cookie/`Authorization`/`?token=`/none
- [ ] the first-frame auth — `{"type":"auth"}`/`40{"token"}`/
      `connection_init`/`CONNECT`
- [ ] the binding — the socket's identity (the cookie's user)

## The coverage-start

- [ ] the `endpoint × check` matrix seeded — the unmeasured cells
- [ ] the per-endpoint framing + auth recorded
- [ ] the budget ledger started — 5/15 per class, 25/45 per challenge

## The detection-output

```
endpoint:  <the path(s)>
framing:   <raw|socket.io|sockjs|stomp|graphql-ws|mqtt|protobuf>
auth:      <cookie|token|bearer|none>
schema:    <the action/field set>
cells:     <the unmeasured matrix>
```

Detection ends when the schema + the auth + the framing + the cell-matrix
are known — the message-side probing starts.
