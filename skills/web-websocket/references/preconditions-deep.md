# Preconditions (deep) — the required state, per mechanism

## The channel preconditions — for ANY finding

```text
P0: the target opens a ws:// / wss:// channel
    verify: a 101 on the upgrade — ws_probe -> 101 Switching Protocols
    falsifier: a 400/426/404 -> the endpoint is not a ws endpoint

P1: the channel carries data or actions
    verify: a frame produces a data/action reply — not a pong/ok/drop
    falsifier: every frame -> a drop/ok -> a closed/write-only channel

P2: a credential exists to bind OR the channel is unauth
    verify: a Cookie/token/session OR a no-credential data reply
    falsifier: a 101 that needs a credential you cannot supply
```

## The handshake-side preconditions

### The CSWSH preconditions — ALL FOUR

```text
C1: the foreign Origin is accepted — a 101, verbatim
    verify: --origin <foreign> -> 101
    falsifier: 403 on ALL bypasses -> Origin enforced

C2: the socket binds the victim SESSION-COOKIE
    verify: Cookie:session=victim -> {"user":"victim"} the bound identity
    falsifier: the socket wants ?token=/Bearer, not the cookie -> no
              browser-attachable credential

C3: the victim cookie is SameSite=Lax/None (it travels)
    verify: Set-Cookie: SameSite=Lax|None on the login
    falsifier: SameSite=Strict -> the browser blocks the cookie

C4: the channel carries victim-data or accepts a privileged action
    verify: {"action":"me"/"history"/"read"} -> the victim's data
    falsifier: a drop/ok/no-data -> no exploitable channel
```

### The unauth preconditions

```text
U1: a 101 with no credentials
    verify: no-cookie --message '{}' -> 101
U2: a frame produces a data/action reply
    verify: {"action":"x"} -> a data reply
    falsifier: a drop-all -> a closed channel (a gap)
```

### The token-in-URL preconditions

```text
T1: the ws URL carries ?token=/?jwt=/?key=/?auth=/?session=/?api_key=
    verify: grep -riE 'wss?://[^"'\'']*\?' /tmp/bundle
T2: the credential is sensitive — a session/JWT/key, not a public id
    verify: the token is a credential
    falsifier: a public/anon id — no leak
```

## The message-side preconditions

### The object-IDOR preconditions

```text
I1: a frame field names an object — id/doc/object/room/channel/user_id/
    account/org/tenant/conversation/item/record
    verify: the bundle names an id-field
I2: the id-space covers other principals' objects — enumerable or known
    verify: the own-id baseline -> the literal/alias shape
I3: no per-message ownership check — measured
    verify: a mutated id -> the other-object reply
    falsifier: forbidden/404 on EVERY real other's id
```

### The action-dispatch preconditions

```text
A1: a dispatch field — action/type/event/cmd/method/op/verb/kind/do/fn/
    handler/route/call/name
    verify: the bundle names the dispatch key
A2: a privileged action exists in the schema — admin/debug/internal/
    system/eval/exec/flag/config/broadcast/impersonate/grant/reset/dump/
    export/metrics/reload
    verify: the bundle names a privileged action
A3: no role check on the dispatch — measured
    verify: a privileged action -> a privileged reply/state
    falsifier: forbidden/unknown on EVERY privileged action
```

### The spoof preconditions

```text
S1: a frame carries an identity field — from/user_id/sender/user/
    principal/subject/actor/author
    verify: the bundle names an identity field
S2: the server trusts the frame's identity, not the handshake's
    verify: {"from":"<other>",...} -> acts as the other
    falsifier: the field ignored/overwritten on EVERY mutation
```

### The self-grant preconditions

```text
G1: a grant field — role/perm/perms/is_admin/debug/internal/scope/
    level/tier/admin/sudo/superuser/staff/moderator
    verify: the bundle names a grant field
G2: the frame binds the grant — the role/perm changes the context
    verify: {"action":"x","role":"admin"} -> the grant accepted
    falsifier: ignored/forbidden on EVERY grant field
```

### The injection preconditions

```text
J1: a field reaches a sink — q/filter/file/path/url/data/obj/xml/host/
    cmd/search/where/order/name/text/tpl/msg/input/value/template/
    content/body/message
    verify: the field is consumed by a query/template/path/cmd/deser/fetch
J2: the field is not escaped/validated at the frame layer
    verify: a marker payload -> the eval/read
J3: the payload class is confirmed by its own oracle — the arithmetic/
    the timing/the file/the rows/the deserialization-output
    verify: the payload-class's measured oracle
    falsifier: the payload echoed RAW + the class-oracle fails
```

### The subscription preconditions

```text
B1: a subscription/join/watch/listen/follow field — subscribe/room/
    channel/topic/destination/namespace
    verify: the bundle names a membership field
B2: a restricted channel exists — internal/admin/secret/<other-user>/
    a privileged namespace
    verify: the bundle/schema names a restricted channel
B3: no membership check — measured
    verify: a subscribe-to-restricted -> the pushed feed
    falsifier: forbidden on EVERY restricted channel
```

### The resumption preconditions

```text
R1: a resume field — session_id/resume/reconnect/seq/offset/lastEventId
    verify: the bundle names a resume field
R2: a prior/other context exists — an old session_id/another's session
    verify: a known old/other session_id
R3: the resumption does not re-auth — measured
    verify: session_id:<other> -> the resumed foreign context
    falsifier: forbidden/re-auth on EVERY resumption
```

## The tools preconditions

```text
T1: ws_probe.py present — python3 tools/web/ws_probe.py --selftest
T2: proto_decode.py present — python3 tools/proto_decode.py --selftest
T3: bundle_miner present — python3 tools/web/bundle_miner.py --help
T4: a ws client — ws_probe.py / websockets / a socket lib
```

## The budget preconditions

```text
B1: 5 probes / 15 min per mechanism class — the per-cell cap
B2: 25 probes / 45 min per challenge — the ceiling
B3: a uniform cell is closed — a measured dead end
B4: the escalation rungs on uniform-all — chain_match/reclassify/
    writeup_search/novel_plan/fanout_sweep/solver_handoff
```

## The precondition-record

`precondition: <the mechanism>: <the named precondition>: <the verify>`
— each precondition named + verified; a failed precondition is the
mechanism's falsifier.
