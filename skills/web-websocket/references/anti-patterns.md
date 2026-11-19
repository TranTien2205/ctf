# Anti-patterns — the things that look like findings but are not

## Anti-pattern: "the socket opened, therefore a bug"

A `101 Switching Protocols` is the handshake — the channel exists. The
finding is a frame the server sent that crosses a boundary — another's
object, a privileged action, an eval. A `101` + `pong`/`ok`/`echo` is
surface, not a finding.

## Anti-pattern: "a foreign Origin was accepted, therefore CSWSH"

A `101`+`Origin:evil` is leg-1 of 4 — without the cookie-binding +
the SameSite-travels + a data channel, it is the Origin-gap only.
The four-leg chain is CSWSH; a one-leg acceptance is not.

## Anti-pattern: "the frame replied ok, therefore the write landed"

`{"status":"ok"}`/`ok`/`true` is a control reply — it says the frame
was ACCEPTED, not that the write produced a state-change. Confirm by
a second read — `{"action":"balance"}`/the HTTP state — the change.

## Anti-pattern: "unknown action means the action is protected"

`{"error":"unknown action"}` means the action-NAME is wrong — the
dispatch could not route it. A `{"error":"forbidden"}`/`"unauthorized"`
on a KNOWN action is the real rejection — the role check that fires.
`unknown` is a weak-negative; `forbidden` is `uniform`.

## Anti-pattern: "the HTTP 403 means the WS is closed"

`GET /api/objects/x -> 403` closes the HTTP IDOR cell — the WS
`{"action":"read","id":"x"}` is a SEPARATE authz path, routinely weaker.
Measure the frame, not the HTTP twin.

## Anti-pattern: "a drop is a rejection"

A silent drop is a `gap` — the frame was ignored, not rejected. A
`forbidden`/`unauthorized`/`403` is a measured rejection. A drop is
unmeasured — the channel may process it internally.

## Anti-pattern: "the SameSite cookie means CSWSH is safe"

`SameSite=Strict` is a BROWSER defense — it stops the victim's BROWSER
from attaching the cookie. The server still accepts the foreign `Origin`
— a non-browser client or a `SameSite=Lax`/`None` context still fires.
The server-side gap remains.

## Anti-pattern: "the token-in-URL is the auth, so no CSWSH"

`?token=` is a credential-in-URL finding — SEPARATE from the channel's
authz. The channel may still carry an unauth `101` or a foreign-`Origin`
accept — the token's presence does not close the origin/unauth cells.

## Anti-pattern: "a raw JSON send worked, so the transport is raw"

A `{"action":"x"}` that gets `{"error":"malformed"}`/`"unknown"` — the
envelope is wrong, not the action. Send the `42["x",{...}]`/`a[...]`/
STOMP/`type:` shape — the envelope first, the action second.

## Anti-pattern: "the socket needs a token so it's authed"

A `{"type":"auth","token":null}`/`{"type":"auth","token":""}`/a forgeable
`?token=` — the auth-REQUIRED socket is not the same as an auth-ENFORCED
socket. Probe the token's validity/forge.

## Anti-pattern: "two payloads on one socket, the reply tells which"

The reply does NOT name the frame that caused it — the channel is
async. One field per connection, always.

## Anti-pattern: "a privileged reply on a guessed action is a fluke"

`{"action":"admin"} -> {"flag":...}` on a guessed action — it IS the
gap (the dispatch does not check role); the action-name being guessed
does not reduce the finding — the privilege-crossing reply is the proof.

## The anti-pattern record

`anti: <the claim>: <the reality>` — each false-positive named; the
rule that corrects it.
