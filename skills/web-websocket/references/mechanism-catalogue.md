# Mechanism catalogue — the complete indexed list of named gaps

## Category A — handshake-side gaps

### A1. foreign-Origin accept (CSWSH-leg-1)
- the check: `--origin <foreign>` -> `101`
- the precondition: a cookie-binding + SameSite-travels + a data channel
- the finding: CSWSH (the four-leg chain) or the Origin-gap (the subset)
- the route: `web-websocket`/`web-csrf`

### A2. unauth channel (the open socket)
- the check: no-credential `101` + a data/action reply
- the finding: an unauth channel — no credentials needed
- the route: `web-websocket`/`web-info-disclosure`

### A3. credential-in-URL (the token leak)
- the check: `?token=`/`?jwt=`/`?key=`/`?auth=`/`?session=`/`?api_key=`
- the finding: a credential in the URI — logs/history/referer
- the route: `web-auth-session`/`web-info-disclosure`

### A4. auth-binding (the cookie/bearer binding)
- the check: `Cookie:`/`Authorization:`/`?token=`/`X-<custom>` -> the
  bound identity
- the finding: the binding mechanism — CSWSH-able if the cookie binds
- the route: `web-websocket`/`web-auth-session`

### A5. sub-protocol select (the alt-protocol)
- the check: `Sec-WebSocket-Protocol: <alt>` -> accepted
- the finding: an alternate protocol the server speaks
- the route: `web-websocket`/`web-parser-differential`

### A6. first-frame auth (the post-upgrade token)
- the check: `{"type":"auth"}`/`40{"token"}`/`connection_init`/`CONNECT`
- the finding: the auth is a frame — probe the token's forge/stale/null
- the route: `web-websocket`/`web-auth-session`

## Category B — message-side gaps

### B1. object-IDOR (the per-frame read gap)
- the check: `{"action":"read","id":"<other>"}` + another's object
- the finding: a cross-principal object read
- the route: `web-idor`

### B2. membership/subscription-IDOR
- the check: `{"action":"join"/"subscribe"/"watch","<other-channel>"}` /
  `SUBSCRIBE`/`{"type":"subscribe"}`
- the finding: a cross-principal feed read
- the route: `web-idor`

### B3. action-dispatch gap (the privileged action)
- the check: `{"action":"<privileged>"}` -> a privileged reply/state
- the finding: a privileged handler with no role check
- the route: `web-auth-session`/`web-logic-flaw`

### B4. role-self-grant (the privileged field)
- the check: `{"action":"x","role":"admin"}`/`"perm"`/`"is_admin"`/
  `"scope"`/`"debug"`/`"internal"`
- the finding: a frame field binds a privileged property
- the route: `web-mass-assignment`/`web-auth-session`

### B5. identity-spoof (the claimed user)
- the check: `{"from":"<other>",...}`/`{"user_id":"<other>"}`/`{"sender"}`
- the finding: the frame claims an identity the handshake did not set
- the route: `web-mass-assignment`/`web-auth-session`

### B6. injection-in-frame (the sink-reaching field)
- the check: `{"<field>":"<payload>"}` -> the payload-class oracle
- the finding: a field reaches a sink (query/template/path/cmd/deser/
  fetch/prototype)
- the route: the payload's class

### B7. write-side gap (the state-changing frame)
- the check: `{"action":"transfer"/"set"/"broadcast"/"delete"/"create"}`
- the finding: a state-change the write-frame caused
- the route: `web-logic-flaw`/the state class

## Category C — protocol/session gaps

### C1. subscription-IDOR (another's feed)
- the check: `{"action":"subscribe","channel":"<other>"}`/`SUBSCRIBE
  /user/<other>`/`{"type":"subscribe",<query>}`
- the route: `web-idor`

### C2. namespace-membership (the privileged namespace)
- the check: `/<ns>`/`{"action":"join","room":"<x>"}`/`{"action":
  "subscribe","channel":"<x>"}`/`SUBSCRIBE destination:/<x>`
- the route: `web-idor`/`web-auth-session`

### C3. session-resumption (the stale-context replay)
- the check: `session_id`/`resume`/`reconnect`/`seq`/`offset`/
  `lastEventId` -> a resumed context
- the route: `web-websocket`/`web-auth-session`

### C4. concurrent-socket race
- the check: two sockets, one account, an overlapping state op
- the route: `web-race-condition`

### C5. fragment-split inject
- the check: a `fin=0` continuation frame splitting a payload
- the route: `web-parser-differential`

### C6. compression bypass
- the check: a `permessage-deflate` compressed frame
- the route: `web-parser-differential`

### C7. transport-switch differential
- the check: the same app on raw-WS vs SockJS vs Socket.IO — a check
  absent on one transport
- the route: `web-parser-differential`

### C8. graphql-over-WS
- the check: `{"type":"subscribe",<query>}` — the whole web-graphql set
- the route: `web-graphql`

## The catalogue discipline

Every named gap has: the check (the probe), the finding (the oracle
reply), the route (the flag-closing class). The catalogue is the
mechanism inventory — the coverage matrix is its `× endpoint` product.
