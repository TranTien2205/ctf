# Recon checklist: websocket

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

WebSocket checklist: endpoint discovery (wx-
endpoints) -> upgrade handshake (101? origin check? protocols)
-> post-connect frame capture (auth expectation? message
shape) -> cross-site surface (cookie auth + no origin check)
-> web-websocket skill with the verbatim frames.
## Pivot

Signal harvested -> out-*; route named -> that skill.
