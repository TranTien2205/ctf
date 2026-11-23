# Tool output parsing: ffufout

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

ffuf output -> observations: status+size+words+
lines per hit; filter-calibrated hits only (-fs/-fc set from
baseline). Each surviving line = one 'path found' observation
with its verbatim status/length. The ffuf run's filter
settings go in the observation note.
## Pivot

Signal harvested -> out-*; route named -> that skill.
