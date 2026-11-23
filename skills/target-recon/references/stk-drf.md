# Stack playbook: drf

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Django REST Framework: browsable API HTML on every
endpoint, 'Django REST framework' header block, OPTIONS returns
verbose allow/renders/parses metadata, ?format=json switch.

Recon checks:
- GET /api/ -> root route map often lists every viewset
- OPTIONS on an endpoint -> allowed methods + field schema
  (parameter inventory free of guessing)
- ?format=api vs ?format=json -> renderer list
- Pagination style (page/size vs cursor) names the iteration
  surface
- Versioning: /api/v1/, Accept-Version header

Predicts: massassign on writable serializer fields, idor on
pk endpoints, authz gaps on viewsets, nosqli if MongoEngine
backed.
## Pivot

Signal harvested -> out-*; route named -> that skill.
