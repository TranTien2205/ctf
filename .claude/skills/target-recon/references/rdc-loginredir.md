# Redirect recon: loginredir

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Login-redirect map: unauthed requests 302 ->
/login?next=<original> - the 'next' param is a redirect-
param candidate AND tells which routes are gated. 302 vs
401 posture per route = the auth-boundary map for free.
## Pivot

Signal harvested -> out-*; route named -> that skill.
