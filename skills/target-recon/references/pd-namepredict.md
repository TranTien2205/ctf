# Param discovery: namepredict

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Param-name prediction from observed data:
JS variable names, error messages ('missing field: redirect_url'),
redirect targets' query keys, HTML comments, JSON response
fields (a response field 'isAdmin' predicts a request param).
Every leaked name goes into the candidate list verbatim with
its source.
## Pivot

Signal harvested -> out-*; route named -> that skill.
