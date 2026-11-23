# API recon: openapi

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

OpenAPI hunting in order: /openapi.json /openapi.yaml
/swagger.json /swagger.yaml /api-docs /v2/api-docs /v3/api-docs
/swagger-ui.html /docs /redoc /api/schema /api/openapi.json
/.well-known/schema-discovery. One 200 here ends route
enumeration - the doc IS the surface map: paths, methods,
params, schemas, auth requirements, all verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
