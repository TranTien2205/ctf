# .env / config / credential files — operational checklist

Configuration files leak database creds, API keys, JWT secrets, and session keys — the shortest path from disclosure to impact. Probe the standard names, in a bounded list.

## Checklist

- [ ] Probe the bounded list: /.env /.env.bak /config.json /config.yml /settings.py /web.config /appsettings.json.
- [ ] A 200 must carry real content — compare against the catch-all body, not just the status.
- [ ] Extract: DB urls, AWS/SECRET keys, JWT signing keys, admin passwords.
- [ ] Chain each find to its sink: JWT secret → forge session; DB creds → connect or SSRF; admin cred → login.

## Abort conditions

- .env often 403s on the dot-file while .env.bak/.env.old read fine — probe variants.
- A JSON parse of the response proves it's real config, not a templated error page.
- Extracted credentials go in field notes, NEVER into the repo or a commit.

## Falsifier

Falsifier — every config path returns the catch-all or 404: no conventional config is served. The disclosure may exist under non-standard names — only worth probing if a hint (comment, header, link) names one.

## Cross-references

`git-exposure.md` · `chaining.md` · `backup-archives.md`
