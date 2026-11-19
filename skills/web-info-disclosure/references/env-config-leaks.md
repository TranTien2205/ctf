# .env / config / credential files

Configuration files leak database creds, API keys, JWT secrets, and session keys — the shortest path from disclosure to impact. Probe the standard names, in a bounded list.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.env returns KEY=VALUE lines | env file exposed | read keys, chain to session/db |
| /config.json or /config.yml 200 with structured body | config exposed | extract secrets |
| backup variant (.env.bak, .env.old, config.bak) 200 | backup leak | same handling |
| credentials.yml.enc or *.pem | key material | use or note for later |

## Steps

1. Probe the bounded list: /.env /.env.bak /config.json /config.yml /settings.py /web.config /appsettings.json.
2. A 200 must carry real content — compare against the catch-all body, not just the status.
3. Extract: DB urls, AWS/SECRET keys, JWT signing keys, admin passwords.
4. Chain each find to its sink: JWT secret → forge session; DB creds → connect or SSRF; admin cred → login.

## Falsifier

Falsifier — every config path returns the catch-all or 404: no conventional config is served. The disclosure may exist under non-standard names — only worth probing if a hint (comment, header, link) names one.

## Traps

- .env often 403s on the dot-file while .env.bak/.env.old read fine — probe variants.
- A JSON parse of the response proves it's real config, not a templated error page.
- Extracted credentials go in field notes, NEVER into the repo or a commit.
- keys may be scoped: an AWS key that reads only one bucket is still a finding.

## Commands

```bash
for p in /.env /.env.bak /config.json; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`git-exposure.md` · `chaining.md` · `backup-archives.md`
