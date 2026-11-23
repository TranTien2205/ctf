# Param-level recon: dupcheck

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Duplicate-param check: ?id=1&id=2 - first wins,
last wins, array, or error? Parser-merge behavior predicts
nosqli (arrays), parser-differential (proxy vs app picks
different), massassign (object merge). Record the merge
rule observed verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
