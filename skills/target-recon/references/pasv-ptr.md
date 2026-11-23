# Passive recon: ptr

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Reverse-lookup the IP: dig -x <ip>. A PTR naming
staging.internal.corp or node03.cluster.local reveals internal
naming conventions = wordlist seeds and environment hints.
No PTR or a generic cloud PTR (ec2-x-x-x-x) is itself recorded
as the negative it is.
## Pivot

Signal harvested -> out-*; route named -> that skill.
