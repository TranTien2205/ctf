# Handoff format: classifyready

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Classify-ready check: the list is ready
when stack identity is named-or-unknown, endpoint/param
inventory exists, every item has its evidence, and negatives
are recorded. Then: classify.py "<the list>" then
chain_match.py "<strongest single signal>" - recon is done.
## Pivot

Signal harvested -> out-*; route named -> that skill.
