# .env / config / credential files — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.env returns KEY=VALUE lines | env file exposed | read keys, chain to session/db |
| /config.json or /config.yml 200 with structured body | config exposed | extract secrets |
| backup variant (.env.bak, .env.old, config.bak) 200 | backup leak | same handling |
| credentials.yml.enc or *.pem | key material | use or note for later |

## Falsifier

Falsifier — every config path returns the catch-all or 404: no conventional config is served. The disclosure may exist under non-standard names — only worth probing if a hint (comment, header, link) names one.
