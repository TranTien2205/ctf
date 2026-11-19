# API docs and schema exposure

Swagger/OpenAPI, GraphQL introspection, and generated API docs hand you the complete endpoint map plus parameter shapes — the cheapest route map available.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /swagger.json or /openapi.json 200 | OpenAPI served | read all paths |
| /graphql + introspection response | schema readable | hands to web-graphql |
| /api/docs, /redoc, /scalar, /docs | doc UI | fetch the spec it loads |
| Postman collection link or /v1/openapi | spec artifact | read |

## Steps

1. Probe: /swagger.json /openapi.json /api-docs /v3/api-docs /graphql.
2. Parse the spec: every path, method, and parameter is now known — the fuzz surface.
3. Flag admin/internal/debug routes in the spec for priority probing.
4. GraphQL introspection → hand to web-graphql for schema abuse.

## Falsifier

Falsifier — no spec endpoints exist and the API surface is small and self-evident: nothing hidden was disclosed.

## Traps

- A docs UI page is HTML; find the spec URL it loads (usually in the page source).
- Private/internal operations may need auth even in the spec — listed is not callable.
- Old spec versions may persist at versioned paths (/v1/ when the API is v3).

## Commands

```bash
for p in /swagger.json /openapi.json /api-docs /graphql; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`exposed-artifacts.md` · `../web-graphql/`
