# Stack playbook: express

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Express fingerprints: X-Powered-By: Express,
connect.sid cookie, JSON APIs under /api/, body-parser shapes.

Recon checks:
- connect.sid decode (express-signed) -> session_dissect
- /api/ route conventions -> enumerate resources
- Query array syntax ?a[]=x&a[]=y -> qs parser = nosqli +
  prototype-pollution class weight
- JSON body with object values ($gt, __proto__) acceptance ->
  nosqli/massassign prediction
- Error handler leaks stack in dev (NODE_ENV)
- helmet absence -> loose headers

Predicts: nosqli (operator injection), prototype-pollution,
massassign, authz on JWT-less endpoints.
## Pivot

Signal harvested -> out-*; route named -> that skill.
