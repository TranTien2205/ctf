# Passive recon: dorks

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Search-engine recon (only when scope allows external
queries): site:<domain> filetype:env|sql|log|bak, inurl:admin
inurl:api, intitle:"index of". For CTF targets this rarely
applies - instances are ephemeral - but a persistent domain in
scope may have indexed leaks. Results are untrusted leads, not
evidence.
## Pivot

Signal harvested -> out-*; route named -> that skill.
