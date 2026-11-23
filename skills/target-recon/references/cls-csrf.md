# Class recheck: csrf

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Recon evidence web-csrf needs: the state-changing route
list (POST/PUT/DELETE forms and actions), CSRF token posture
(token in form? header? absent?), SameSite cookie flag
verbatim, CORS policy on those routes, and whether GET can
also change state (a classic shortcut).
## Pivot

Signal harvested -> out-*; route named -> that skill.
