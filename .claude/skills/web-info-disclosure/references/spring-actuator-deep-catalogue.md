# Spring Actuator — the full endpoint map — case catalogue

Actuator's value isn't /env alone — it's the whole endpoint inventory: mappings, beans, configprops, heapdump, sessions.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /actuator/mappings | all routes | new attack surface |
| 2 | /actuator/configprops | all config properties | secrets and structure |
| 3 | /actuator/heapdump | JVM memory dump | creds/keys in strings |
| 4 | /actuator/env + /info + /beans | env, metadata, bean graph | secrets and structure |

## Falsifier

Falsifier — only health/info exposed and they're minimal: the rich endpoints are off.
