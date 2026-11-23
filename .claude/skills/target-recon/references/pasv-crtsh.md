# Passive recon: crtsh

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Query crt.sh for the domain: https://crt.sh/?q=%25.<domain>&output=json
Yields: SAN lists = subdomain inventory without touching the
target, historical certs = dead staging hosts, internal names
(dev.corp.local) that leaked into public certs. In-scope use:
names on the SAME host/port only unless scope grants sprawl.
Record each discovered name verbatim with its SAN source line.
## Pivot

Signal harvested -> out-*; route named -> that skill.
