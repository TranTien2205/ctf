# Crawl strategy: boundary

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Crawl boundary: same-origin only, the supplied
port only; outbound links are recorded but never followed.
Subdomains in scope rules only. A crawl that exits scope
stops - the recorded out-of-scope surface goes to out-*.
## Pivot

Signal harvested -> out-*; route named -> that skill.
