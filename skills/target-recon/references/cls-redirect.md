# Class recheck: redirect

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Recon evidence web-open-redirect needs: redirect
params (next, url, return, redirect, dest, callback,
continue, to) across login/error/flow paths, allowlist hints
(same-host enforcement, encoding checks observable), and
where the value is consumed (header Location vs meta vs JS).
## Pivot

Signal harvested -> out-*; route named -> that skill.
