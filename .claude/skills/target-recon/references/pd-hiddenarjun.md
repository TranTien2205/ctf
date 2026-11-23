# Param discovery: hiddenarjun

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Hidden parameter discovery (arjun-style):
POST/GET candidates from a bounded wordlist (admin, debug,
redirect, token, file, url, id, user, key, secret) - response
length/status deltas name the accepted ones. Calibrate against
a known-dead param first; a wildcard-equal response set means
the method can't discriminate and is recorded as a negative.
## Pivot

Signal harvested -> out-*; route named -> that skill.
