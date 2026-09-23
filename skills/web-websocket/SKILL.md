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
- One channel at a time: two concurrent payloads make the reply unattributable.
- Do not use the channel for a destructive broadcast; it affects every client.

## Routing

Shares signals with: `../web-csrf/`, `../web-auth-session/`, `../web-xss/`.
Depth, one named file at a time: `../ctf-web/client-side.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class is
solved. See `../../LEARNING_LOOP.md`.
