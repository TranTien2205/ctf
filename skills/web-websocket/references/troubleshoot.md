# Troubleshoot — the failure modes, the fix

## The socket will not open

| Symptom | Cause | Fix |
|---|---|---|
| `400`/`426` | wrong `Upgrade` headers | the full `Connection:Upgrade`/`Upgrade:websocket`/`Sec-WebSocket-Version:13`/`Sec-WebSocket-Key:` set |
| `404` | wrong path | the bundle's real path — `/ws` vs `/api/ws` vs `/socket.io/` |
| `301`/`302` | a redirect to login | HTTP-auth first — `Cookie:`/`Authorization:` |
| `401`/`403` | the upgrade is authed | the credential — `Cookie`/`Authorization`/`?token=` |
| `426`/`Upgrade Required` | the endpoint is NOT ws | the real ws path — the bundle names it |
| TLS error | a cert/protocol | `wss://` vs `ws://`; the probe's `--insecure` |

## The socket opens but drops every frame

| Symptom | Cause | Fix |
|---|---|---|
| silence after `101` | the auth is a first-frame `{"token"}`/`40{"token"}`/`connection_init` | send the auth frame first |
| silence | a `subscribe`-only channel | no action surface — the membership is the check |
| silence | the envelope is wrong | `42[...]`/`a[...]`/STOMP — the real send-shape |
| `400`/`malformed`/`bad request` | a framing/schema error | the bundle's exact send-shape |
| `close 1008` | a policy violation | the action/field violated policy — the rejection IS data |

## The reply is not readable

| Symptom | Cause | Fix |
|---|---|---|
| `\x0a\x05...` binary | protobuf | `proto_decode.py frame.bin` |
| `a["{...}"]` | SockJS wrapper | unwrap the array, parse the inner string |
| `42["x",{...}]` | Socket.IO | strip `42`, parse `["x",{...}]` |
| a serialized blob | a `web-deserialization` object | the deserializer |
| compressed | `permessage-deflate` | inflate the frame |
| `MESSAGE\n...` | STOMP | the STOMP frame's body |

## The action/field returns `unknown`

| Symptom | Cause | Fix |
|---|---|---|
| `unknown action` | a guessed action name | the bundle's real `action`/`type`/`event` set |
| `unknown action` | the dispatch field is wrong | `action` vs `type` vs `event` vs `cmd` — the bundle's key |
| `invalid field` | a guessed field name | the bundle's field names |
| `malformed` | the wrong envelope | the real send-shape — `42[...]`/`a[...]`/STOMP |

## The IDOR returns `not found`

| Symptom | Cause | Fix |
|---|---|---|
| `not found` on `id:"victim"` | the id-space is uuid/non-sequential | a KNOWN other's id — the bundle/your own object |
| `not found` | the field is wrong | `id` vs `user_id` vs `doc` — the bundle's name |
| `404`/empty | the object does not exist | an enumerable id — `1`/`2`/`admin`/`me`/`self`/`current`/`0`/`-1` |

## The CSWSH reads `403`

| Symptom | Cause | Fix |
|---|---|---|
| `403` on `evil.example` | the Origin check works | the bypass set — `null`/`file:`/`*.target`/`target.evil`/no-`Origin` |
| `403` on ALL origins | an allowlist | no CSWSH — `uniform`: origin |
| `101` but no victim data | the cookie did not travel | `SameSite`/`Lax`-context — the browser defense |

## The timing/reconnect issues

| Symptom | Cause | Fix |
|---|---|---|
| the socket closes fast | a `ping`/`pong` keepalive | answer `2`/`9` ping with `3`/`pong` |
| a reconnect reverts auth | a session-resumption gap | the reconnect re-auth — a finding |
| a slow reply | a queue/async | the reply is another frame — read the stream |

## The tool issues

| Symptom | Cause | Fix |
|---|---|---|
| `ws_probe` errors | the URL/flag shape | `python3 tools/web/ws_probe.py --selftest` |
| `proto_decode` fails | not protobuf | a serialized/blob/compressed frame |
| the proxy drops frames | a WS-unaware proxy | a direct socket / `ws_probe` |

## The diagnostic record

`diag: <symptom> -> <cause> -> <the fix>` — each block a named row; the
fix is the named command/field, not a guess.
