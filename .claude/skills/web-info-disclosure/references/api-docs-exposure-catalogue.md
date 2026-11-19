# API docs and schema exposure — case catalogue

Swagger/OpenAPI, GraphQL introspection, and generated API docs hand you the complete endpoint map plus parameter shapes — the cheapest route map available.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /swagger.json or /openapi.json 200 | OpenAPI served | read all paths |
| 2 | /graphql + introspection response | schema readable | hands to web-graphql |
| 3 | /api/docs, /redoc, /scalar, /docs | doc UI | fetch the spec it loads |
| 4 | Postman collection link or /v1/openapi | spec artifact | read |

## Falsifier

Falsifier — no spec endpoints exist and the API surface is small and self-evident: nothing hidden was disclosed.

## Coverage notes

- A docs UI page is HTML; find the spec URL it loads (usually in the page source).
- Private/internal operations may need auth even in the spec — listed is not callable.
- Old spec versions may persist at versioned paths (/v1/ when the API is v3).

## Cross-references

`exposed-artifacts.md` · `../web-graphql/`
