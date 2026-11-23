# Recon trap: authbudget

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Trap: burning login attempts in recon. Failed
logins count against lockouts and WAF rules - map the login
flow (au-loginflow) with ONE credential attempt maximum, and
record lockout signals before any second try.
## Pivot

Signal harvested -> out-*; route named -> that skill.
