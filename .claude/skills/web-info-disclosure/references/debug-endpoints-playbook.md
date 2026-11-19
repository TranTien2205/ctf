# Debug and actuator endpoints — playbook

Framework debug surfaces hand out env vars, routes, health internals, heap dumps, and sometimes an interactive console. Spring Actuator, Django __debug__, Flask/Werkzeug debugger, Laravel debug pages.

## Ordered playbook

1. Probe: /actuator /actuator/env /actuator/health /actuator/mappings /actuator/heapdump.
2. Probe framework debug: /__debug__/ /debug /_profiler /telescope /horizon.
3. actuator/env → env vars including secrets; actuator/mappings → all routes (new attack surface).
4. actuator/heapdump → download and strings it for credentials.
5. Werkzeug console needs a PIN — check /console for the traceback page that leaks it.

## Falsifier

Falsifier — all debug paths 404/403 and error pages are generic: debug surfaces are off. The disclosure channel is closed; other classes own the challenge.

## Commands

```bash
for p in /actuator /actuator/env /actuator/heapdump /__debug__/ /_profiler; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```
