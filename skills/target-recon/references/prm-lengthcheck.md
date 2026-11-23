# Param-level recon: lengthcheck

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Per-param length check: where does it truncate
or reject? A hard max suggests validation exists; silent
truncation at N suggests a DB column limit (type+length
info leak); no limit with storage = upload/logic surface.
Record the boundary number verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
