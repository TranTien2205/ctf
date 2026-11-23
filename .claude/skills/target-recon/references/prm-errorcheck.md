# Param-level recon: errorcheck

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Per-param error check: bad type, over-length,
special chars - does it 400 with a message (names expected
format = free schema), 500 with a stack (debug posture +
parser identity), or silently clamp? Error behavior per
param is its own observation; a silent clamp predicts logic
surfaces.
## Pivot

Signal harvested -> out-*; route named -> that skill.
