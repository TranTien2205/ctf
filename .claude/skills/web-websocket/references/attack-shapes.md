# Attack shapes — the gap classes, each a template

## Shape 1: CSWSH — the cross-site channel hijack

```text
precondition: foreign-Origin accepted + cookie-binding + SameSite-travels
              + a data/action channel
the page:     a foreign-origin HTML that opens the socket as the victim
the frames:   read the victim's data / write the victim's actions
the proof:    the victim's data arrives on the attacker origin
```

## Shape 2: unauth channel — the open socket

```text
precondition: a 101 with no credentials + a data/action reply
the probe:    {"action":"dump"}/{"action":"read","id":"x"}/SUBSCRIBE
the proof:    the data/action reply verbatim
```

## Shape 3: message-IDOR — the per-frame object read

```text
precondition: a field names an object; no per-object scope check
the probe:    {"action":"read","id":"<other>"} / subscribe another's
              channel / open another's doc
the proof:    the other-object reply verbatim
```

## Shape 4: action-dispatch — the privileged action

```text
precondition: a dispatch field + a privileged action + no role check
the probe:    {"action":"admin"}/{"action":"eval"}/42["internal",{...}]
the proof:    the privileged reply / the confirmed state-change
```

## Shape 5: identity-spoof — the frame's claimed user

```text
precondition: the frame carries from/user_id/role; the server trusts it
the probe:    {"from":"victim",...} / {"role":"admin"}
the proof:    the action acts as the claimed identity
```

## Shape 6: injection-in-frame — the sink-reaching field

```text
precondition: a field reaches a query/template/path/cmd/deser/fetch
the probe:    {"q":"<sqli>"} / {"name":"{{7*7}}"} / {"file":"/flag"}
the proof:    the payload-class oracle (49/SLEEP/file/rows)
```

## Shape 7: token-in-URL — the URI credential

```text
precondition: a ?token=/?jwt=/?key=/?auth= on the ws URL
the proof:    the credential in the URI — the log/history leak
the route:    web-auth-session + web-info-disclosure
```

## Shape 8: subscription-IDOR — another's feed

```text
precondition: a subscribe/join/listen to a channel; no membership check
the probe:    SUBSCRIBE /user/<other> / {"action":"subscribe",
              "channel":"internal"} / {"type":"subscribe",<query>}
the proof:    the other-feed's pushed frames
```

## Shape 9: the namespace/room membership

```text
precondition: a /<ns>/room/topic route; a privileged namespace
the probe:    42/admin / {"action":"join","room":"admin"} /
              SUBSCRIBE destination:/admin
the proof:    the privileged-namespace frames
```

## Shape 10: the session-resumption replay

```text
precondition: a reconnect/resume/session_id; a stale-identity resumption
the probe:    reconnect with no credential -> does it resume the old
              identity? / a session_id replay
the proof:    the resumed context's privileged data/action
```

## The shape-record

`shape: <the-gap>: <the precondition>: <the probe>: <the proof>` — the
shape names the class of the gap; the proof is the verbatim reply.
