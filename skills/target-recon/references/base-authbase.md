# Baseline calibration: authbase

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Auth baseline: one request with a nonsense
credential (bad token/bad cookie) - capture the rejection
shape (401 shape? 403? redirect?) = the auth-failure
signature every later authed probe diffs against.
## Pivot

Signal harvested -> out-*; route named -> that skill.
