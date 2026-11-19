# Per-message-field — every frame field's attack surface

## The identity/ownership fields — the IDOR surface

| Field | The probe | The gap |
|---|---|---|
| `id`/`object`/`doc`/`item` | `{"action":"read","id":"victim"}` | another's object |
| `room`/`channel`/`conversation`/`topic` | `{"action":"join","room":"admin"}` | a restricted channel |
| `user_id`/`user`/`uid`/`owner` | `{"action":"get","user_id":2}` | another's record |
| `to`/`target`/`recipient` | `{"action":"send","to":"admin"}` | a write-routing gap |
| `account`/`org`/`team`/`tenant` | `{"action":"list","org":"other"}` | a tenant-crossing |

## The dispatch fields — the privilege surface

| Field | The probe | The gap |
|---|---|---|
| `action`/`type`/`event`/`cmd`/`method` | `{"action":"admin"}` | a privileged action |
| `role`/`perm`/`is_admin`/`debug`/`internal` | `{"role":"admin"}` | a self-granted role |
| `scope`/`level`/`access` | `{"scope":"admin"}` | a self-granted scope |
| `admin`/`internal`/`system` flag | `{"internal":true}` | an internal flag |

## The injection fields — the payload surface

| Field | The payload class |
|---|---|
| `q`/`search`/`filter`/`where`/`query` | `web-sqli`/`web-nosqli` |
| `id`/`sort`/`order`/`limit`/`offset` | `web-sqli` |
| `name`/`text`/`msg`/`subject`/`tpl`/`render` | `web-ssti` |
| `host`/`file`/`cmd`/`input`/`domain`/`url` | `web-command-injection`/`web-ssrf` |
| `file`/`path`/`doc`/`template`/`name` | `file-read-primitives` |
| `xml`/`data`/`import` | `web-xxe`/`web-deserialization` |
| `obj`/`config`/`merge`/`__proto__` | `web-prototype-pollution` |
| `name`/`filter`/`xpath`/`ldap` | `web-nosqli`/LDAP/XPath |

## The protocol-carrier fields

| Field | The gap |
|---|---|
| `connection_init.payload.authToken` | the graphql-ws auth |
| `40{token}` Socket.IO connect | the socket.io auth |
| `destination:` STOMP header | the routing IDOR |
| `Sec-WebSocket-Protocol` | the protocol selection |

## The field-name hunt

The bundle names the live fields — `web-source-map`/`bundle_miner` grep
`id|room|channel|user|action|type|event|to|target|file|q|search`. A
guessed field is a weak probe; the bundle's field is the live one.

## The per-field rule

One field per connection, mutated against a same-session baseline. The
reply (another's data / a state-change / an evaluation) is the verdict;
a uniform `forbidden`/`unknown`/`raw` is the recorded negative.
