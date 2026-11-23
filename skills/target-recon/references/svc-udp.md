# Service recon: udp

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

UDP service: no connect, no banner - send an empty
datagram then a newline then a protocol guess. Silence is the
recorded negative; any reply is the protocol's identity. DNS
on 53, SNMP community probing, NTP version requests are the
named shapes. One probe per guess - UDP has no backpressure.
## Pivot

Signal harvested -> out-*; route named -> that skill.
