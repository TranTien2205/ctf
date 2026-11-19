# Per vector — each vector, its lead, its route

## The `101`-foreign-Origin vector

- the lead: a `101` on a foreign `Origin`
- the route: CSWSH → verify cookie-binding + SameSite + data-channel
- the class: `web-websocket`/`web-csrf`-adjacent

## The `101`-no-auth vector

- the lead: a `101` with no credentials
- the route: an unauth channel → does it carry data?
- the class: `web-websocket` (unauth-channel)

## The `?token=` vector

- the lead: a credential on the ws URL
- the route: `web-auth-session` (the token's forge/leak) +
  `web-info-disclosure` (the URL leak)
- the class: a composite — the channel cell + the token cell

## The `{"action":"read","id"}` vector

- the lead: a field naming an object
- the route: message-IDOR → `web-idor`
- the class: `web-websocket` → `web-idor`

## The `{"action":"x"}` dispatch vector

- the lead: a `action`/`type`/`event`/`cmd` field
- the route: action-dispatch → a privileged action
- the class: `web-websocket` (dispatch gap) → `web-auth-session`/`web-logic-flaw`

## The `{"from"/"role"/"user_id"}` vector

- the lead: an identity/role field
- the route: a spoof/self-grant → `web-mass-assignment`/`web-auth-session`
- the class: `web-websocket` (spoof) → `web-mass-assignment`

## The `{"q"/"filter"/"file"/"xml"/"data"}` vector

- the lead: a query/file/data field
- the route: the injection → the payload class
- the class: `web-websocket` (the carrier) → `web-sqli`/`web-ssti`/etc.

## The `SUBSCRIBE`/`subscribe`/`join`/`watch` vector

- the lead: a subscription/join field
- the route: a subscription-IDOR → another's feed
- the class: `web-websocket` → `web-idor`

## The binary/protobuf vector

- the lead: a binary frame
- the route: `proto_decode` → a `field N` carrying the flag, OR a
  `web-deserialization` object
- the class: `web-websocket` → `web-deserialization`/`proto-decode`

## The namespace/room vector

- the lead: a `/<ns>`/`room`/`channel`/`topic` route
- the route: a namespace/room-membership IDOR
- the class: `web-websocket` → `web-idor`

## The vector-record

`vector: <the lead>: <the route>: <the flag-closing class>` — the lead
maps to the route; the coverage matrix is per-vector.
