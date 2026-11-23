# API recon: pagination

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Pagination shape: ?page= ?limit= ?offset=
?cursor= ?per_page= ?skip=. Enumerating pages reveals the
object count = collection size observation. limit=0,
limit=-1, limit=99999 acceptance = logic surface worth a
recorded probe later. Cursor style (opaque vs signed)
predicts tamper surface.
## Pivot

Signal harvested -> out-*; route named -> that skill.
