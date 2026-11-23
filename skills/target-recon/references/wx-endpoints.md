# WebSocket recon: endpoints

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

WebSocket endpoint discovery: /ws /socket
/socket.io/?EIO=4 /sockjs/info /live /realtime /stream /
gateway in JS bundles - the connect call sites name the real
path. SockJS /info returns JSON verbatim; socket.io returns
its EIO handshake parameters.
## Pivot

Signal harvested -> out-*; route named -> that skill.
