# WebSocket recon: messageshape

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Message-shape capture: after 101, the first
frames reveal the protocol - socket.io '40{...}' envelope,
JSON-RPC, STOMP frames (CONNECT/subscribe), raw JSON, binary.
The auth frame expectation (send token? cookie-only?) is the
authorization surface question for the websocket skill.
## Pivot

Signal harvested -> out-*; route named -> that skill.
