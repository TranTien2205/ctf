# .env / config / credential files — case catalogue

Configuration files leak database creds, API keys, JWT secrets, and session keys — the shortest path from disclosure to impact. Probe the standard names, in a bounded list.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /.env returns KEY=VALUE lines | env file exposed | read keys, chain to session/db |
| 2 | /config.json or /config.yml 200 with structured body | config exposed | extract secrets |
| 3 | backup variant (.env.bak, .env.old, config.bak) 200 | backup leak | same handling |
| 4 | credentials.yml.enc or *.pem | key material | use or note for later |

## Falsifier

Falsifier — every config path returns the catch-all or 404: no conventional config is served. The disclosure may exist under non-standard names — only worth probing if a hint (comment, header, link) names one.

## Coverage notes

- .env often 403s on the dot-file while .env.bak/.env.old read fine — probe variants.
- A JSON parse of the response proves it's real config, not a templated error page.
- Extracted credentials go in field notes, NEVER into the repo or a commit.
- keys may be scoped: an AWS key that reads only one bucket is still a finding.

## Cross-references

`git-exposure.md` · `chaining.md` · `backup-archives.md`
