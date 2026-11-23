# Handoff format: format

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Observation record format: <what>: <verbatim
excerpt> [<source request>]. Example -
server-header: "nginx/1.24.0" [GET / 200]. Every line has a
source; a line without a source is a guess and is labelled
one. classify.py consumes this list verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
