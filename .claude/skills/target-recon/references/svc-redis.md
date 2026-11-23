# Service recon: redis

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Redis on the supplied port: send PING - +PONG = RESP
protocol confirmed, unauthenticated. INFO returns version +
OS + config dir verbatim. -NOAUTH means AUTH required = creds
recon problem. -ERR unknown command means not Redis or a
wrapper. One command, one observation; no module loading or
writes during recon.
## Pivot

Signal harvested -> out-*; route named -> that skill.
