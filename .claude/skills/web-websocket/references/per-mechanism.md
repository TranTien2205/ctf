# Per mechanism — each mechanism, the full check path

## Mechanism: foreign-Origin accept → CSWSH

```text
1. the Origin probe          -> a 101/403
2. the bypass set            -> null/file:///*.target/target.evil/no-Origin
3. the binding               -> a Cookie:/token- binding
4. the SameSite read         -> the cookie travels?
5. the data channel          -> a frame returns victim-data?
the verdict: all four legs -> CSWSH; a subset -> the weaker gap
```

## Mechanism: unauth channel

```text
1. a no-credential 101       -> the channel opens
2. a first-frame check       -> {"action":"x"} -> a reply or a drop?
3. a data probe              -> {"action":"dump"}/{"action":"read","id":"x"}
the verdict: a data reply -> unauth; a drop-all -> a closed channel
```

## Mechanism: token-in-URL

```text
1. grep the ws URL           -> ?token=/?jwt=/?key=/?auth=/?session=/?api_key=
2. the credential            -> the verbatim token on the URI
3. the forge check           -> web-auth-session's JWT/token attacks
the verdict: the credential in the URI -> a leak + the channel cell
```

## Mechanism: object-IDOR

```text
1. the control               -> {"action":"read","id":"me"} -> my object
2. the mutation              -> {"action":"read","id":"<other>"} -> ?
3. the id-space              -> sequential/username/uuid/me-alias
4. the object surface        -> id/doc/room/channel/user_id/account/org/
                              tenant/conversation/item/record/object
the verdict: another's object -> a message-IDOR
```

## Mechanism: membership/subscription-IDOR

```text
1. the membership field      -> join/subscribe/watch/listen/follow
2. the restricted channel    -> "admin"/"internal"/"secret"/<other-user>
3. the pushed frames         -> another's feed arrives
the verdict: a pushed other-feed -> a subscription-IDOR
```

## Mechanism: action-dispatch gap

```text
1. the dispatch field        -> action/type/event/cmd/method/op
2. the privileged names      -> admin/debug/internal/system/eval/exec/
                              flag/config/broadcast/impersonate/grant/
                              set_role/reset/dump/export/metrics/reload
3. a namespaced action       -> admin:x / internal:x / system.x / debug/x
the verdict: a privileged reply/state -> a dispatch gap
```

## Mechanism: role-self-grant

```text
1. the grant field           -> role/perm/is_admin/debug/internal/scope/
                              level/tier/admin/sudo
2. the mutation              -> {"action":"x","role":"admin"}
3. the nested variant        -> {"action":"x","user":{"role":"admin"}}
4. the pollution variant     -> {"action":"x","__proto__":{"role":"admin"}}
the verdict: the grant accepted -> a self-grant
```

## Mechanism: identity-spoof

```text
1. the identity field        -> from/user_id/sender/user/author
2. the mutation              -> {"from":"<other>",...} / {"user_id":<n>}
3. the action check          -> does the action act as the other?
the verdict: acts-as-other -> a spoof
```

## Mechanism: injection-in-frame

```text
1. the sink field            -> q/filter/file/path/url/data/obj/xml/host/
                              cmd/search/where/order
2. the payload               -> the payload-class's oracle payload
3. the eval/read             -> the 49/SLEEP-delay/rows/file/output
the verdict: the payload's oracle fires -> an injection -> the payload class
```

## Mechanism: write-side gap

```text
1. the write field           -> transfer/set/broadcast/delete/create/
                              update/config/send
2. the mutation              -> the write frame
3. the state-confirm         -> a second read shows the change
the verdict: a confirmed state-change -> a write-side gap
```

## Mechanism: subscription/backlog read

```text
1. the subscription field    -> subscribe/topic/channel/destination
2. the history field         -> seq/offset/lastEventId/history/from/to
3. the read                  -> another's feed / the backlog
the verdict: a pushed other-feed/backlog -> a subscription-IDOR
```

## Mechanism: session-resumption

```text
1. the resume field          -> session_id/resume/reconnect/seq/offset
2. the mutation              -> a stale/other session_id, a seq:-1
3. the resumed context       -> the old/other context's data
the verdict: a resumed foreign context -> a resumption gap
```

## Mechanism: graphql-over-WS

```text
1. the sub-protocol          -> graphql-transport-ws/graphql-ws
2. the auth frame            -> connection_init + payload.{authToken}
3. the subscription          -> {"type":"subscribe",<query>} -> a
                                subscription-IDOR + a field-leak + a mutation
the verdict: a graphql gap -> web-graphql
```

## Mechanism: binary/protobuf

```text
1. a binary frame            -> proto_decode.py frame.bin
2. the field-stream          -> a field N = the flag/secret/id
3. a field mutation          -> a binary mutated-field frame
the verdict: a numbered-field gap -> proto_decode + the field class
```

## The per-mechanism record

`mechanism: <the name>: <the check-path>: <the oracle>: <the route>` —
each mechanism's check-path + verdict + the flag-closing route.
