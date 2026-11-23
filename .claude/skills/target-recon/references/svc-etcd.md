# Service recon: etcd

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

etcd: HTTP on 2379 - /version returns the version
JSON verbatim, /v2/keys/?recursive=true or /v3/kv/range lists
the keyspace when unauthenticated = cluster config+secrets.
A discovery registry left open is a classic CTF pivot.
## Pivot

Signal harvested -> out-*; route named -> that skill.
