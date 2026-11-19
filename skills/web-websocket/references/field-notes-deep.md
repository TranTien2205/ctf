# Field notes (deep) — the per-endpoint learning record

## The per-endpoint record

```
endpoint:  wss://x/ws
framing:   <raw|socket.io|sockjs|stomp|graphql-ws|mqtt|protobuf>
auth:      <cookie|token|bearer|none> + <samesite>
schema:    <the action set> x <the field set>
cells:     <the oracle/uniform/weak-neg/gap matrix>
flag:      <the verbatim flag-bearing reply, if reached>
route:     <the flag-closing class>
notes:     <the trap the endpoint produced>
```

## The trap-notes — what this endpoint taught

- a `101`+foreign-`Origin` that was NOT CSWSH — the cookie was
  `SameSite=Strict` — record the four-leg requirement
- a `101`+no-cookie that dropped every frame — a `gap`, not a finding —
  record the closed-channel distinction
- a `{"action":"x"}` that returned `unknown action` — the action-name
  was guessed — record the weak-negative discipline
- a binary frame — `proto_decode` — record the binary transport
- a `Socket.IO` channel — the `42[...]` envelope — record the envelope-
  before-payload rule
- a `?token=` — the credential-in-URL — record the separate finding

## The field-name notes — the observed names

```
the dispatch key:   action / type / event / cmd / method / op
the object fields:  id / doc / room / channel / user_id / account /
                    org / tenant / conversation
the auth fields:    token / auth / jwt / session_id / resume /
                    lastEventId / seq / offset
the identity fields: from / user_id / sender / user / role / perm /
                    is_admin / scope
the sink fields:    q / filter / where / order / file / path / url /
                    data / obj / xml / host / cmd
the membership:     subscribe / join / watch / listen / follow /
                    destination / namespace / topic
```

## The reply-vocabulary notes — the observed replies

```
the oracle:         {"id":"<other>",...} / {"flag":...} / a pushed feed /
                    an eval / a state-change
the uniform:        {"error":"forbidden"} / {"error":"unauthorized"} /
                    403/401/1008 close
the weak-neg:       {"error":"unknown action"} / {"error":"invalid
                    field"} / {"error":"not found"} / {"error":"malformed"}
the gap:            silence/drop — the frame was ignored
the surface:        101 / pong / ok / echo / {"status":"ok"}
the differential:   500 / crash / a partial-frame
```

## The per-shape notes — the observed shapes

```
the chat:           room/dm/history/to/from/msg — IDOR+spoof+broadcast
the doc:            open/op/sync/version/content — doc-IDOR+op-inject
the dashboard:      stats/config/control/admin — dispatch+config
the trading:        order/balance/transfer/account — IDOR+transfer
the notif:          subscribe/topic/channel/user_id — subscription-IDOR
the graphql:        subscription/query/mutation — graphql-over-WS
the binary:         a field-stream — proto_decode + a field-IDOR
the mqtt:           topic/cmd/payload — a topic-IDOR + a control-cmd
```

## The route-notes — the flag-closing classes

```
a message-IDOR       -> web-idor
a dispatch gap       -> web-auth-session / web-logic-flaw / the flag
a self-grant/spoof   -> web-mass-assignment / web-auth-session
an injection         -> the payload's class
a CSWSH              -> web-websocket (the four-leg chain)
an unauth channel    -> web-websocket / web-info-disclosure
a token-in-URL       -> web-auth-session / web-info-disclosure
a subscription-IDOR  -> web-idor
a graphql-WS         -> web-graphql
a resume gap         -> web-websocket / web-auth-session
```

## The promotion note

`web-websocket` is a catalogue class — a confirmed local chain is the
FIRST verification — record the verbatim chain + file it via
`classify_solve.py`. Do NOT claim the corpus's techniques worked here
before a card proves them.
