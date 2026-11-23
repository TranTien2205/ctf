# Protocol recon: proxytopology

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Proxy-topology assembly: from Via chains,
X-Forwarded-For hops, edge headers (cf-*, x-amz-*, akamai-),
error-page style changes (front vs app signatures) - the
hop map IS the parser-differential/smuggling input. Record
each hop's identity.
## Pivot

Signal harvested -> out-*; route named -> that skill.
