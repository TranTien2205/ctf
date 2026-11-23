# Recon workflow: priorityorder

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Priority order of harvest: page+headers
(1 req, stack+params) -> JS/bundle (1 req, endpoints+secrets)
-> docs surfaces (1 req, full map) -> robots/sitemap/well-known
(cheap oddities) -> forms -> method/content-type matrices ->
wordlist enum (last, most expensive, smallest list).
## Pivot

Signal harvested -> out-*; route named -> that skill.
