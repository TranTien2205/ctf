# Class recheck: cmdi

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Recon evidence web-command-injection needs: params
that plausibly reach a system call (ping, lookup, convert,
export, backup, filename ops), the OS fingerprint (linux
vs windows - error paths/headers), output channel (does the
command output come back? blind vs inline), and filename/
path params anywhere.
## Pivot

Signal harvested -> out-*; route named -> that skill.
