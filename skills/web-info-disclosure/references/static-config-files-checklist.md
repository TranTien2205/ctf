# Static config file exposure — checklist

web.config, .htaccess, nginx.conf served inside the app, robots-style configs: the server's own ruleset as readable text.

## Checklist

- [ ] Probe /web.config /.htaccess /.htpasswd /nginx.conf /conf/ paths.
- [ ] .htpasswd contains crackable password hashes — a credential find.
- [ ] web.config reveals protected paths and the auth scheme.
- [ ] The config IS the route map — every protected path is named.

## Abort conditions

- .htpasswd hashes crack with hashcat -m 1600 (apr1) etc.
- web.config may have protected-paths lists = the hidden route inventory.
- A served .htaccess sometimes exposes the auth realm name.

## Falsifier

Falsifier — no server config file is served: channel closed.
