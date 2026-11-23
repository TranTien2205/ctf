# Worked example: api-openapi

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Walked: supplied http://<target>:9000/api.

1. web_probe -> JSON 404 {'detail':'Not Found'} = FastAPI
   shape (stk-fastapi).
2. api-openapi order: GET /openapi.json -> 200 = the whole
   route map in one request (paths+params+schemas verbatim).
3. No wordlist needed - doc IS the enum. Param inventory from
   schema fields; auth scheme from security definitions.
4. Observations: 12 routes, Bearer JWT auth, object params
   accepted on /api/search (pd-jsonvsform).
5. classify -> nosqli candidate on the object-param route.
## Pivot

Signal harvested -> out-*; route named -> that skill.
