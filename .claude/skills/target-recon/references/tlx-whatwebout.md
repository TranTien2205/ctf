# Tool output parsing: whatwebout

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

whatweb output -> observations: plugin hits
(Server, X-Powered-By, framework names, cms identity) each
with confidence; a 'passive' vs 'aggressive' hit distinction
matters - only what it measured is claimed.
## Pivot

Signal harvested -> out-*; route named -> that skill.
