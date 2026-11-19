# Negative results — the measured dead ends, verbatim

## The record shape

```text
negative: <endpoint>:<cell>: <the probe> -> <the verbatim reply/drop>
         <the weak-negative caveat if any>
```

## The handshake negatives

```text
negative: /ws:origin: --origin 'https://evil.example' -> 403 Forbidden
         + null/file:///*.target/target.evil/sub.target/target.com.evil/
           eviltarget/targetcom/no-Origin all -> 403
         (the Origin check is enforced — CSWSH closed)

negative: /ws:unauth: no-cookie 101 -> every frame dropped
         (the channel opens but no data flows without a credential —
          a gap, not a finding)

negative: /ws:binding: Cookie:session=victim -> {"user":"anonymous"}
         (the cookie did not bind — the socket wants ?token=)

negative: /ws:subproto: graphql-ws/stomp/mqtt -> 400/close
         (only the intended protocol is accepted)

negative: /ws:auth: no-credential -> 401 Unauthorized
         (the upgrade requires credentials — the channel is closed)
```

## The message negatives

```text
negative: /ws:idor: {"action":"read","id":"victim"} -> {"error":"forbidden"}
         + id=2,3,admin / doc=admin-doc / room=internal / channel=secret /
           user_id=2 / org=acme -> forbidden
         (the per-object scope check holds)

negative: /ws:action: {"action":"admin"} -> {"error":"forbidden"}
         + debug/internal/system/eval/exec/flag/config/broadcast/
           impersonate/grant/reset/dump/export -> forbidden/unknown
         (the dispatch checks role — the action cell is closed)

negative: /ws:spoof: {"from":"victim","action":"x"} -> acts as <handshake-user>
         + user_id/sender/user/author/actor -> ignored/forbidden
         (the handshake identity is authoritative)

negative: /ws:grant: {"action":"x","role":"admin"} -> ignored/forbidden
         + perm/is_admin/scope/level/debug/internal/sudo -> ignored
         (the grant field is not bound)

negative: /ws:inject: {"q":"{{7*7}}"} -> "{{7*7}}" (raw, not evaluated)
         + ' OR 1=1 / ;id / ../../ / <!ENTITY / {__proto__} -> raw/error
         (the fields do not reach a sink unescaped)

negative: /ws:subscribe: {"action":"subscribe","channel":"internal"} ->
         {"error":"forbidden"}
         + join room=admin / watch doc=x / listen topic=internal -> forbidden
         (the membership check holds)

negative: /ws:write: {"action":"transfer","to":"me","amount":1} ->
         {"error":"forbidden"} ; a second {"action":"balance"} -> no change
         (the write-side is enforced)

negative: /ws:resume: {"session_id":"<old>"} -> {"error":"re-auth required"}
         + resume/reconnect/seq/offset/lastEventId -> re-auth
         (the resumption checks auth — no resumption gap)
```

## The weak-negatives — the re-probe named

```text
weak-neg: /ws:action: {"action":"admin"} -> {"error":"unknown action"}
         (the action-NAME was guessed — re-probe the bundle's real set)

weak-neg: /ws:idor: {"action":"read","id":"FAKE-uuid"} -> {"error":"not found"}
         (the id was guessed — re-probe a KNOWN other's id)

weak-neg: /ws:frame: {"action":"x"} -> {"error":"malformed"}
         (the envelope is wrong — send the 42["x",{...}]/a[...]/STOMP
          shape — a framing error, not a rejection)

weak-neg: /ws:field: {"action":"x","theField":"y"} -> {"error":"invalid field"}
         (the field-NAME was guessed — the bundle's real field names)
```

## The gaps — the unmeasured cells

```text
gap: /ws:frames: {"action":"x"} -> (silence/drop)
     (the frame was ignored — the channel may process silently; a
      state-check or a different field)

gap: /ws:subscribe: {"action":"subscribe",...} -> a pong/ok/echo
     (a subscribe-only channel — the membership is the only check; a
      surface, not a finding)

gap: /ws:binary: a binary frame -> a binary reply
     (proto_decode.py frame.bin — the field-stream needs the decoder)
```

## The negative-discipline

- a `uniform` cell is CLOSED — do not re-probe
- a `weak-negative` names the re-probe — run it before closing
- a `gap`/drop is NOT a verdict — record it as `gap`, not `uniform`
- a `surface` reply is not a finding and not a `uniform`
- the negative IS the budget redirect — a measured dead end

## The negative-record

`negative: <cell>: <the verbatim reply> -> <the verdict> -> <the cell's
state>` — a measured reply, not an assumed one.
