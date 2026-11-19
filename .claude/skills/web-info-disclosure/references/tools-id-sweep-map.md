# tools/web/id_sweep.py — existence oracle over ids — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| --url contains {id} or {ids} | the sweep template | sequential or list |
| --range LOW-HIGH[:STEP] | numeric sweep | bounded |
| --rate/--retries | politeness + resilience | sized to target |
| --no-follow keeps the 302 oracle | redirect evidence | when 302 is the signal |

## Falsifier

Falsifier — ids return uniform 404/catch-all: no enumerable surface.
