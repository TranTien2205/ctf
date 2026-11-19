# Debug and actuator endpoints — operational checklist

Framework debug surfaces hand out env vars, routes, health internals, heap dumps, and sometimes an interactive console. Spring Actuator, Django __debug__, Flask/Werkzeug debugger, Laravel debug pages.

## Checklist

- [ ] Probe: /actuator /actuator/env /actuator/health /actuator/mappings /actuator/heapdump.
- [ ] Probe framework debug: /__debug__/ /debug /_profiler /telescope /horizon.
- [ ] actuator/env → env vars including secrets; actuator/mappings → all routes (new attack surface).
- [ ] actuator/heapdump → download and strings it for credentials.
- [ ] Werkzeug console needs a PIN — check /console for the traceback page that leaks it.

## Abort conditions

- /actuator root 404 doesn't mean /actuator/env 404s — probe specific endpoints.
- heapdump can be 100MB+ — stream and grep, don't load it.
- Some debug endpoints need a specific Accept header or auth — a 403 may be role-scoped, not closed.

## Falsifier

Falsifier — all debug paths 404/403 and error pages are generic: debug surfaces are off. The disclosure channel is closed; other classes own the challenge.

## Cross-references

`error-pages.md` · `env-config-leaks.md` · `framework-debug.md`
