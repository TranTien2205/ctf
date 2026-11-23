# Handoff format: evidencerule

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Evidence rule: an observation needs the
bytes it was read from - a status, a header line, a body
excerpt. 'Looks like Django' without the sessionid/csrftoken
line is a guess. Tools that emit response+excerpt together
(http_probe) are the sanctioned path.
## Pivot

Signal harvested -> out-*; route named -> that skill.
