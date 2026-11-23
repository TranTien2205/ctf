# Passive recon: axfr

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Zone-transfer attempt (within scope): dig axfr
@<ns> <domain> - a successful AXFR = complete zone map =
instant subdomain+record inventory. Almost always refused;
the refusal is the recorded negative and the attempt is
documented as the cheapest DNS question.
## Pivot

Signal harvested -> out-*; route named -> that skill.
