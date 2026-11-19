# Negative map — each negative, the cell it closes

## The handshake negatives

| The verbatim reply | The verdict | The cell |
|---|---|---|
| `403 Forbidden`/`close` on EVERY foreign-Origin + bypass | `uniform` | `origin` — CSWSH closed |
| `401`/`403` on a no-credential `101` | `uniform` | `unauth` — the channel needs auth |
| `{"user":"anonymous"}`/no-identity on `Cookie:`/`Bearer`/`?token=` | `uniform` | `binding` — the credential does not bind |
| `400`/close on EVERY `Sec-WebSocket-Protocol` alt | `uniform` | `subproto` — only the intended protocol |
| a `101`+no-credential that drops EVERY frame | `gap` | `unauth` — a closed channel, not a verdict |
| `SameSite=Strict` on the cookie | `browser-defense` | `cswsh` — the browser leg fails |

## The message negatives — the rejections

| The verbatim reply | The verdict | The cell |
|---|---|---|
| `{"error":"forbidden"}`/`"unauthorized"`/`403`/`1008` on EVERY `id`/`doc`/`room`/`channel`/`user_id`/`account`/`org`/`tenant` mutation | `uniform` | `idor` — the object-scope check holds |
| `forbidden`/`unknown` on EVERY `admin`/`debug`/`internal`/`system`/`eval`/`exec`/`flag`/`config`/`broadcast`/`impersonate`/`grant`/`reset`/`dump`/`export`/`metrics`/`reload` action | `uniform` | `action` — the dispatch checks role |
| the `from`/`user_id`/`sender`/`user`/`author` field ignored/overwritten on EVERY mutation | `uniform` | `spoof` — the handshake identity holds |
| the `role`/`perm`/`is_admin`/`scope`/`level`/`debug`/`internal`/`admin`/`sudo` field ignored/`forbidden` | `uniform` | `grant` — the grant is not bound |
| the payload echoed RAW + the class-oracle fails (no `49`/SLEEP/`id`/file/rows) | `uniform` | `inject` — the sink is escaped/absent |
| `forbidden` on EVERY `join`/`subscribe`/`watch`/`listen`/`follow` to a restricted channel | `uniform` | `membership` — the membership check holds |
| a second read shows NO change after EVERY write-frame | `uniform` | `write` — no write-side gap |
| `forbidden`/`unknown` on EVERY `session_id`/`resume`/`seq`/`offset`/`lastEventId` | `uniform` | `resume` — no resumption gap |
| `forbidden`/`unknown` on EVERY `subscribe`/`topic`/`destination`/`namespace`/`#`/`+` | `uniform` | `subscribe` — the subscription check holds |

## The weak-negative map — the re-probe that reopens

| The verbatim reply | The verdict | The re-probe |
|---|---|---|
| `{"error":"unknown action"}` | `weak-negative` | the bundle's REAL action set |
| `{"error":"invalid field"}` | `weak-negative` | the bundle's REAL field names |
| `{"error":"not found"}`/`"invalid"` on a guessed id | `weak-negative` | a KNOWN-other's id |
| `{"error":"malformed"}`/`"bad request"` | `weak-negative` | the correct ENVELOPE shape |
| `{"error":"unknown action"}` on `admin` | `weak-negative` | the bundle's real privileged names |
| `404`/empty on a guessed nonexistent id | `weak-negative` | a KNOWN other's id |
| silence/drop | `gap` | a state-change check / a different field |
| `500`/crash | `candidate` | a parser/branch differential |

## The gap map — the unresponsive cells

| The reply | The verdict | The next step |
|---|---|---|
| a `101` + a silent drop on EVERY frame | `gap` | the channel may process silently — a state-check |
| a `101` + a `pong`/`ok`/echo | `surface` | not a finding — the happy-path |
| a subscribe-only channel | `gap` | the membership is the check — no action surface |
| a reconnect that re-auths cleanly | `uniform` | `resume` — the resumption checks auth |

## The negative-discipline

- a `uniform` is a MEASURED dead end — the verbatim rejection
- a `weak-negative` is a re-probe — the schema was guessed
- a `gap` is unmeasured — not a verdict either way
- a `surface` reply is not a finding — and not a `uniform`
- record every cell — the negative is the budget redirect

## The negative-record

`negative: <cell>: <the verbatim reply> -> the verdict -> the cell's
state (closed | re-probe | unmeasured)` — a negative is a measured
reply, not an assumed one.
