# Input via environment — env-var buffers — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| getenv('X') then strcpy | env input | X = payload |
| the env value reaches a stack buffer | env overflow | set it in the environment |

## Falsifier

Falsifier — the env var isn't copied to a stack buffer or is validated first: not this route.
