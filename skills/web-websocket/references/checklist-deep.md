# Checklist (deep) — the exhaustive pass, every box

## Phase 0 — the intake

- [ ] `bundle_miner`/`web-source-map` the front-end — the bundle is out
- [ ] the ws endpoint(s) named — `/ws`/`/socket.io`/`/sockjs`/`/stomp`/
      `/graphql`/`/mqtt`/etc.
- [ ] the client library named — the framing is known
- [ ] the URL params named — `?token=`/`?jwt=`/`?EIO=`/`?transport=`/
      `?sid=`/`?key=`/`?auth=`
- [ ] a live feature noted — the channel's purpose
- [ ] `ws_probe.py --selftest` — the tool works
- [ ] `proto_decode.py` present — the binary path

## Phase 1 — the handshake

- [ ] the baseline `101`/`401`/`403`/`426` measured
- [ ] the foreign `Origin` — `101`-accepted / `403`-checked
- [ ] the Origin-bypass set run — `null`/`file:`/`*.target`/`target.evil`/
      `sub.target`/`target.com.evil`/`eviltarget`/`targetcom`/no-`Origin`
- [ ] the cookie-binding — `Cookie:session` -> the bound identity / `anonymous`
- [ ] the bearer-binding — `Authorization:Bearer` -> the bound identity
- [ ] the token-binding — `?token=<jwt>` -> the bound identity
- [ ] the custom-header — `X-Api-Key`/`X-Auth-Token` -> the bound identity
- [ ] the no-auth open — a `101`+data / a `101`+drop-all / a `401`
- [ ] the `Sec-WebSocket-Protocol` — the accepted sub-protocol
- [ ] the `Sec-WebSocket-Extensions` — `permessage-deflate`/etc.
- [ ] the `Set-Cookie: SameSite=` on the login — the CSWSH leg
- [ ] the `101`-reply headers — `Sec-WebSocket-Accept`/`X-`/`Set-Cookie`
- [ ] a first-frame auth — `{"type":"auth"}`/`40{"token"}`/`connection_init`/
      `CONNECT` — the auth-in-frame shape

## Phase 2 — the schema + the framing

- [ ] the bundle's `ws.send`/`socket.emit`/`stompClient.send` read — the
      real first-frames
- [ ] the bundle's `ws.onmessage`/`socket.on`/`stompClient.subscribe` read
      — the expected replies
- [ ] the action set — the real `action`/`type`/`event`/`cmd`/`method`/
      `op`/`verb`/`kind` names
- [ ] the field names — the `id`/`room`/`channel`/`user_id`/`role`/`from`/
      `q`/`filter`/`file`/`token`/`subscribe`/`destination`/`topic`
- [ ] the framing decided — raw/`42[...]`/`a[...]`/STOMP/`{"type":}`/
      binary-MQTT/protobuf

## Phase 3 — the message cells (one field per connection)

- [ ] `id`/`doc`/`object`/`item`/`record`/`file`/`note`/`message`/`thread`/
      `ticket`/`order`/`invoice` — the object-IDOR
- [ ] `room`/`channel`/`conversation`/`topic`/`destination`/`namespace` —
      the membership-IDOR
- [ ] `user_id`/`uid`/`account`/`org`/`tenant`/`project`/`entity` —
      the cross-principal read
- [ ] `to`/`target`/`recipient`/`for_user`/`subject_id` — the write-routing
- [ ] `action`/`type`/`event`/`cmd`/`command`/`method`/`op`/`verb`/`kind`/
      `do`/`fn`/`handler`/`route`/`call`/`name`/`sub`/`exec` — the dispatch
- [ ] `role`/`perm`/`perms`/`permission`/`scope`/`level`/`tier`/`rank`/
      `is_admin`/`isAdmin`/`admin`/`debug`/`internal`/`privileged`/`sudo`/
      `superuser`/`staff`/`moderator` — the self-grant
- [ ] `from`/`sender`/`user`/`principal`/`subject`/`actor`/`author`/
      `owner`/`creator`/`account_id`/`as_user`/`impersonate` — the spoof
- [ ] `q`/`search`/`query`/`filter`/`where`/`order`/`sort`/`field`/`column`/
      `select`/`match`/`criteria`/`expression`/`clause` — the query-inject
- [ ] `name`/`text`/`tpl`/`msg`/`input`/`value`/`template`/`content`/`body`/
      `message` — the SSTI/inject surface
- [ ] `file`/`path`/`filename`/`doc`/`name` — the LFI surface
- [ ] `host`/`cmd`/`exec`/`command`/`target` — the CMDi surface
- [ ] `url`/`fetch`/`webhook`/`callback`/`image`/`import` — the SSRF surface
- [ ] `xml`/`data`/`import`/`parse`/`svg`/`session`/`obj`/`config`/`set`/
      `merge`/`key`/`value` — the deser/XXE/pollution surface
- [ ] `__proto__`/`constructor`/`prototype` — the pollution surface
- [ ] `token`/`auth`/`jwt`/`session`/`key`/`session_id`/`resume`/`reconnect`/
      `seq`/`offset`/`lastEventId`/`api_key`/`secret`/`credential` — the
      auth/resume surface
- [ ] `subscribe`/`join`/`watch`/`listen`/`follow`/`unsubscribe`/`feed`/
      `event_name`/`channel`/`topic`/`destination`/`namespace` — the
      subscription surface

## Phase 4 — the verdict + the route

- [ ] each `oracle` recorded — the verbatim reply + the route
- [ ] each `uniform` recorded — the verbatim rejection + the cell
- [ ] each `weak-negative` recorded — the re-probe named
- [ ] each `gap` recorded — the cell is unmeasured
- [ ] the `post-probe` --evidence ⊂ --response — checked

## Phase 5 — the record + the escalate

- [ ] the coverage matrix — every `endpoint × check` cell marked
- [ ] `../field-notes.md` — the endpoint/framing/auth/verdicts
- [ ] the budget ledger — within 5/15 + 25/45
- [ ] a one-field-per-connection — no concurrent payloads
- [ ] the escalate — chain_match/reclassify/writeup_search/novel_plan/
      fanout_sweep/solver_handoff when uniform-all

## The checklist-record

`checklist: <phase>: <the boxes ticked>: <the cells>` — each phase's
coverage; the cells the phase closed.
