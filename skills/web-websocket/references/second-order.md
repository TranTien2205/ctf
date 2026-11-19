# Second-order — the follow-on gaps the first finding opens

## The CSWSH's second-order

- the victim's socket opens → the victim's OTHER ws channels are
  reachable too (the same cookie)
- the victim's live data → a message-IDOR on the victim's socket reads
  ANY object the victim could reach
- a cross-client `broadcast` → the attacker page INJECTS into the
  victim's socket (a client-side write)

## The unauth-channel's second-order

- the unauth data → a field that leaks another's session/token
- the unauth action → a privileged action reachable without auth
- the unauth read → a dump of the whole object-space

## The message-IDOR's second-order

- the other-object's fields → a `flag`/`secret`/`key`/`password` field
- the other-object's `id` → the WHOLE id-space sweeps
- the read-IDOR's twin → the write-IDOR (update/delete/transfer)

## The action-dispatch's second-order

- the privileged action's reply → a `flag`/`users`/`config` dump
- the `eval`/`exec` action → a full RCE
- the `config`/`set` action → a config overwrite → a self-privilege

## The injection's second-order — the payload's chain

- the SQLi's rows → the `flag`/`password`/`session` columns → a session
- the SSTI's eval → `{{config.FLAG}}`/`{{self.__init__.__globals__}}`
- the LFI's file → the `/flag`/the source/the config
- the CMDi's output → `cat /flag`
- the deserialization's object → a gadget chain → RCE
- the SSRF's fetch → the internal `169.254.169.254`/`internal/`/`file://`
- the pollution's bound property → a privileged gate's `isAdmin`/`role`

## The subscription-IDOR's second-order

- the other-feed's pushed frames → the flag/secret riding the feed
- the wildcard `#`/`+` → the WHOLE topic-space
- the `lastEventId`/history → the feed's full backlog

## The token-in-URL's second-order

- the URL's `?token=`/`?jwt=` → `web-auth-session`'s forge —
  `alg:none`/weak-key/`kid`-inject/`jku`/`x5u`
- the stale `?token=`/`?session=` → a non-rotated session
- the `?key=`/`?api_key=` → a service/api key

## The resumption's second-order

- a `session_id`/`resume`/`reconnect` → the old session's context →
  the old user's privileged data
- a `lastEventId`/`seq`/`offset` → the feed's backlog → the flag

## The composite second-order

```text
the first finding (a read) -> the field it leaks (a token/key)
  -> web-auth-session (forge) -> a privileged context
  -> the privileged action -> the flag
```

The first finding is the entry; the second-order is the depth — a read
leaks a credential, the credential's forge opens the privileged action,
the action closes the flag.

## The second-order record

`second: <the first finding> -> <the leaked field/capability> -> <the
follow-on class> -> <the flag>` — the chain is the card's `chain[]`.
