# Debug and actuator endpoints — summary

Framework debug surfaces hand out env vars, routes, health internals, heap dumps, and sometimes an interactive console. Spring Actuator, Django __debug__, Flask/Werkzeug debugger, Laravel debug pages.

## Signal → route

- /actuator → JSON link list → enumerate env/health/routes
- /actuator/env or /heapdump → read for creds
- __debug__ toolbar or /debug routes → read config
- Werkzeug debugger page → PIN exploit or read frames
- Whoops/Ignition styled error page → read env, check RCE history

## Falsifier

Falsifier — all debug paths 404/403 and error pages are generic: debug surfaces are off. The disclosure channel is closed; other classes own the challenge.
