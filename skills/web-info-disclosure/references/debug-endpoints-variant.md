# Debug and actuator endpoints — surface variants

Framework debug surfaces hand out env vars, routes, health internals, heap dumps, and sometimes an interactive console. Spring Actuator, Django __debug__, Flask/Werkzeug debugger, Laravel debug pages.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| /actuator → JSON link list | Spring Actuator | enumerate env/health/routes |
| /actuator/env or /heapdump | secrets or memory | read for creds |
| __debug__ toolbar or /debug routes | framework debug on | read config |
| Werkzeug debugger page | Flask debug console | PIN exploit or read frames |

## Variant-specific traps

- /actuator root 404 doesn't mean /actuator/env 404s — probe specific endpoints.
- heapdump can be 100MB+ — stream and grep, don't load it.
- Some debug endpoints need a specific Accept header or auth — a 403 may be role-scoped, not closed.
- Spring Boot 2.x vs 3.x paths differ (/actuator/env vs /actuator/env/{name}).

## Falsifier

Falsifier — all debug paths 404/403 and error pages are generic: debug surfaces are off. The disclosure channel is closed; other classes own the challenge.

## Cross-references

`error-pages.md` · `env-config-leaks.md` · `framework-debug.md`
