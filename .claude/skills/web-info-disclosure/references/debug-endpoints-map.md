# Debug and actuator endpoints — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /actuator → JSON link list | Spring Actuator | enumerate env/health/routes |
| /actuator/env or /heapdump | secrets or memory | read for creds |
| __debug__ toolbar or /debug routes | framework debug on | read config |
| Werkzeug debugger page | Flask debug console | PIN exploit or read frames |
| Whoops/Ignition styled error page | PHP debug on | read env, check RCE history |

## Falsifier

Falsifier — all debug paths 404/403 and error pages are generic: debug surfaces are off. The disclosure channel is closed; other classes own the challenge.
