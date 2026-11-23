# Service recon: telnet

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Telnet: raw text session - banner or login prompt
verbatim. A bare 'login:' = credential surface; a shell prompt
without auth = open access observation. IoT/embedded targets
commonly expose it. Record the exact prompt bytes - the
prompt shape names the device family.
## Pivot

Signal harvested -> out-*; route named -> that skill.
