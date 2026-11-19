# Negative results (deep) — what a dead end actually recorded

## The record shape

```
negative: <endpoint>:<cell>: <the probe> -> <the verbatim reply/drop>
         <the weak-negative caveat if any>
```

A `uniform` cell is DATA — it closes the cell and redirects the budget.

## The cell-by-cell dead ends

### `origin` — CSWSH closed

```
negative: /ws:origin: --origin 'https://evil.example' -> 403 Forbidden
         + null/file:///*.target/target.evil/no-Origin all -> 403
         (the Origin check is enforced — CSWSH closed)
```

### `binding` — the cookie does not bind

```
negative: /ws:binding: Cookie:session=victim -> {"user":"anonymous"}
         (the socket ignored the cookie — it wants ?token=)
```

### `unauth` — the socket needs credentials

```
negative: /ws:unauth: no-cookie 101 -> every frame dropped
         (the upgrade opens but no data flows without a token)
```

### `idor` — the object check holds

```
negative: /ws:idor: {"action":"read","id":"victim"} -> {"error":"forbidden"}
         + id=2,3,4 / room=admin / channel=internal -> forbidden
         (the per-object scope check is enforced)
```

### `action` — the dispatch checks role

```
negative: /ws:action: {"action":"admin"} -> {"error":"forbidden"}
         + debug/internal/system/eval/exec -> forbidden/unknown
         (the dispatch whitelist is enforced)
```

### `spoof` — the frame identity is ignored

```
negative: /ws:spoof: {"from":"victim",...} -> sent as <handshake-user>
         + user_id/role/sender mutations -> ignored/forbidden
         (the handshake identity is authoritative)
```

### `inject` — the sink is safe

```
negative: /ws:inject: {"q":"{{7*7}}"} -> "{{7*7}}" (raw, not evaluated)
         + ' OR 1=1 / ;id / ../../ / <!ENTITY -> raw/error
         (the fields do not reach a sink unescaped)
```

### `subproto` — only the intended protocol

```
negative: /ws:subproto: graphql-ws/stomp/mqtt -> 400/close
         (the server only speaks the intended sub-protocol)
```

## The weak-negative — the caveat that reopens

- `unknown action` on a GUESSED action → re-probe with the bundle's
  real action set
- `not found` on a guessed id → re-probe a KNOWN other's id
- `malformed`/`bad request` → the framing was wrong — re-send the
  envelope's real shape
- a `uniform` at the wrong framing → re-run at the real envelope
- a drop with no reply → the channel may process silently — re-check
  the state

## The dead-end discipline

- a `uniform` cell is CLOSED — do not re-probe it
- a `weak-negative` names the re-probe — run it before closing
- a `gap`/drop is NOT a verdict — record it as `gap`, not `uniform`
- record every cell in the coverage matrix — the negative is the budget
  redirect

## The honest-negative rule

A `uniform` result is reported as measured, not as "probably safe" — the
verbatim reply IS the measurement. A `weak-negative` is reported as a
weak-negative with the re-probe named — never inflated to `uniform`.
