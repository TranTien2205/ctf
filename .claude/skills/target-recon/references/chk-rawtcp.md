# Recon checklist: rawtcp

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Raw-TCP checklist: nc banner grab (verbatim) ->
text? HELP/probe commands -> binary? protocol-shape ->
svc-* family match -> interactive prompt -> pwn-binary-
triage. One command per guess, every response verbatim -
raw services have no 404 to calibrate against.
## Pivot

Signal harvested -> out-*; route named -> that skill.
