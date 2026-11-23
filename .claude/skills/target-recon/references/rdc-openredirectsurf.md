# Redirect recon: openredirectsurf

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Redirect-param surface: every observed
param ending in url/next/return/dest/callback/continue/
to/goto in links, forms, JS, errors = the candidate list.
Recon names the params verbatim; the redirect skill tests
whether they are actually free.
## Pivot

Signal harvested -> out-*; route named -> that skill.
