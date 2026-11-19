# Per falsifier — each falsifier, the kill it confirms

## The handshake falsifiers

| Falsifier | Kills |
|---|---|
| `403`/close on EVERY foreign `Origin` + every bypass | CSWSH |
| `401`/`403`/close on a no-credential `101` | unauth channel |
| a `101`+no-credential that drops every frame | unauth-data (a `gap`, not a finding) |
| `anonymous`/no-user reply on `Cookie:`/`Authorization:`/`?token=` | the cookie/bearer/token binding |
| `400`/close on every `Sec-WebSocket-Protocol` alt | the sub-protocol select |
| `SameSite=Strict` on the cookie | the browser-CSWSH (a defense, not a server gap) |

## The message falsifiers

| Falsifier | Kills |
|---|---|
| `{"error":"forbidden"}`/`"unauthorized"`/`403`/`1008` on EVERY `id`/`room`/`channel`/`user_id`/`tenant` mutation | the object-IDOR |
| `forbidden`/`unknown action` on EVERY privileged action | the action-dispatch |
| the `from`/`user_id`/`role` field ignored/overwritten on EVERY mutation | the identity-spoof |
| the `role`/`perm`/`is_admin`/`scope` field ignored/`forbidden` | the self-grant |
| the payload echoed RAW + the payload-class's oracle fails | the injection |
| `forbidden` on EVERY `subscribe`/`join`/`watch`/`listen`/`follow` | the membership/subscription-IDOR |
| a state-read that shows no change after a write-frame | the write-side gap |
| `forbidden`/`unknown` on every `session_id`/`resume`/`seq`/`lastEventId` | the resumption |

## The weak-falsifier — the re-probe that reopens

| A `uniform`-looking reply | The reopen |
|---|---|
| `{"error":"unknown action"}` | a guessed action — the bundle's real set |
| `{"error":"invalid field"}` | a guessed field — the bundle's names |
| `{"error":"not found"}` on a guessed id | a KNOWN other's id |
| `{"error":"malformed"}`/`"bad request"` | the wrong framing — the real envelope |
| silence/drop | a state-change check / a different field |
| `500`/crash | a parser/branch differential |
| `forbidden` on `id:"FAKE"` only | a `uniform` ONLY if EVERY real other's id too |

## The per-falsifier discipline

- a falsifier is a MEASURED uniform — the verbatim rejection
- a `weak-negative` is NOT a falsifier — it names the re-probe
- a `gap`/drop is NOT a falsifier — it is unmeasured
- a falsifier needs the REAL rejection on the REAL object/action — not
  a guessed-name `unknown`

## The falsifier-record

`falsifier: <cell>: <the verbatim uniform reply> -> the cell is closed`
— a falsifier is the measured proof the check holds; a weak-negative is
the measured proof the probe was wrong, not the check.
