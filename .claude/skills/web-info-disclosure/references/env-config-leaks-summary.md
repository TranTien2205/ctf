# .env / config / credential files — summary

Configuration files leak database creds, API keys, JWT secrets, and session keys — the shortest path from disclosure to impact. Probe the standard names, in a bounded list.

## Signal → route

- /.env returns KEY=VALUE lines → read keys, chain to session/db
- /config.json or /config.yml 200 with structured body → extract secrets
- backup variant (.env.bak, .env.old, config.bak) 200 → same handling
- credentials.yml.enc or *.pem → use or note for later

## Falsifier

Falsifier — every config path returns the catch-all or 404: no conventional config is served. The disclosure may exist under non-standard names — only worth probing if a hint (comment, header, link) names one.
