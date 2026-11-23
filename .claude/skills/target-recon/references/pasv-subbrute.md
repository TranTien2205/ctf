# Passive recon: subbrute

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Active subdomain brute (only when scope grants
name sprawl): ffuf/gobuster vhost mode against the IP with a
bounded subdomain list - calibrated on the default-vhost
response first (vh-fuzz). For CTF instances this rarely
applies - the supplied name IS the surface.
## Pivot

Signal harvested -> out-*; route named -> that skill.
