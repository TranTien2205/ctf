# API recon: contenttype

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Content-Type probing: same endpoint accepts
application/json, application/x-www-form-urlencoded,
multipart/form-data, text/xml? Each parser is a different
code path: JSON -> nosqli/prototype shapes, XML -> xxe
surface, form -> classic injection, multipart -> upload.
A 415 names the accepted types verbatim - that IS the answer.
## Pivot

Signal harvested -> out-*; route named -> that skill.
