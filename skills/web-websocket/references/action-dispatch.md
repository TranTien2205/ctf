# Action dispatch — the privileged-action surface in the schema

## The dispatch model

The server routes each frame by a `action`/`type`/`event`/`cmd`/`method`
field — a dispatch table the client bundle defines. The UI shows a
subset; the schema accepts the full set. The hidden actions are the
privileged path.

## The action inventory — from the bundle

```bash
grep -riE '\.emit\(|\.send\(|action.*:|type.*:|event.*:|cmd.*:|method.*:' /tmp/bundle \
  | grep -oE '["'"'"'](action|type|event|cmd|method)["'"'"']\s*[:=]\s*["'"'"'][a-zA-Z_]+' | sort -u
# every named action/type/event the client knows
```

The client knows every action the schema accepts — the bundle is the
dispatch map.

## The privileged-action set — probe each

```json
{"action":"ping"}                   // the baseline
{"action":"admin"}                   // a privileged action
{"action":"debug"}                   // a debug/eval action
{"action":"eval","code":"..."}       // an eval — a stronger primitive
{"action":"broadcast","text":"..."}  // a broadcast the UI hides
{"action":"set_role","role":"admin"} // self-role-assign
{"action":"impersonate","user":"admin"}
{"action":"flag"}                    // a flag action
{"action":"config","key":"..."}      // a config-set
{"action":"reset","user":"admin"}    // a reset action
{"action":"grant","perm":"..."}      // a permission grant
{"action":"dump"}                    // a data-dump action
{"action":"sql","q":"..."}           // a query action
{"action":"exec","cmd":"..."}        // an exec action
```

Each named action the UI does not show is a candidate privileged path —
probe it; the reply (data/state-change) or the uniform-error decides.

## The role/permission field in the dispatch

```json
{"action":"admin","role":"admin"}       // a role field the client sets
{"action":"x","user":{"role":"admin"}}  // a nested role
{"action":"x","perm":["admin"]}         // a permission array
{"action":"x","debug":true}             // a debug flag
{"action":"x","internal":true}          // an internal flag
```

A `role`/`perm`/`is_admin`/`debug`/`internal`/`admin`/`privileged` field
the client sets — a self-granted privilege in the frame
(`web-mass-assignment`-shaped — the frame binds the role).

## The dispatch-by-side-effect

An action that does not reply but changes state — a `transfer`/
`grant`/`reset`/`broadcast` that succeeds silently. Confirm by a second
read (`{"action":"balance"}`/the HTTP state) — the state changed.

## The internal/admin-channel actions

```json
{"action":"subscribe","channel":"internal"}
{"action":"subscribe","channel":"admin-feed"}
{"action":"subscribe","channel":"system"}
{"action":"subscribe","channel":"debug"}
{"action":"subscribe","channel":"user-<other>"}
```

An internal/admin/system channel the schema lets anyone join — a
read-side privileged channel.

## The action-dispatch boundary

- `web-websocket` — the privileged action in the message schema
- `web-logic-flaw` — a workflow-skip/state-action the dispatch skips
- `web-mass-assignment` — a `role`/`perm`/`is_admin` the frame binds
- `web-command-injection`/`web-sqli` — an `exec`/`sql`/`eval`/`q` action
  carrying a payload — the payload's class owns it

## The dispatch record

`action: <name>: <privileged-effect|uniform-error>` — each action with
the verbatim reply or the state-change it produced; a uniform
`{"error":"unknown action"}` is a recorded negative.
