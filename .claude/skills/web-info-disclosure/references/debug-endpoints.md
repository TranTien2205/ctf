# Debug and actuator endpoints

Framework debug surfaces hand out env vars, routes, health internals, heap dumps, and sometimes an interactive console. Spring Actuator, Django __debug__, Flask/Werkzeug debugger, Laravel debug pages.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /actuator → JSON link list | Spring Actuator | enumerate env/health/routes |
| /actuator/env or /heapdump | secrets or memory | read for creds |
| __debug__ toolbar or /debug routes | framework debug on | read config |
| Werkzeug debugger page | Flask debug console | PIN exploit or read frames |
| Whoops/Ignition styled error page | PHP debug on | read env, check RCE history |

## Steps

1. Probe: /actuator /actuator/env /actuator/health /actuator/mappings /actuator/heapdump.
2. Probe framework debug: /__debug__/ /debug /_profiler /telescope /horizon.
3. actuator/env → env vars including secrets; actuator/mappings → all routes (new attack surface).
4. actuator/heapdump → download and strings it for credentials.
5. Werkzeug console needs a PIN — check /console for the traceback page that leaks it.

## Falsifier

Falsifier — all debug paths 404/403 and error pages are generic: debug surfaces are off. The disclosure channel is closed; other classes own the challenge.

## Traps

- /actuator root 404 doesn't mean /actuator/env 404s — probe specific endpoints.
- heapdump can be 100MB+ — stream and grep, don't load it.
- Some debug endpoints need a specific Accept header or auth — a 403 may be role-scoped, not closed.
- Spring Boot 2.x vs 3.x paths differ (/actuator/env vs /actuator/env/{name}).

## Commands

```bash
for p in /actuator /actuator/env /actuator/heapdump /__debug__/ /_profiler; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`error-pages.md` · `env-config-leaks.md` · `framework-debug.md`
