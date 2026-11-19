# Class boundary — this class vs the confusables

## `web-websocket` vs `web-csrf`

| The observed | The class |
|---|---|
| a forged one-shot request, no read-back | `web-csrf` |
| a forged CHANNEL-OPEN + a bidirectional read/write | `web-websocket` (CSWSH) |

CSWSH is strictly stronger — the socket maintains the session and reads
the replies. The mechanism is the same (cookie on a forged open); the
channel capability is the distinction.

## `web-websocket` vs `web-idor`

| The observed | The class |
|---|---|
| `GET /api/objects/{other-id}` returns the object | `web-idor` |
| `{"action":"read","id":"<other>"}` returns it over WS | `web-websocket` (message-IDOR) |

The same bug, different transport — the WS authz is a separate, weaker
implementation. A `403` on HTTP does NOT close the WS cell.

## `web-websocket` vs `web-auth-session`

| The observed | The class |
|---|---|
| a forgeable/mis-issued JWT/session/token | `web-auth-session` |
| the ws handshake's `?token=`/cookie-binding | `web-websocket` |
| the token-in-URL leak itself | `web-auth-session`/`web-info-disclosure` |

The channel class owns the binding/channel questions; the token's
lifecycle/forge is `web-auth-session`'s.

## `web-websocket` vs the injection classes

| The observed | The class |
|---|---|
| a `{"q":"<sqli>"}` frame returning injected rows | `web-sqli` |
| a `{"id":"<other>"}` frame returning another's object | `web-websocket` |

The FRAME is the carrier — the payload's class owns the exploit. The
message-IDOR (a cross-principal read) is this class's; the injected
extraction is the payload's.

## `web-websocket` vs `web-mass-assignment`

| The observed | The class |
|---|---|
| a `role`/`perm`/`is_admin` bound on an HTTP `PUT` | `web-mass-assignment` |
| a `{"action":"x","role":"admin"}` the frame binds | `web-websocket` (a self-grant) |

## `web-websocket` vs `web-graphql`

| The observed | The class |
|---|---|
| a `subscription{...}`/`query` over `graphql-ws` | `web-graphql` over WS |
| the channel/authz questions about it | `web-websocket` |

A `graphql-ws` subscription-IDOR is both — the transport (WS) is this
class, the query abuse is `web-graphql`.

## `web-websocket` vs `web-deserialization`

A serialized-object frame → `web-deserialization`; the channel carrying
it is `web-websocket`.

## The composite rule

A chain uses both — `web-websocket` opens the channel and produces the
cross-boundary frame; the payload/neighbor class owns the downstream
exploit. Record each as its own class; the card names the flag-closing
class with `web-websocket` as the channel.
