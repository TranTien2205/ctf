# Service recon: elastic

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Elasticsearch: GET / returns JSON
{name,cluster_name,version:{number,lucene_version}} = complete
identity. /_cat/indices?v lists index names = data inventory;
/_cat/aliases, /_nodes. Unauthenticated 200 = the observation;
kibana/dev-tools paths on adjacent surface noted.
## Pivot

Signal harvested -> out-*; route named -> that skill.
