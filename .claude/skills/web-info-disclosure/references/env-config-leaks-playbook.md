# .env / config / credential files — playbook

Configuration files leak database creds, API keys, JWT secrets, and session keys — the shortest path from disclosure to impact. Probe the standard names, in a bounded list.

## Ordered playbook

1. Probe the bounded list: /.env /.env.bak /config.json /config.yml /settings.py /web.config /appsettings.json.
2. A 200 must carry real content — compare against the catch-all body, not just the status.
3. Extract: DB urls, AWS/SECRET keys, JWT signing keys, admin passwords.
4. Chain each find to its sink: JWT secret → forge session; DB creds → connect or SSRF; admin cred → login.

## Falsifier

Falsifier — every config path returns the catch-all or 404: no conventional config is served. The disclosure may exist under non-standard names — only worth probing if a hint (comment, header, link) names one.

## Commands

```bash
for p in /.env /.env.bak /config.json; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```
