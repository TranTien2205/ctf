# .env variant enumeration — case catalogue

The .env file has a family: .env.local, .env.production, .env.development, .env.bak, .env.old, .env.save, .env.example — each with different exposure rules.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /.env 403 but /.env.bak 200 | backup variant wins | read it |
| 2 | /.env.production vs /.env.local | environment variants | production secrets |
| 3 | /.env.example with real values | dev left real values | read it |

## Falsifier

Falsifier — every variant returns catch-all/404: no .env exposure.
