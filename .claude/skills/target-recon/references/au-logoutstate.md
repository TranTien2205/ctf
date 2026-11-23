# Authenticated recon: logoutstate

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Logout/session-lifecycle probe: does POST
/logout actually invalidate (re-request with the same session
verbatim), do sessions persist across logins, is there
remember-me. A session that survives logout is a recorded
observation - fixation and lifecycle weaknesses start here.
## Pivot

Signal harvested -> out-*; route named -> that skill.
