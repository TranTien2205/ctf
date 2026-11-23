# Param discovery: headerparams

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Header-parameter surface: custom X-* headers
the app reads (X-Forwarded-For -> IP-based logic, X-Original-URL
-> routing override, X-Api-Version -> behavior switch). JS and
error messages name them; an OPTIONS pre-flight lists accepted
custom headers verbatim via Access-Control-Allow-Headers.
## Pivot

Signal harvested -> out-*; route named -> that skill.
