# Vhost/subdomain: sanenum

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

SAN enumeration: names on the live cert plus crt.sh
SAN lists = candidate virtual hosts on the same IP. Each name
in scope gets one Host-header probe against the supplied
IP:port - a different response size vs the IP default = a real
vhost. Record name, status, and length verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
