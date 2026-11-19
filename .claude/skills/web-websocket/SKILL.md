---
name: web-websocket
description: >
  WebSocket and realtime-API testing. Use when the target opens a ws:// or wss://
  channel, uses Socket.IO or SockJS, or a live feature (chat, notifications,
  presence) carries the flag path. Covers cross-site WebSocket hijacking, missing
  message-level authorization, and origin checks.
tags: [web, websocket, cswsh, realtime, ctf]
environment: [ctf, lab, authorized-testing]
---

# WebSocket / realtime API

**Catalogue technique.** Nothing in this toolkit has solved a WebSocket challenge
yet. Treat the content as standard published knowledge and record what actually
happens in `field-notes.md`.

## Recognise

A handshake upgrade (`Upgrade: websocket`), a `ws://`/`wss://` URL in front-end
JavaScript, `socket.io`, `sockjs`, or a feature that updates without a reload.
The interesting question is not the protocol; it is **what authenticates the
channel and what authorizes each message**.

## Operational probe

1. Capture the handshake request from front-end JavaScript or the browser. Note
   whether it carries a `Cookie`, an `Authorization` header, or a token inside
   the first message.
2. Open the channel from a second, unauthenticated context and from a foreign
   `Origin`. A server that accepts the handshake and then answers with victim
   data or accepts a privileged action is the finding.
3. Send one benign, attributable message (a marker in your own room/object) and
   read the reply. Do not send a destructive action first.

```javascript
// run from a page with a foreign Origin; the browser attaches the victim cookie
var ws = new WebSocket("wss://TARGET/ws");
ws.onmessage = e => console.log(e.data);
ws.onopen = () => ws.send(JSON.stringify({action:"ping", marker:"wsprobe"}));
```

Outside a browser, `tools/web/ws_probe.py` performs the handshake and reads
frames directly — the foreign-Origin check without a victim cookie, and the
first message capture when the front-end JS names the expected protocol:

```bash
python tools/web/ws_probe.py "wss://TARGET/ws" --message '{"action":"ping"}'
python tools/web/ws_probe.py "wss://TARGET/ws" --origin "https://evil.example"
python tools/web/ws_probe.py "ws://TARGET/ws" --headers 'Cookie: session=abc'
```

Expected confirmation is a message the server should not have sent to that
context, or a state change attributable to the message. A successful handshake,
a 101 response, or an empty ping reply is surface evidence only.

## Message-level authorization

A channel that authenticates once at the handshake often trusts every later
message. After the channel is open, test:

- an object id belonging to another identity, with no ownership check per message;
- an action the UI never exposes, named only in the client bundle;
- a role or `user_id` field the client can set in the message body.

## Traps

- SameSite cookies and browser origin rules decide whether a cross-site
  handshake carries credentials; read them before claiming hijacking.
- Socket.IO wraps messages in a framing envelope (`40`, `42["event",...]`).
  Read the framing before assuming a plain JSON protocol.
- A binary frame that is not JSON may be protobuf wire format —
  `python3 tools/proto_decode.py blob.bin` (or `--hex`) walks field
  keys without needing the `.proto`; the flag then usually sits in a
  numbered field, not a named one.
- One channel at a time: two concurrent payloads make the reply unattributable.
- Do not use the channel for a destructive broadcast; it affects every client.

## Routing

Shares signals with: `../web-csrf/`, `../web-auth-session/`, `../web-xss/`.
Depth, one named file at a time: `../ctf-web/client-side.md`.

| Any channel-abuse question | `references/channel-abuse.md` / `references/channel-abuse-deep.md` |
|---|---|
| the model | `references/mechanism.md` / `references/mechanism-deep.md` / `references/theory.md` / `references/theory-deep.md` / `references/summary.md` / `references/summary-deep.md` / `references/glossary.md` / `references/glossary-deep.md` |
| the handshake checks | `references/handshake-side.md` / `references/handshake-side-deep.md` |
| CSWSH | `references/cswsh.md` / `references/cswsh-deep.md` |
| the message checks | `references/message-side.md` / `references/message-side-deep.md` |
| a per-frame object gap | `references/message-idor.md` / `references/message-idor-deep.md` |
| a privileged action | `references/action-dispatch.md` / `references/action-dispatch-deep.md` |
| an injection carrier | `references/injection-in-frames.md` / `references/injection-in-frames-deep.md` |
| the envelope | `references/framing-protocols.md` / `references/framing-protocols-deep.md` |
| the timed pass | `references/workflow.md` / `references/workflow-deep.md` / `references/first-hour.md` / `references/recon-order.md` |
| detection | `references/detection.md` / `references/detection-deep.md` / `references/detection-matrix.md` / `references/detection-index.md` / `references/detection-checklist.md` / `references/detection-surface.md` / `references/detection-playbook.md` / `references/detection-catalogue.md` / `references/detection-signals.md` / `references/detection-map.md` / `references/detection-verdicts.md` / `references/detection-workflow.md` |
| the evidence discipline | `references/evidence-rules.md` / `references/evidence-rules-deep.md` / `references/evidence-map.md` |
| the kill-map | `references/falsifiers.md` / `references/falsifiers-deep.md` / `references/per-falsifier.md` |
| the dead ends | `references/negative-results.md` / `references/negative-results-deep.md` / `references/negative-map.md` |
| the pass, box by box | `references/checklist.md` / `references/checklist-deep.md` |
| the required state | `references/preconditions.md` / `references/preconditions-deep.md` |
| the nonstandard cases | `references/edge-cases.md` / `references/edge-cases-deep.md` |
| the failure modes | `references/common-mistakes.md` / `references/common-mistakes-deep.md` / `references/anti-patterns.md` |
| the fix map | `references/troubleshoot.md` / `references/troubleshoot-deep.md` |
| the check bypasses | `references/evasion.md` / `references/evasion-deep.md` |
| the payload corpus | `references/payload-variants.md` / `references/payload-dictionary.md` / `references/payload-map.md` / `references/extended-corpus.md` / `references/probe-catalogue.md` / `references/probe-map.md` |
| the exploit templates | `references/attack-shapes.md` / `references/multi-step-chains.md` / `references/exploitation.md` / `references/second-order.md` |
| the worked material | `references/worked-examples.md` / `references/scenarios.md` / `references/case-studies.md` / `references/case-studies-deep.md` / `references/real-world-cases.md` / `references/verified-chains.md` |
| the mechanism inventory | `references/mechanism-index.md` / `references/mechanism-map.md` / `references/mechanism-catalogue.md` |
| the reply verdicts | `references/decision-table.md` / `references/decision-catalogue.md` / `references/detection-verdicts.md` |
| the cheat sheets | `references/quick-map.md` / `references/quick-reference.md` / `references/quick-reference-deep.md` |
| the grammar | `references/lead-grammar.md` |
| the boundaries | `references/boundary-map.md` / `references/per-boundary.md` |
| the routes | `references/per-route.md` / `references/reporting.md` |
| per endpoint | `references/per-endpoint.md` / `references/per-endpoint-deep.md` |
| per field | `references/per-message-field.md` / `references/per-message-field-deep.md` |
| per transport | `references/per-transport.md` / `references/per-transport-deep.md` |
| per channel | `references/per-channel.md` |
| per mechanism | `references/per-mechanism.md` |
| per check | `references/per-check.md` |
| per surface | `references/per-surface.md` / `references/per-surface-map.md` |
| per vector | `references/per-vector.md` |
| per target | `references/per-target.md` |
| the operator files | `references/field-manual.md` / `references/operator-notes.md` / `references/closing-notes.md` / `references/onboarding.md` / `references/onboarding-deep.md` / `references/field-notes-deep.md` / `references/common-questions.md` / `references/class-boundary.md` |

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class is
solved. See `../../LEARNING_LOOP.md`.
