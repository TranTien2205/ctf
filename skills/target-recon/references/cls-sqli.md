# Class recheck: sqli

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Recon evidence web-sqli needs: injectable params (numeric
ids, sort/order, search, filter fields), the DBMS hint from
error/stack/version, which requests are POST-JSON vs GET-query
(different injection surface), auth boundary on the target
param, and any existing reflection/error oracle already
observed. Deliver: param list + DBMS prior + one oracle.
## Pivot

Signal harvested -> out-*; route named -> that skill.
