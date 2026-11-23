# Service recon: couchdb

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

CouchDB: HTTP on 5984 - GET / returns
{"couchdb":"Welcome","version":...} verbatim. /_all_dbs lists
databases unauthenticated when open; /_utils = Futon UI;
/_users = the user db. A couch port = nosql-adjacent surface
with admin-party posture as the classic check.
## Pivot

Signal harvested -> out-*; route named -> that skill.
