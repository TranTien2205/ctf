# API recon: restshape

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

REST shape mapping: /api/<resource>/<id>/<action>
conventions. Enumerated resources predict siblings: /api/users
means /api/orders, /api/admin are worth single probes. Plural
nouns, kebab-case, version prefixes. A resource named in JS
but absent on GET may answer POST/PUT - method matrix next.
## Pivot

Signal harvested -> out-*; route named -> that skill.
