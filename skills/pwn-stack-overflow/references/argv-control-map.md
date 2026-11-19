# Input via argv — when the read is the command line — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| main uses argv[1] directly | argv input | the arg is the buffer |
| copied into a stack buffer | argv overflow | argv[1] = payload |

## Falsifier

Falsifier — the input isn't argv — check stdin/protocol paths.
