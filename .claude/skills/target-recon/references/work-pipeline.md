# The recon pipeline

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

fetch the entry point -> fingerprint -> enumerate ->
harvest signals -> hand off to classify. Each stage
emits observations, not hypotheses.

## Pivot

Signal harvested -> out-*; route named -> that skill.
