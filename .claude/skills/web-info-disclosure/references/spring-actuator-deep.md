# Spring Actuator — the full endpoint map

Actuator's value isn't /env alone — it's the whole endpoint inventory: mappings, beans, configprops, heapdump, sessions.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /actuator/mappings | all routes | new attack surface |
| /actuator/configprops | all config properties | secrets and structure |
| /actuator/heapdump | JVM memory dump | creds/keys in strings |
| /actuator/env + /info + /beans | env, metadata, bean graph | secrets and structure |

## Steps

1. Enumerate every /actuator/<name> the root lists.
2. env → secrets; mappings → all routes; configprops → full config.
3. heapdump → download, strings, grep for passwords/keys/flag.
4. beans → the dependency graph; httptrace → recent requests.

## Falsifier

Falsifier — only health/info exposed and they're minimal: the rich endpoints are off.

## Traps

- Actuator paths differ between Boot 2/3 and configs — enumerate from the root.
- heapdump needs analysis tooling (strings + grep is enough for secrets).
- Some endpoints are write-capable (shutdown, restart) — read-only is the disclosure boundary.

## Commands

```bash
curl -s '$BASE/actuator' ; curl -s '$BASE/actuator/env'
```

## Cross-references

`debug-endpoints.md` · `env-config-leaks.md`
