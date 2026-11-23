# Recon trap: certrequired

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Trap: a service demanding client certs that
looks 'dead'. Mutual-TLS rejection (handshake failure,
certificate required alert) is a posture observation - the
port is alive and gated, not closed. Record it; do not keep
probing it like a normal web port.
## Pivot

Signal harvested -> out-*; route named -> that skill.
