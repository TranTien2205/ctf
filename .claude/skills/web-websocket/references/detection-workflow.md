# Detection workflow — the ordered detection, with the decision points

## Step 0 — does a ws channel exist?

```bash
python3 tools/web/bundle_miner.py "$BASE" --out /tmp/bundle
grep -riE 'wss?://|new WebSocket|socket\.io|SockJS|stomp|pusher|ably|graphql-ws|mqtt' /tmp/bundle
```

- a `wss?://`/`new WebSocket`/`socket.io`/`stomp`/etc. -> YES, a channel
- nothing -> check the live features; a `chat`/`live`/`realtime`/`notif`
  UI word -> a probable channel; nothing -> no ws surface, route away

## Step 1 — which endpoint + which transport?

```text
the endpoint:  the bundle's wss?://... URL — /ws /socket.io /sockjs /
               /stomp /graphql /mqtt /api/ws /subscriptions /etc.
the transport: the client lib — raw / Socket.IO / SockJS / STOMP /
               Pusher / Ably / graphql-ws / MQTT
the framing:   raw / 42[...] / a[...] / STOMP / {"type":} / binary
```

## Step 2 — the handshake verdict

```bash
python3 tools/web/ws_probe.py "$WS/ws" --message '{}'                  # baseline
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --message '{}'  # origin
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"me"}'  # binding
python3 tools/web/ws_probe.py "$WS/ws" --message '{"action":"me"}'     # unauth
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: graphql-ws' --message '{}'  # subproto
curl -sI "$BASE/login" | grep -i 'set-cookie'                          # samesite
```

- `101` + foreign-Origin -> the origin gap / CSWSH-candidate
- `403` on all bypasses -> `uniform`: origin
- `101` + cookie-binding -> a bound channel
- `101` + no-cookie + data -> an unauth channel
- `101` + no-cookie + drop-all -> a closed channel (a gap)
- `401`/`403` -> the upgrade is authed — the credential cell
- `?token=` -> a credential-in-URL

## Step 3 — the schema + the framing

```text
the bundle's ws.send/socket.emit/stompClient.send -> the real frames
the bundle's action/type/event/cmd names          -> the dispatch keys
the bundle's id/room/channel/user_id/role names   -> the field set
the transport's envelope                           -> the send-shape
```

## Step 4 — the message verdicts — one field per connection

```bash
# the object-IDOR
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"read","id":"victim"}'
# the membership
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"join","room":"admin"}'
# the dispatch
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"admin"}'
# the spoof
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"from":"victim","action":"x"}'
# the inject
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"q":"{{7*7}}"}'
# the subscribe
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"subscribe","channel":"internal"}'
```

- another's object -> `oracle`: idor
- a pushed feed -> `oracle`: subscription-IDOR
- a privileged reply -> `oracle`: dispatch
- acts-as-other -> `oracle`: spoof
- the eval/read -> `oracle`: inject -> the payload class
- `forbidden`/`unauthorized` -> `uniform`
- `unknown`/`invalid`/`not found` -> `weak-negative`
- silence/drop -> `gap`
- `pong`/`ok`/`echo` -> `surface`

## Step 5 — the coverage + the verdict

```text
the matrix: every endpoint x check cell -> oracle/uniform/weak-neg/gap/
            unmeasured
the verdict: any oracle -> a finding; all uniform -> the socket is closed
             for this class; cells unmeasured -> the budget decides
the record:  field-notes.md + the verbatim replies + the route
```

## Step 6 — the route

```text
the oracle's class-route:
  message-IDOR        -> web-idor
  dispatch gap        -> web-auth-session / web-logic-flaw / the flag
  self-grant/spoof    -> web-mass-assignment / web-auth-session
  injection           -> the payload's class
  CSWSH               -> web-websocket (the four-leg chain)
  unauth channel      -> web-websocket / web-info-disclosure
  token-in-URL        -> web-auth-session / web-info-disclosure
  subscription-IDOR   -> web-idor
  graphql-over-WS     -> web-graphql
  resumption          -> web-websocket / web-auth-session
```

## The workflow-record

```
detect: <the pass>: <the verdicts>: <the cells>: <the route>
```

The workflow is the ordered pass — the endpoint -> the handshake -> the
schema -> the messages -> the verdict -> the route.
