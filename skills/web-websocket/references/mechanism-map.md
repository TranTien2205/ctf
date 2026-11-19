# Mechanism map — the mechanism → the check → the file

## The map

| Mechanism | The check | The file |
|---|---|---|
| foreign-Origin | `--origin <foreign>` -> `101`/`403` | `cswsh.md`/`handshake-side-deep.md` |
| auth-binding | `Cookie:`/`Authorization:`/`?token=` | `handshake-side-deep.md` |
| unauth-open | no-credential `101`+data | `handshake-side-deep.md` |
| token-in-URL | `?token=`/`?jwt=`/`?key=` on the URL | `handshake-side-deep.md` |
| sub-protocol | `Sec-WebSocket-Protocol:<alt>` | `handshake-side-deep.md`/`per-transport-deep.md` |
| first-frame auth | `{"type":"auth"}`/`40{"token"}`/`connection_init` | `handshake-side-deep.md` |
| object-IDOR | `{"action":"read","id":"<other>"}` | `message-idor-deep.md` |
| membership-IDOR | `{"action":"join"/"subscribe","<other-channel>"}` | `message-idor-deep.md` |
| action-dispatch | `{"action":"<privileged>"}` | `action-dispatch-deep.md` |
| role-self-grant | `{"action":"x","role":"admin"}` | `action-dispatch-deep.md` |
| identity-spoof | `{"from":"<other>",...}` | `message-side-deep.md` |
| injection | `{"<field>":"<payload>"}` | `injection-in-frames-deep.md` |
| write-side | `{"action":"transfer"/"set"/"broadcast"}` | `message-side-deep.md` |
| subscription-IDOR | `{"action":"subscribe","<other-feed>"}`/`SUBSCRIBE` | `per-transport-deep.md` |
| namespace-membership | `/<ns>`/`room`/`channel`/`topic` | `per-transport-deep.md` |
| session-resumption | `session_id`/`resume`/`reconnect`/`seq`/`lastEventId` | `edge-cases-deep.md` |
| concurrent-race | two sockets, one account | `edge-cases-deep.md` |
| fragment-split | `fin=0` continuation | `edge-cases-deep.md` |
| compression-bypass | `permessage-deflate` | `edge-cases-deep.md` |
| graphql-over-WS | `{"type":"subscribe",...}` | `per-transport-deep.md`/`web-graphql` |
| transport-switch | raw-WS vs SockJS vs Socket.IO on one host | `per-transport-deep.md` |

## The mechanism-to-cell map

| Mechanism | The coverage-matrix cell |
|---|---|
| foreign-Origin | `origin` |
| auth-binding | `binding` |
| unauth-open | `unauth` |
| token-in-URL | `token` |
| sub-protocol | `subproto` |
| object-IDOR | `idor` |
| membership-IDOR | `idor` |
| action-dispatch | `action` |
| role-self-grant | `action` |
| identity-spoof | `spoof` |
| injection | `inject` |
| subscription-IDOR | `subscribe` |
| session-resumption | `resume` |
| the rest | the `edge` cells |

## The mechanism-to-skill map — the flag-closing class

| Mechanism | The flag-closing skill |
|---|---|
| CSWSH | `web-websocket`/`web-csrf` |
| unauth | `web-websocket`/`web-info-disclosure` |
| IDOR/subscription | `web-idor` |
| dispatch | `web-auth-session`/`web-logic-flaw` |
| self-grant/spoof | `web-mass-assignment`/`web-auth-session` |
| inject | the payload class |
| token-URL | `web-auth-session`/`web-info-disclosure` |
| graphql-WS | `web-graphql` |
| resume | `web-websocket`/`web-auth-session` |

## The map-discipline

The map is the index — each mechanism names its check + its file + its
cell + its route. An unmeasured mechanism is a pending cell; the map
says which check closes it.
