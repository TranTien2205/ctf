# Worked example: websocket

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Walked: JS showed new WebSocket('wss://.../ws').

1. wx-handshake probe -> 101 Switching Protocols, no Origin
   check observed, subprotocol list empty.
2. wx-messageshape: first frame '40{"sid":...}' = socket.io
   envelope; server expects token in auth payload.
3. Observations: ws endpoint, socket.io, origin-unchecked,
   token-in-payload auth.
4. Route: web-websocket with the verbatim handshake + frame.
## Pivot

Signal harvested -> out-*; route named -> that skill.
