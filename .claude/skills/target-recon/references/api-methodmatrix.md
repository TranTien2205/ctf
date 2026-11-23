# API recon: methodmatrix

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Method matrix per discovered endpoint:
OPTIONS first (Allow: header + CORS pre-flight reveals the
set free), then single GET/POST/PUT/PATCH/DELETE/HEAD.
Different methods on one route = different code paths =
different authz. 405 vs 501 vs 404 recorded verbatim -
a 405 on PUT where GET works confirms the route exists.
## Pivot

Signal harvested -> out-*; route named -> that skill.
