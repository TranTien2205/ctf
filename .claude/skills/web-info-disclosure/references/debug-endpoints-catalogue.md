# Debug and actuator endpoints — case catalogue

Framework debug surfaces hand out env vars, routes, health internals, heap dumps, and sometimes an interactive console. Spring Actuator, Django __debug__, Flask/Werkzeug debugger, Laravel debug pages.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /actuator → JSON link list | Spring Actuator | enumerate env/health/routes |
| 2 | /actuator/env or /heapdump | secrets or memory | read for creds |
| 3 | __debug__ toolbar or /debug routes | framework debug on | read config |
| 4 | Werkzeug debugger page | Flask debug console | PIN exploit or read frames |
| 5 | Whoops/Ignition styled error page | PHP debug on | read env, check RCE history |

## Falsifier

Falsifier — all debug paths 404/403 and error pages are generic: debug surfaces are off. The disclosure channel is closed; other classes own the challenge.

## Coverage notes

- /actuator root 404 doesn't mean /actuator/env 404s — probe specific endpoints.
- heapdump can be 100MB+ — stream and grep, don't load it.
- Some debug endpoints need a specific Accept header or auth — a 403 may be role-scoped, not closed.
- Spring Boot 2.x vs 3.x paths differ (/actuator/env vs /actuator/env/{name}).

## Cross-references

`error-pages.md` · `env-config-leaks.md` · `framework-debug.md`
