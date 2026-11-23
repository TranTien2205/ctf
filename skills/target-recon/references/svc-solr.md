# Service recon: solr

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Solr: HTTP 8983 - /solr/admin/info/system returns
version+lucene verbatim; /solr/#/ admin UI; /solr/<core>/
select?q= = query surface (the injection/data surface).
Core list from /solr/admin/cores = the index inventory.
## Pivot

Signal harvested -> out-*; route named -> that skill.
