# Vhost/subdomain: fuzz

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

VHost fuzzing (only when scope grants name sprawl):
ffuf -u http://IP:port/ -H 'Host: FUZZ.domain' -w small-list
with -fs filtering the default-vhost size - the calibrated
negative FIRST. Every hit is a new name on the same host;
a shared instance gets a small wordlist and low rate.
## Pivot

Signal harvested -> out-*; route named -> that skill.
