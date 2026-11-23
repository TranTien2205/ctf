# Class recheck: websocket

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Recon evidence web-websocket needs: endpoint
paths, handshake posture (101? origin checked? protocol
list), message format after connect (JSON-RPC/STOMP/socket.io
envelope/raw), auth expectations (token frame? cookie?),
and cross-site hijack surface (origin unchecked + cookie
auth = cswh prior).
## Pivot

Signal harvested -> out-*; route named -> that skill.
