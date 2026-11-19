# Message-side (deep) — the per-frame authz surface, complete

## The trust-model, formalized

```
authenticate(handshake) -> identity   (once)
for each frame: dispatch(action, fields)   (per frame, no re-auth)
```

The HTTP app's per-request `authorize(request.user, request.path)`
becomes a per-frame `dispatch(action, fields)` — and the per-frame
`authorize(user, action, field)` is what is missing.

## The four message-side mechanisms

### 1. The object-IDOR — a field names another's resource

`{"action":"read","id":"<other>"}` — the `id`/`room`/`channel`/
`conversation`/`document`/`object`/`user_id`/`account`/`org`/`tenant`
field crosses a principal boundary. `message-idor.md` is the deep file.

### 2. The action-dispatch — a privileged action

`{"action":"admin"}`/`{"action":"debug"}`/`{"action":"eval"}`/`{"type":
"internal"}` — the `action`/`type`/`event`/`cmd`/`method`/`op` dispatch
reaches a privileged handler. `action-dispatch.md`.

### 3. The identity/role spoof — the frame's claimed identity

`{"from":"<victim>"}`/`{"user_id":"<other>"}`/`{"role":"admin"}`/`{"sender":
"admin"}`/`{"user":{"role":"admin"}}` — the frame claims an identity the
handshake did not establish; the server trusts the frame.

### 4. The injection — a field reaches a sink

`{"q":"<sqli>"}`/`{"name":"{{7*7}}"}`/`{"file":"/flag"}`/`{"data":"<ser>"}` —
the payload classes' carriers. `injection-in-frames.md`.

## The read-side vs write-side split

- **read-side** — a frame that RETURNS another's data — `read`/`get`/
  `history`/`subscribe`/`open`/`load`/`list`/`dump` — the data-leak
- **write-side** — a frame that CHANGES state — `send`/`transfer`/`grant`/
  `set`/`broadcast`/`reset`/`delete` — the impact

A read-side oracle is the finding; a write-side frame that changes
state is the impact — confirm by a second read.

## The reply-shape verdicts

- `{"id":"victim","data":...}` — the object → a message-IDOR oracle
- `{"flag":...}`/`{"admin":...}` — a privileged reply → a dispatch gap
- `{"error":"forbidden"}`/`{"error":"unauthorized"}` — a real rejection
- `{"error":"unknown action"}` — the action was a guess, not a defense
- a `pong`/`ok`/`{"status":"ok"}` — surface, not a finding
- silence — a dropped frame — a gap, not a verdict
- a crash/`500` — a parser/branch differential — a noisy oracle

## The authz-context layers

- **handshake-bound identity** — the cookie/`?token=` user
- **frame-bound identity** — the `from`/`user_id`/`role` the frame sets
- **per-message scope** — the object's owner the frame names
- **the channel** — the room/namespace the socket joined

A finding crosses one of these: a frame that reads the handshake's
non-owned object (IDOR), claims a different identity (spoof), reaches a
privileged action (dispatch), or joins a restricted channel (membership).

## The message-side record

`message: <endpoint>: <idor|action|spoof|inject>: <field>: <verdict>` —
per-field per-mechanism, verbatim; the frame + the reply.
