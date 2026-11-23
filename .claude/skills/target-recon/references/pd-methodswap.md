# Param discovery: methodswap

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Method swap on each discovered endpoint: GET
params -> POST body -> PUT -> header. Same route accepting
both = two code paths = two authz opportunities. PHP-style
params on POST when route expects JSON can reveal a secondary
parser - record which method each accepted, verbatim status.
## Pivot

Signal harvested -> out-*; route named -> that skill.
