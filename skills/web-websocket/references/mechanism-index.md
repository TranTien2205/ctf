# Mechanism index — every named gap, mapped

## The handshake-side mechanisms

| Mechanism | The check | The deep file |
|---|---|---|
| foreign-Origin accept | `--origin <foreign>` -> `101`? | `cswsh.md`/`handshake-side-deep.md` |
| auth-binding | `Cookie`/`Authorization`/`?token=` binds? | `handshake-side-deep.md` |
| unauth-open | a `101`+data with no credentials | `handshake-side-deep.md` |
| token-in-URL | a credential on the ws URL | `handshake-side-deep.md` |
| sub-protocol select | a `Sec-WebSocket-Protocol` alt | `handshake-side-deep.md` |
| sub-protocol differential | an alt parser, weaker validators | `per-transport-deep.md` |

## The message-side mechanisms

| Mechanism | The field | The deep file |
|---|---|---|
| object-IDOR | `id`/`doc`/`object`/`room`/`channel`/`user_id`/`tenant` | `message-idor-deep.md` |
| membership-IDOR | `join`/`subscribe`/`watch`/`listen`/`follow` | `message-idor-deep.md` |
| action-dispatch | `action`/`type`/`event`/`cmd`/`method`/`op` | `action-dispatch-deep.md` |
| role-self-grant | `role`/`perm`/`is_admin`/`debug`/`internal`/`scope` | `action-dispatch-deep.md` |
| identity-spoof | `from`/`user_id`/`sender`/`user`/`role` | `message-side-deep.md` |
| injection | `q`/`filter`/`file`/`xml`/`data`/`cmd`/`url`/`obj` | `injection-in-frames-deep.md` |
| write-side gap | `send`/`transfer`/`set`/`broadcast`/`delete` | `message-side-deep.md` |
| subscription-IDOR | `subscribe`/`topic`/`channel`/`destination` | `per-transport-deep.md` |

## The session/protocol mechanisms

| Mechanism | The field | The deep file |
|---|---|---|
| auth-in-first-frame | `{"type":"auth","token"}`/`connection_init`/`40{"token"}` | `handshake-side-deep.md` |
| session-resumption | `resume`/`session_id`/`reconnect` | `edge-cases-deep.md` |
| history/offset read | `seq`/`offset`/`lastEventId`/`history` | `message-idor-deep.md` |
| namespace-membership | `/<ns>`/`room`/`channel`/`topic` | `per-transport-deep.md` |
| concurrent-socket race | two sockets, one account | `edge-cases-deep.md` |
| fragment-split inject | `fin=0` continuation frames | `edge-cases-deep.md` |
| compression bypass | `permessage-deflate` | `edge-cases-deep.md` |

## The mechanism-to-skill map

| Mechanism | The flag-closing skill |
|---|---|
| CSWSH | `web-websocket`/`web-csrf` |
| unauth channel | `web-websocket`/`web-info-disclosure` |
| message-IDOR | `web-idor` |
| action-dispatch | `web-auth-session`/`web-logic-flaw` |
| role-self-grant | `web-mass-assignment` |
| identity-spoof | `web-mass-assignment`/`web-auth-session` |
| injection-in-frame | `web-sqli`/`web-ssti`/`web-command-injection`/`web-xxe`/`web-deserialization`/`web-nosqli`/`web-ssrf`/`file-read-primitives`/`web-prototype-pollution` |
| token-in-URL | `web-auth-session`/`web-info-disclosure` |
| subscription-IDOR | `web-idor` |
| graphql-over-WS | `web-graphql` |

## The index discipline

The index names every mechanism the corpus covers; a `uniform` cell in
the coverage matrix is a measured dead end; an unmeasured mechanism is a
pending cell — never assume a mechanism is closed until its probe ran.
