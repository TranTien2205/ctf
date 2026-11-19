# Spring Actuator — the full endpoint map — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /actuator/mappings | all routes | new attack surface |
| /actuator/configprops | all config properties | secrets and structure |
| /actuator/heapdump | JVM memory dump | creds/keys in strings |
| /actuator/env + /info + /beans | env, metadata, bean graph | secrets and structure |

## Falsifier

Falsifier — only health/info exposed and they're minimal: the rich endpoints are off.
