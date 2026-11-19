# .env variant enumeration — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.env 403 but /.env.bak 200 | backup variant wins | read it |
| /.env.production vs /.env.local | environment variants | production secrets |
| /.env.example with real values | dev left real values | read it |

## Falsifier

Falsifier — every variant returns catch-all/404: no .env exposure.
