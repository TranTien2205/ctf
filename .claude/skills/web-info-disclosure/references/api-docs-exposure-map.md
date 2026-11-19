# API docs and schema exposure — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /swagger.json or /openapi.json 200 | OpenAPI served | read all paths |
| /graphql + introspection response | schema readable | hands to web-graphql |
| /api/docs, /redoc, /scalar, /docs | doc UI | fetch the spec it loads |
| Postman collection link or /v1/openapi | spec artifact | read |

## Falsifier

Falsifier — no spec endpoints exist and the API surface is small and self-evident: nothing hidden was disclosed.
