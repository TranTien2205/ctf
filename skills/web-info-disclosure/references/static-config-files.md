# Static config file exposure

web.config, .htaccess, nginx.conf served inside the app, robots-style configs: the server's own ruleset as readable text.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /web.config 200 | IIS config | rewrite rules, auth rules |
| /.htaccess or /.htpasswd | Apache config/creds | rules + hashed passwords |
| /nginx.conf or site config | server rules | route map |
| /crossdomain.xml already covered | policy | see well-known |

## Steps

1. Probe /web.config /.htaccess /.htpasswd /nginx.conf /conf/ paths.
2. .htpasswd contains crackable password hashes — a credential find.
3. web.config reveals protected paths and the auth scheme.
4. The config IS the route map — every protected path is named.

## Falsifier

Falsifier — no server config file is served: channel closed.

## Traps

- .htpasswd hashes crack with hashcat -m 1600 (apr1) etc.
- web.config may have protected-paths lists = the hidden route inventory.
- A served .htaccess sometimes exposes the auth realm name.

## Commands

```bash
for p in /web.config /.htaccess /.htpasswd /nginx.conf; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`source-disclosure.md` · `env-config-leaks.md`
