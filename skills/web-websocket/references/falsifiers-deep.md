# Falsifiers (deep) — the kill-map, five layers

## The layer kill-map

| Layer | A `uniform` rejection kills | The cell |
|---|---|---|
| handshake:Origin | CSWSH | `origin` |
| handshake:auth-binding | cookie-bound CSWSH | `binding` |
| handshake:no-auth | unauth channel | `unauth` |
| handshake:token | — (still a URL-leak finding) | `token` |
| handshake:subproto | the alt-protocol | `subproto` |
| message:idor | the object-read gap | `idor` |
| message:action | the dispatch gap | `action` |
| message:spoof | the identity gap | `spoof` |
| message:inject | the injection gap | `inject` |

## The uniform-rejection vocabulary

The reply must be a REAL rejection, verbatim:

- `{"error":"forbidden"}`/`{"error":"unauthorized"}`/`{"error":"access denied"}`
- `{"status":403}`/`{"status":401}`/a close-frame `1008`
- `{"error":"not found"}`/`{"error":"invalid"}` — a resource rejection
- a `400`/`422` validation rejection

NOT a real rejection (a weak-negative, re-probe with the real shape):

- `{"error":"unknown action"}`/`{"error":"invalid field"}` — the name
  was a guess, not a defense
- `{"error":"bad request"}`/`{"error":"malformed"}` — a framing error
- silence/drop — a gap, not a verdict
- a crash/`500` — a differential, not a rejection

## The kill-map per mechanism

### The Origin/CSWSH kill-map

- `403`/close on EVERY foreign `Origin` + every bypass (`null`/`file:`/
  `*.target`/`target.evil`/no-`Origin`) → the Origin check is enforced —
  the `origin` cell is `uniform`
- `101` on a foreign `Origin` BUT no cookie-binding → no CSWSH (the
  `binding` cell fails) — a weaker finding remains
- `101`+cookie BUT `SameSite=Strict` → the browser blocks it (a defense,
  not a server gap) — CSWSH is not browser-exploitable

### The unauth kill-map

- `401`/`403`/close on a no-credential `101` → the upgrade is authed —
  `unauth` is `uniform`
- a `101`+no-credential that drops every frame → a closed channel —
  not `uniform`-safe, just unresponsive

### The IDOR kill-map

- `forbidden`/`404`/`401` on EVERY `id`/`room`/`channel`/`user_id`/
  `tenant` mutation → the object-scope check is enforced — `idor` `uniform`
- a `404`/`not found` on a guessed nonexistent id → a weak-negative —
  the REAL check is a KNOWN other's id

### The action kill-map

- `unknown action`/`forbidden` on EVERY privileged action → the dispatch
  checks role/whitelist — `action` `uniform`
- `unknown action` on a GUESSED action → a weak-negative — the bundle's
  real action set is the check

### The spoof kill-map

- `forbidden`/the `from`/`user_id`/`role` field ignored on EVERY mutation
  → the handshake's identity is authoritative — `spoof` `uniform`

### The inject kill-map

- the payload echoed RAW/uninterpreted + the sink-class's own oracle
  fails (no `49`/`SLEEP`-delay/`id` output) → the sink is escaped/
  absent — `inject` `uniform`

## The falsifier record

`falsifier: <layer>:<cell>: <the uniform reply verbatim>` — a `uniform`
cell is a measured dead end; a `weak-negative` names the re-probe that
would reopen it.
