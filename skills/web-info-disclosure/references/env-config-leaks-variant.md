# .env / config / credential files — surface variants

Configuration files leak database creds, API keys, JWT secrets, and session keys — the shortest path from disclosure to impact. Probe the standard names, in a bounded list.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| /.env returns KEY=VALUE lines | env file exposed | read keys, chain to session/db |
| /config.json or /config.yml 200 with structured body | config exposed | extract secrets |
| backup variant (.env.bak, .env.old, config.bak) 200 | backup leak | same handling |
| credentials.yml.enc or *.pem | key material | use or note for later |

## Variant-specific traps

- .env often 403s on the dot-file while .env.bak/.env.old read fine — probe variants.
- A JSON parse of the response proves it's real config, not a templated error page.
- Extracted credentials go in field notes, NEVER into the repo or a commit.
- keys may be scoped: an AWS key that reads only one bucket is still a finding.

## Falsifier

Falsifier — every config path returns the catch-all or 404: no conventional config is served. The disclosure may exist under non-standard names — only worth probing if a hint (comment, header, link) names one.

## Cross-references

`git-exposure.md` · `chaining.md` · `backup-archives.md`
