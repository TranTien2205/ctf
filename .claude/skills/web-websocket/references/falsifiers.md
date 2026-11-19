# Falsifiers — the kill-map, the measured dead ends

## The handshake falsifiers

| The check | A `uniform` rejection kills | The verbatim |
|---|---|---|
| foreign `Origin` | CSWSH | `403`/close on EVERY foreign + bypass |
| cookie/bearer/token binding | the bound-channel cells | `anonymous`/no-identity on the credential |
| no-auth open | the unauth channel | `401`/`403`/close on no-credential |
| `?token=`/`?jwt=` | — | still a URL-leak finding, not a channel-cell |
| `Sec-WebSocket-Protocol: <alt>` | the alt-protocol | `400`/close on every alt |
| first-frame auth | the frame-auth channel | `forbidden`/`401` on the auth-frame |

## The message falsifiers

| The check | A `uniform` rejection kills | The verbatim |
|---|---|---|
| `id`/`doc`/`object`/`room`/`channel`/`user_id`/`account`/`org`/`tenant` mutation | the object-IDOR | `forbidden`/`404`/`401`/`403` on EVERY real other's id |
| `join`/`subscribe`/`watch`/`listen`/`follow` to a restricted channel | the membership/subscription-IDOR | `forbidden`/`403`/`1008` on EVERY restricted |
| `admin`/`debug`/`internal`/`system`/`eval`/`exec`/`flag`/`config`/`broadcast`/`impersonate`/`grant`/`reset`/`dump`/`export`/`metrics`/`reload`/`su`/`login_as` action | the action-dispatch | `forbidden`/`unknown` on EVERY privileged action |
| `role`/`perm`/`is_admin`/`scope`/`level`/`debug`/`internal`/`admin`/`sudo`/`superuser`/`staff`/`moderator` field | the self-grant | ignored/`forbidden` on EVERY grant field |
| `from`/`user_id`/`sender`/`user`/`author`/`actor`/`principal`/`subject`/`as_user`/`impersonate` field | the identity-spoof | ignored/overwritten/`forbidden` on EVERY identity field |
| `q`/`filter`/`file`/`path`/`url`/`data`/`obj`/`xml`/`host`/`cmd`/`name`/`text`/`tpl`/`msg`/`input`/`value`/`template`/`content`/`body`/`order`/`sort`/`where`/`select`/`match`/`criteria`/`expression`/`clause` | the injection | the payload RAW + the class-oracle fails |
| `transfer`/`set`/`update`/`grant`/`reset`/`delete`/`create`/`insert`/`broadcast`/`announce`/`emit-all`/`send_all`/`config` | the write-side | `forbidden`/`unknown` on EVERY write + a second read shows no change |
| `subscribe`/`topic`/`channel`/`destination`/`namespace`/`#`/`+`/`feed`/`event_name` | the subscription-IDOR | `forbidden`/`403`/`1008` on EVERY restricted feed |
| `session_id`/`resume`/`reconnect`/`seq`/`offset`/`lastEventId`/`token`/`auth`/`jwt`/`session`/`key`/`api_key`/`secret`/`credential` | the resumption | `forbidden`/`re-auth`/`unknown` on EVERY resumption |

## The weak-falsifier — the re-probe that reopens

| A `uniform`-looking reply | The reopen |
|---|---|
| `{"error":"unknown action"}` | a guessed action — the bundle's real set |
| `{"error":"invalid action"}`/`"invalid field"` | a guessed name — the bundle's real names |
| `{"error":"not found"}`/`"invalid"` on a guessed id | a KNOWN other's id |
| `{"error":"malformed"}`/`"bad request"`/`"invalid request"` | the wrong envelope — the real send-shape |
| `{"error":"no such object"}`/`"missing field"` | a guessed id/schema — the real schema |
| `{"error":"unrecognized"}` | a guessed name — the real set |
| silence/drop | a gap — a state-change check / a different field |
| `500`/crash | a candidate — a parser/branch differential |
| `pong`/`ok`/echo/`{"status":"ok"}` | surface — not a `uniform` |

## The falsifier vocabulary — the real-rejection shapes

```text
the real rejections:
  {"error":"forbidden"}       {"error":"unauthorized"}
  {"error":"access denied"}   {"error":"not permitted"}
  {"error":"insufficient permission"}
  {"status":403}              {"status":401}
  a close-frame 1008          a 403/401 HTTP on the upgrade
NOT real rejections:
  {"error":"unknown action"}  {"error":"invalid field"}
  {"error":"not found"}       {"error":"malformed"}
  silence/drop                a 500/crash
  pong/ok/echo                a 101
```

## The falsifier-record

`falsifier: <cell>: <the verbatim uniform reply> -> the cell is closed`
— a falsifier is the measured proof the check holds; a weak-negative is
the measured proof the probe was wrong, not the check.
