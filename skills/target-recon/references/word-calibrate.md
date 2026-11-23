# Wordlist selection: calibrate

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Calibration first: request 3 known-dead paths
of matching length - a 404-shape baseline. A 200-everything
wildcard server makes wordlists useless until filtered by
size/content (-fs/-fc on ffuf). Calibrate, then enumerate;
the baseline IS the filter.
## Pivot

Signal harvested -> out-*; route named -> that skill.
