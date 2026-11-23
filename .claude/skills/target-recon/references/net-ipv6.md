# Network recon: ipv6

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

IPv6 intake: check AAAA (dig AAAA <domain>) - an
answer means the family exists; dual-stack hosts can serve
different vhosts per family. [host]:port syntax for direct
probes. Record the family map; missing AAAA = the negative
note, not a dead end.
## Pivot

Signal harvested -> out-*; route named -> that skill.
